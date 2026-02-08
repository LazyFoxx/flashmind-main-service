import structlog

from src.application.exceptions import UserNotFoundError
from src.application.interfaces import (
    AbstractUnitOfWork,
)

from .dto import GetProfileUserInput, GetProfileUserOutput


class GetUserProfileUseCase:
    def __init__(
        self,
        uow: AbstractUnitOfWork,
    ):
        self.uow = uow
        self.logger = structlog.get_logger(__name__)

    async def execute(self, input_dto: GetProfileUserInput) -> GetProfileUserOutput:
        async with self.uow:
            user = await self.uow.users.get_by_id(input_dto.user_id)

        if user is None:
            self.logger.warning(
                "Пользователь не найден", user_id=input_dto.user_id, exc_info=True
            )
            raise UserNotFoundError()

        self.logger.info("Получил профиль пользователя из БД", user_id=str(user.id)[:8])

        return GetProfileUserOutput(
            first_name=user.first_name,
            last_name=user.last_name,
            avatar_url=user.avatar_url,
            bio=user.bio,
        )
