from uuid import UUID, uuid4

import structlog

from src.application.exceptions import CardNotExistsError
from src.application.interfaces import (
    AbstractUnitOfWork,
)
from src.domain.entities import Card

from .dto import GetCardOutput


class GetCardUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow
        self.logger = structlog.get_logger(__name__)

    async def execute(self, card_id: UUID) -> GetCardOutput:

        async with self.uow:
            try:
                card = await self.uow.cards.get_by_id(card_id=card_id)
                await self.uow.commit()

                if not card:
                    raise CardNotExistsError(card_id=card_id)

                self.logger.debug(
                    "Карточка найдена",
                    front=card.front,
                )
            except CardNotExistsError:
                raise
            except Exception as e:
                # возможные не отловленные ошибки
                self.logger.error("Ошибка при добавлении карточки в БД", error=str(e))
                raise

        return GetCardOutput(
            card_id=str(card.id),
            deck_id=str(card.deck_id),
            front=card.front,
            back=card.back,
        )
