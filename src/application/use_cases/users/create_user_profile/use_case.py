import structlog

from src.application.exceptions import UserAlreadyExistsError
from src.application.interfaces import (
    AbstractUnitOfWork,
)
from src.domain.entities.user.user import User

from .dto import CreateProfileUserInput, CreateProfileUserOutput


class CreateUserProfileUseCase:
    def __init__(
        self,
        uow: AbstractUnitOfWork,
    ):
        self.uow = uow
        self.logger = structlog.get_logger(__name__)

    async def execute(
        self, input_dto: CreateProfileUserInput
    ) -> CreateProfileUserOutput:
        new_user = User(
            id=input_dto.user_id,
            first_name=input_dto.first_name,
            last_name=input_dto.last_name,
            avatar_url=input_dto.avatar_url,
            bio=input_dto.bio,
        )

        async with self.uow:
            existing_user = await self.uow.users.get_by_id(input_dto.user_id)
            if existing_user:
                self.logger.error(
                    "Пользователь с таким  id уже существует", user_id=new_user.id
                )
                raise UserAlreadyExistsError(
                    f"Пользователь с id {input_dto.user_id} уже существует."
                )

            try:
                await self.uow.users.add(user=new_user)
                await self.uow.commit()
                self.logger.info(
                    "Профиль пользователя добавлен в БД", user_id=new_user.id
                )
            except Exception as e:
                self.logger.error(
                    "Ошибка при добавлении профиля пользователя в БД", error=str(e)
                )
                raise

        return CreateProfileUserOutput(
            first_name=new_user.first_name,
            last_name=new_user.last_name,
            avatar_url=new_user.avatar_url,
            bio=new_user.bio,
        )
