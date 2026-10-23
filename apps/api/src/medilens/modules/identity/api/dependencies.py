from functools import lru_cache

from medilens.modules.identity.application.token_validator import TokenValidator, ValidatorConfig
from medilens.modules.identity.infra.jwks import CachedJwks
from medilens.modules.identity.infra.settings import get_identity_settings


@lru_cache
def get_token_validator() -> TokenValidator:
    s = get_identity_settings()
    jwks = CachedJwks(s.jwks_url, ttl=s.jwks_ttl_seconds, min_refresh=s.jwks_min_refresh_seconds)
    cfg = ValidatorConfig(
        issuer=s.issuer, audience=s.audience, algorithms=s.algorithms, roles_claims=s.roles_claims
    )
    return TokenValidator(cfg, jwks.get_key)
