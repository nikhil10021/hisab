from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=".env",
        extra="ignore",
        populate_by_name=True,
    )

    environment: Literal["dev", "prod"] = Field(
        default="dev",
        validation_alias="ENVIRONMENT",
    )
    allowed_origins: str = Field(
        default="http://localhost:5173",
        validation_alias="CORS_ORIGINS",
    )
    max_request_size_bytes: int = Field(
        default=1_048_576,
        gt=0,
        validation_alias="MAX_REQUEST_SIZE_BYTES",
    )
    metadata_cache_seconds: int = Field(
        default=300,
        ge=0,
        validation_alias="METADATA_CACHE_SECONDS",
    )

    @property
    def cors_origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.allowed_origins.split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()
