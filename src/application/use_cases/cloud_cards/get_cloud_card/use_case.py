from uuid import UUID, uuid4

import structlog

from src.application.exceptions import CardNotExistsError
from src.application.interfaces import (
    AbstractUnitOfWork,
)

from .dto import GetCloudCardOutput


class GetCloudCardUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow
        self.logger = structlog.get_logger(__name__)

    async def execute(self, card_id: UUID) -> GetCloudCardOutput:

        async with self.uow:
            try:
                card = await self.uow.cloud_cards.get_by_id(card_id=card_id)
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
                self.logger.error("Ошибка при получении карточки", error=str(e))
                raise

        return GetCloudCardOutput(
            card_id=str(card.id),
            front=card.front,
            back=card.back,
        )
