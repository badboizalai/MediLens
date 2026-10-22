from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class IdentitySettings(BaseSettings):
    """Keycloak (local) and Cognito (AWS) differ only in these values."""

    model_config = SettingsConfigDict(env_prefix="MEDILENS_OIDC_", extra="ignore")

    issuer: str = "http://localhost:8080/realms/medilens"
    audience: str = "medilens-api"
    # Keycloak: <issuer>/protocol/openid-connect/certs ; Cognito: <issuer>/.well-known/jwks.json
    jwks_url: str = "http://localhost:8080/realms/medilens/protocol/openid-connect/certs"
    algorithms: tuple[str, ...] = ("RS256",)
    roles_claims: tuple[str, ...] = ("realm_access.roles", "cognito:groups", "roles")
    jwks_ttl_seconds: int = 3600
    jwks_min_refresh_seconds: int = 30


@lru_cache
def get_identity_settings() -> IdentitySettings:
    return IdentitySettings()
