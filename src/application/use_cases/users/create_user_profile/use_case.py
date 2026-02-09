import structlog

from src.application.exceptions import UserAlreadyExistsError
from src.application.interfaces import (
    AbstractUnitOfWork,
)
from src.application.interfaces import AbstractCloudStorage

from src.domain.entities.user.user import User

from .dto import CreateProfileUserInput, CreateProfileUserOutput


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
        self, input_dto: CreateProfileUserInput
    ) -> CreateProfileUserOutput:
        
        avatar_key = input_dto.avatar_key
        if avatar_key is None:
            # тут будет путь на стандартную аву а пока заглушка
            avatar_key = ''

        
        new_user = User(
            id=input_dto.user_id,
            first_name=input_dto.first_name,
            last_name=input_dto.last_name,
            avatar_key=avatar_key,
            bio=input_dto.bio,
        )

        async with self.uow:
            try:
                # проверяем наличие пользователя в БД 
                existing_user = await self.uow.users.get_by_id(input_dto.user_id)
                if existing_user:
                    # Если уже существует - обновляем.
                    self.logger.warning(
                        "Пользователь с таким  id уже существует", user_id=new_user.id)
                    await self.uow.users.update(new_user)
                    await self.uow.commit()

                    # удаляем прошлую фотографию из хранилища если изменилась
                    old_avatar_key = existing_user.avatar_key
                    if old_avatar_key != new_user.avatar_key:
                        pass
                        # ЛОГИКА УДАЛЕНИЯ
                else:
                    # добавляем нового пользователя
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

            if avatar_key != "": #заглушка
                avatar_url = await self.storage.generate_presigned_url(object_key=input_dto.avatar_key, expires_in=3600*720)

        return CreateProfileUserOutput(
            first_name=new_user.first_name,
            last_name=new_user.last_name,
            avatar_url=avatar_url,
            bio=new_user.bio,
        )
