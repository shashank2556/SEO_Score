"""Application settings loaded from environment / .env."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    database_url: str = "postgresql+asyncpg://seo:seo@localhost:5432/seo_score"
    database_url_sync: str = "postgresql+psycopg2://seo:seo@localhost:5432/seo_score"
    redis_url: str = "redis://localhost:6379/0"
    pagespeed_api_key: str = ""


settings = Settings()
