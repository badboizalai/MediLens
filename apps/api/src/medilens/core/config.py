from functools import lru_cache
from typing import Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

Env = Literal["local", "dev", "staging", "prod"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    env: Env = "local"
    log_level: str = "INFO"
    database_url: str = "postgresql+psycopg://medilens:medilens_dev@localhost:5432/medilens"
    redis_url: str = "redis://localhost:6379/0"
    oidc_issuer: str = ""
    oidc_audience: str = "medilens-api"
    cors_origins: list[str] = ["http://localhost:3000"]
    knowledge_allow_drafts: bool = False  # BR-024/BR-051: only CSO-reviewed articles in prod

    @model_validator(mode="after")
    def _prod_is_strict(self) -> "Settings":
        if "*" in self.cors_origins:
            raise ValueError("wildcard CORS origin is not allowed; list explicit origins")
        return self

    @property
    def docs_enabled(self) -> bool:
        return self.env != "prod"

    @property
    def json_logs(self) -> bool:
        return self.env != "local"


@lru_cache
def get_settings() -> Settings:
    return Settings()
