from uuid import UUID
import structlog

from src.application.exceptions import UserAlreadyExistsError
from src.application.interfaces import (
    AbstractUnitOfWork,
)
from src.application.interfaces import AbstractCloudStorage

from src.domain.entities.user.user import User


class CreateUserProfileUseCase:
    def __init__(
        self,
        uow: AbstractUnitOfWork,
        storage: AbstractCloudStorage
    ):
        self.uow = uow
        self.logger = structlog.get_logger(__name__)
        self.storage = storage

    async def execute(
        self, user_id
    ) -> None:

        new_user = User(
            id=UUID(user_id),
            first_name="",
            last_name="",
            avatar_key="",
            bio="",
        )

        async with self.uow:
            try:
                # проверяем наличие пользователя в БД 
                existing_user = await self.uow.users.get_by_id(user_id)
                if existing_user:
                    # Если уже существует - обновляем.
                    self.logger.error(
                        "Пользователь с таким  id уже существует", user_id=new_user.id)
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