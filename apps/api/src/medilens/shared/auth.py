"""Cross-cutting authentication: the authenticated Principal and FastAPI dependencies.

Token validation lives in the identity module, which registers itself via
`register_token_validator`; shared never imports modules.
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Annotated, Protocol

from fastapi import Depends, Request

from medilens.core.errors import Forbidden, Unauthorized


@dataclass(frozen=True)
class Principal:
    sub: str
    roles: frozenset[str] = frozenset()

    def has_role(self, *roles: str) -> bool:
        return bool(self.roles.intersection(roles))


class InvalidToken(Exception):
    """Token missing, malformed, expired, or failing signature/iss/aud checks."""


class TokenVerifier(Protocol):
    def validate(self, token: str) -> Principal: ...


_factory: Callable[[], TokenVerifier] | None = None


def register_token_validator(factory: Callable[[], TokenVerifier]) -> None:
    global _factory
    _factory = factory


def get_token_validator() -> TokenVerifier:
    if _factory is None:
        raise RuntimeError("no token validator registered")
    return _factory()


def get_current_user(
    request: Request, validator: Annotated[TokenVerifier, Depends(get_token_validator)]
) -> Principal:
    scheme, _, token = request.headers.get("authorization", "").partition(" ")
    if scheme.lower() != "bearer" or not token.strip():
        raise Unauthorized("Missing bearer token")
    try:
        return validator.validate(token.strip())
    except InvalidToken:
        raise Unauthorized("Invalid or expired token", invalid_token=True) from None


def require_role(*roles: str) -> Callable[[Principal], Principal]:
    def dependency(user: Annotated[Principal, Depends(get_current_user)]) -> Principal:
        if not user.has_role(*roles):
            raise Forbidden("Insufficient role")
        return user

    return dependency
