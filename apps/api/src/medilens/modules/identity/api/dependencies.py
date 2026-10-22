from collections.abc import Callable
from functools import lru_cache
from typing import Annotated

from fastapi import Depends, Request

from medilens.core.errors import AppError, Forbidden
from medilens.modules.identity.application.token_validator import TokenValidator, ValidatorConfig
from medilens.modules.identity.domain.principal import InvalidToken, Principal
from medilens.modules.identity.infra.jwks import CachedJwks
from medilens.modules.identity.infra.settings import get_identity_settings


class Unauthenticated(AppError):
    status = 401
    code = "MEDILENS-401"


@lru_cache
def get_token_validator() -> TokenValidator:
    s = get_identity_settings()
    jwks = CachedJwks(s.jwks_url, ttl=s.jwks_ttl_seconds, min_refresh=s.jwks_min_refresh_seconds)
    cfg = ValidatorConfig(
        issuer=s.issuer, audience=s.audience, algorithms=s.algorithms, roles_claims=s.roles_claims
    )
    return TokenValidator(cfg, jwks.get_key)


def get_current_user(
    request: Request, validator: Annotated[TokenValidator, Depends(get_token_validator)]
) -> Principal:
    scheme, _, token = request.headers.get("authorization", "").partition(" ")
    if scheme.lower() != "bearer" or not token.strip():
        raise Unauthenticated("Missing bearer token")
    try:
        return validator.validate(token.strip())
    except InvalidToken:
        raise Unauthenticated("Invalid or expired token") from None


def require_role(*roles: str) -> Callable[[Principal], Principal]:
    def dependency(user: Annotated[Principal, Depends(get_current_user)]) -> Principal:
        if not user.has_role(*roles):
            raise Forbidden("Insufficient role")
        return user

    return dependency
