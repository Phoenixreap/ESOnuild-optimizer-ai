from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings.

    Environment variables override defaults. For development, SQLite is used by default.
    """

    database_url: str = "sqlite:////workspace/omnilink-backend/omnilink.db"
    platform_fee_percent: float = 2.0
    jwt_secret: str = "change-me-in-env"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

