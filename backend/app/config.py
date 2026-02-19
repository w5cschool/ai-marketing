from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Email Marketing API"
    app_env: str = "local"
    api_v1_prefix: str = "/api/v1"
    debug: bool = False

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/ai_email_marketing"

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    resend_api_key: str = ""
    resend_from_email: str = "team@example.com"
    resend_webhook_secret: str = ""
    youtube_api_key: str = ""

    allow_origins: str = "http://localhost:3000"
    default_send_rate_limit: int = 60
    daily_send_limit: int = Field(default=500, ge=1)

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
