import structlog

from src.application.exceptions import UserNotFoundError
from src.application.interfaces import (
    AbstractCloudStorage,
    AbstractUnitOfWork,
)

from .dto import GetProfileUserInput, GetProfileUserOutput


class GetUserProfileUseCase:
    def __init__(self, uow: AbstractUnitOfWork, storage: AbstractCloudStorage):
        self.uow = uow
        self.logger = structlog.get_logger(__name__)
        self.storage = storage
    
    def _is_full_url(self, path_or_key: str) -> bool:
        """
        Проверяет, является ли строка полной ссылкой (URL) или относительным ключом.
        """
        if not path_or_key:
            return False
        return path_or_key.startswith(("http://", "https://"))

    async def execute(self, input_dto: GetProfileUserInput) -> GetProfileUserOutput:
        async with self.uow:
            user = await self.uow.users.get_by_id(input_dto.user_id)

        if user is None:
            self.logger.warning(
                "Пользователь не найден", user_id=input_dto.user_id, exc_info=True
            )
            raise UserNotFoundError(user_id=str(input_dto.user_id))

        self.logger.debug("Получил профиль пользователя из БД", user_id=str(user.id)[:8])

        if not user.avatar_key:
            avatar_url = ""
        else:
            if self._is_full_url(user.avatar_key):
                avatar_url = user.avatar_key
            else:
                avatar_url = await self.storage.generate_presigned_url(
                    object_key=user.avatar_key, expires_in=3600 * 720
                )

        return GetProfileUserOutput(
            user_id=input_dto.user_id,
            first_name=user.first_name,
            last_name=user.last_name,
            avatar_url=avatar_url,
            bio=user.bio,
        )
