from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from medilens.modules.identity.api import (
    dependencies,  # noqa: F401  (registers the token validator)
)
from medilens.shared.auth import Principal, get_current_user

router = APIRouter(tags=["identity"])


class MeOut(BaseModel):
    sub: str
    roles: list[str]


@router.get("/me", response_model=MeOut)
def me(user: Annotated[Principal, Depends(get_current_user)]) -> MeOut:
    return MeOut(sub=user.sub, roles=sorted(user.roles))
