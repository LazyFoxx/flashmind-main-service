from uuid import UUID, uuid4

import structlog

from src.application.exceptions import DeckAlreadyExistsError
from src.application.interfaces import (
    AbstractUnitOfWork,
)
from src.domain.entities import Deck

from .dto import DeleteDeckInput


class DeleteDeckUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow
        self.logger = structlog.get_logger(__name__)

    async def execute(self, input_dto: DeleteDeckInput) -> None:

        async with self.uow:
            try:

                # проверяем существование колоды, обеспечиваем иденпотентность
                deck = await self.uow.decks.get_by_id(input_dto.deck_id)
                if not deck:
                    return None

                await self.uow.decks.delete(
                    deck_id=input_dto.deck_id, user_id=input_dto.user_id
                )

                await self.uow.commit()
                self.logger.info(
                    "Колода успешно удалена",
                    deck_id=input_dto.deck_id,
                    user_id=input_dto.user_id,
                )
            except Exception as e:
                # возможные не отловленные ошибки
                self.logger.error("Ошибка при удалении колоды", error=str(e))
                raise

        return None
