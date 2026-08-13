from uuid import UUID

import structlog

from src.application.interfaces import (
    AbstractCloudStorage,
    AbstractUnitOfWork,
)
from src.domain.entities.user.user import User
from .dto import CreateUserProfileInput

class CreateUserProfileUseCase:
    def __init__(self, uow: AbstractUnitOfWork, storage: AbstractCloudStorage):
        self.uow = uow
        self.logger = structlog.get_logger(__name__)
        self.storage = storage
    

    async def execute(self, input_dto: CreateUserProfileInput) -> None:
        new_user = User(
            id=input_dto.user_id,
            first_name=input_dto.name if input_dto.name else "",
            last_name="",
            avatar_key=input_dto.avatar_url if input_dto.avatar_url else "",
            bio="",
        )

        async with self.uow:
            try:
                # проверяем наличие пользователя в БД
                existing_user = await self.uow.users.get_by_id(new_user.id)
                if existing_user:
                    # Если уже существует - обновляем.
                    self.logger.error(
                        "Пользователь с таким  id уже существует", user_id=new_user.id
                    )
                    raise Exception

                # добавляем нового пользователя
                await self.uow.users.add(user=new_user)
                await self.uow.commit()
                self.logger.info(
                    "Профиль пользователя создан и добавлен в БД", user_id=new_user.id
                )
            except Exception as e:
                self.logger.error(
                    "Ошибка при добавлении профиля пользователя в БД", error=str(e)
                )
                raise
