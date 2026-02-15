import dataclasses

import structlog

from src.application.exceptions import UserNotFoundError
from src.application.interfaces import (
    AbstractCloudStorage,
    AbstractUnitOfWork,
)

from .dto import UpdateProfileUserInput, UpdateProfileUserOutput


class UpdateUserProfileUseCase:
    def __init__(self, uow: AbstractUnitOfWork, storage: AbstractCloudStorage):
        self.uow = uow
        self.logger = structlog.get_logger(__name__)
        self.storage = storage

    async def execute(
        self, input_dto: UpdateProfileUserInput
    ) -> UpdateProfileUserOutput:
        self.logger.debug("Старт обновления полей профиля", user_id=input_dto.user_id)
        async with self.uow:
            try:
                # проверяем наличие пользователя в БД
                existing_user = await self.uow.users.get_by_id(input_dto.user_id)
                if not existing_user:
                    self.logger.error(
                        "Пользователь не найден", user_id=input_dto.user_id
                    )
                    raise UserNotFoundError(
                        f"Пользователь {input_dto.user_id} не найден"
                    )

                updates = {}
                if (
                    input_dto.first_name is not None
                ):  # Проверяем на None, чтобы не перезаписывать пустыми
                    updates["first_name"] = input_dto.first_name
                if input_dto.last_name is not None:
                    updates["last_name"] = input_dto.last_name
                if input_dto.bio is not None:
                    updates["bio"] = input_dto.bio

                if input_dto.avatar_file:
                    new_avatar_key = await self.storage.put_avatar(
                        str(input_dto.user_id),
                        category="avatar",
                        file=input_dto.avatar_file,
                    )
                    old_key = existing_user.avatar_key
                    if old_key:
                        await self.storage.delete_object(
                            object_key=old_key, user_id=existing_user.id
                        )
                    updates["avatar_key"] = new_avatar_key

                updated_user = dataclasses.replace(existing_user, **updates)  # type: ignore
                await self.uow.users.update(user=updated_user)
                await self.uow.commit()
                self.logger.info(
                    "Профиль пользователя успешно обнавлен в БД",
                    user_id=updated_user.id,
                )

                existing_user = (
                    updated_user  # Перезапишем для дальнейшего использования
                )

            except Exception as e:
                await self.uow.rollback()
                self.logger.error(
                    "Ошибка при добавлении профиля пользователя в БД", error=str(e)
                )
                raise

        if existing_user.avatar_key:
            avatar_url = await self.storage.generate_presigned_url(
                existing_user.avatar_key, expires_in=3600
            )

        return UpdateProfileUserOutput(
            first_name=existing_user.first_name,
            last_name=existing_user.last_name,
            avatar_url=avatar_url,
            bio=existing_user.bio,
        )
