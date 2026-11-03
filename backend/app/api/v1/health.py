from fastapi import APIRouter, Request

from app.api.v1.calculators import limiter

router = APIRouter()


@router.get("/health")
@limiter.limit("60/minute")
def health(request: Request) -> dict[str, str]:
    return {"status": "ok"}
