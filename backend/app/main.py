import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.requests import Request
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.api.v1.calculators import limiter
from app.api.v1.calculators import router as calculators_router
from app.api.v1.health import router as health_router
from app.core.errors import AppError, ErrorResponse
from app.core.registry import discover_calculators
from app.core.settings import Settings, get_settings

logger = logging.getLogger(__name__)


class RequestSizeLimitMiddleware:
    def __init__(
        self,
        app: ASGIApp,
        *,
        max_request_size_bytes: int,
    ) -> None:
        self.app = app
        self.max_request_size_bytes = max_request_size_bytes

    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        content_length = next(
            (
                value
                for key, value in scope.get("headers", [])
                if key.lower() == b"content-length"
            ),
            None,
        )
        if content_length is not None:
            try:
                declared_size = int(content_length)
            except ValueError:
                await self._send_error(scope, receive, send, 400)
                return
            if declared_size > self.max_request_size_bytes:
                await self._send_error(scope, receive, send, 413)
                return

        chunks: list[bytes] = []
        request_size = 0
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            request_chunk = message.get("body", b"")
            request_size += len(request_chunk)
            if request_size > self.max_request_size_bytes:
                await self._send_error(scope, receive, send, 413)
                return
            chunks.append(request_chunk)
            if not message.get("more_body", False):
                break

        request_body = b"".join(chunks)
        body_sent = False

        async def receive_buffered() -> Message:
            nonlocal body_sent
            if not body_sent:
                body_sent = True
                return {
                    "type": "http.request",
                    "body": request_body,
                    "more_body": False,
                }
            return {"type": "http.disconnect"}

        await self.app(scope, receive_buffered, send)

    async def _send_error(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
        status_code: int,
    ) -> None:
        if status_code == 413:
            error = ErrorResponse(
                code="REQUEST_TOO_LARGE",
                message="The request body exceeds the allowed size.",
                details=[],
            )
        else:
            error = ErrorResponse(
                code="INVALID_CONTENT_LENGTH",
                message="The request has an invalid Content-Length header.",
                details=[],
            )
        response = JSONResponse(
            status_code=status_code,
            content=error.model_dump(mode="json", by_alias=True),
        )
        await response(scope, receive, send)


def create_app(
    settings: Settings | None = None,
    *,
    calculator_package: str = "app.calculators",
) -> FastAPI:
    active_settings = settings or get_settings()

    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncGenerator[None, None]:
        application.state.calculators = discover_calculators(calculator_package)
        yield

    is_production = active_settings.environment == "prod"
    application = FastAPI(
        title="Hisab API",
        docs_url=None if is_production else "/docs",
        redoc_url=None if is_production else "/redoc",
        openapi_url=None if is_production else "/openapi.json",
        lifespan=lifespan,
    )
    application.state.settings = active_settings
    application.state.limiter = limiter
    application.add_exception_handler(AppError, handle_app_error)
    application.add_exception_handler(
        RequestValidationError,
        handle_request_validation_error,
    )
    application.add_exception_handler(
        StarletteHTTPException,
        handle_http_error,
    )
    application.add_exception_handler(RateLimitExceeded, handle_rate_limit)
    application.add_exception_handler(Exception, handle_unexpected_error)
    application.add_middleware(
        RequestSizeLimitMiddleware,
        max_request_size_bytes=active_settings.max_request_size_bytes,
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=active_settings.cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )
    application.include_router(health_router, prefix="/api/v1")
    application.include_router(calculators_router, prefix="/api/v1")
    return application


def _error_response(
    *,
    code: str,
    message: str,
    details: list[dict[str, str]] | dict[str, str],
    status_code: int,
) -> JSONResponse:
    payload = ErrorResponse(
        code=code,
        message=message,
        details=details,
    ).model_dump(mode="json", by_alias=True)
    return JSONResponse(status_code=status_code, content=payload)


async def handle_app_error(
    request: Request,
    error: Exception,
) -> JSONResponse:
    if not isinstance(error, AppError):
        raise error
    return _error_response(
        code=error.code,
        message=error.message,
        details=error.details,
        status_code=error.status_code,
    )


async def handle_request_validation_error(
    request: Request,
    error: Exception,
) -> JSONResponse:
    if not isinstance(error, RequestValidationError):
        raise error
    details = [
        {
            "field": ".".join(str(part) for part in item["loc"]),
            "message": "Please provide a valid request.",
        }
        for item in error.errors()
    ]
    return _error_response(
        code="VALIDATION_ERROR",
        message="Please check your request and try again.",
        details=details,
        status_code=422,
    )


async def handle_http_error(
    request: Request,
    error: Exception,
) -> JSONResponse:
    if not isinstance(error, StarletteHTTPException):
        raise error
    if error.status_code == 404:
        code = "NOT_FOUND"
        message = "The requested resource was not found."
    elif error.status_code == 405:
        code = "METHOD_NOT_ALLOWED"
        message = "This method is not allowed for the requested resource."
    else:
        code = "HTTP_ERROR"
        message = "The request could not be completed."
    return _error_response(
        code=code,
        message=message,
        details=[],
        status_code=error.status_code,
    )


async def handle_rate_limit(
    request: Request,
    error: Exception,
) -> JSONResponse:
    if not isinstance(error, RateLimitExceeded):
        raise error
    return _error_response(
        code="RATE_LIMIT_EXCEEDED",
        message="Too many requests. Please try again shortly.",
        details=[],
        status_code=429,
    )


async def handle_unexpected_error(
    request: Request,
    error: Exception,
) -> JSONResponse:
    logger.error(
        "Unhandled API error",
        exc_info=(type(error), error, error.__traceback__),
    )
    return _error_response(
        code="INTERNAL_ERROR",
        message="Something went wrong. Please try again later.",
        details=[],
        status_code=500,
    )


app = create_app()
