from uuid import UUID, uuid4

import structlog

from src.application.exceptions import DeckNotExistsError
from src.application.interfaces import (
    AbstractUnitOfWork,
)
from src.domain.entities import Card

from .dto import GetCloudCardsInput, GetCloudCardsOutput


class GetCloudCardsUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow
        self.logger = structlog.get_logger(__name__)

    async def execute(self, input_dto: GetCloudCardsInput) -> GetCloudCardsOutput:


        async with self.uow:
            try:

                # получаем список карточек
                cards = await self.uow.cloud_cards.get_by_deck_id(cloud_deck_id=input_dto.deck_id)

            except DeckNotExistsError:
                raise
            except Exception as e:
                self.logger.error("Ошибка при получении карточек", error=str(e))
                raise

        return GetCloudCardsOutput(cards=cards)
