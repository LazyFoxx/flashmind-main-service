from typing import Annotated
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.application.exceptions import InvalidTokenError
from src.application.interfaces.unit_of_work import AbstractUnitOfWork
from src.domain.entities import User
from src.infrastructure.auth.auth_service import AuthService

bearer_scheme = HTTPBearer(auto_error=False)


@inject
async def get_current_user(
    auth: FromDishka[AuthService],
    uow: FromDishka[AbstractUnitOfWork],
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme),
    ],
) -> User:
    if not credentials:
        raise InvalidTokenError

    user_id: UUID = await auth.decode_token(credentials.credentials)

    async with uow:
        user: User = await uow.users.get_by_id(user_id)

    if not user:
        raise InvalidTokenError

    return user


@inject
async def get_current_user_id(
    auth: FromDishka[AuthService],
    uow: FromDishka[AbstractUnitOfWork],
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme),
    ],
) -> UUID:
    if not credentials:
        raise InvalidTokenError
    user_id: UUID = await auth.decode_token(credentials.credentials)
    return user_id
