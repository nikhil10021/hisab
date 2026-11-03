from app.core.base import APIModel


class ErrorResponse(APIModel):
    code: str
    message: str
    details: list[dict[str, str]] | dict[str, str]


class AppError(Exception):
    def __init__(
        self,
        *,
        code: str,
        message: str,
        details: list[dict[str, str]] | dict[str, str] | None = None,
        status_code: int = 400,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details if details is not None else []
        self.status_code = status_code
