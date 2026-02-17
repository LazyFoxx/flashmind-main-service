from uuid import UUID

import structlog

from src.application.interfaces import (
    AbstractUnitOfWork,
)

from .dto import GetUserDecksOutput


class GetUserDecksUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow
        self.logger = structlog.get_logger(__name__)

    async def execute(self, user_id: UUID) -> GetUserDecksOutput:
        async with self.uow:
            decks = await self.uow.decks.list_by_user(user_id=user_id)

        if not decks:
            self.logger.debug("Пользователь пока не добавил колод", user_id=user_id)
        self.logger.debug(f"Найдено {len(decks)} колоды", user_id=user_id)

        return GetUserDecksOutput(decks=decks)
