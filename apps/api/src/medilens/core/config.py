from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    env: str = "local"
    log_level: str = "INFO"
    database_url: str = "postgresql+psycopg://medilens:medilens_dev@localhost:5432/medilens"
    redis_url: str = "redis://localhost:6379/0"
    oidc_issuer: str = ""
    oidc_audience: str = "medilens-api"


@lru_cache
def get_settings() -> Settings:
    return Settings()
