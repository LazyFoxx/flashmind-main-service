from uuid import UUID, uuid4

import structlog

from src.application.exceptions import DeckNotExistsError
from src.application.interfaces import (
    AbstractUnitOfWork,
)
from src.domain.entities import Card

from .dto import GetCardsInput, GetCardsOutput


class GetCardsUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow
        self.logger = structlog.get_logger(__name__)

    async def execute(self, input_dto: GetCardsInput) -> GetCardsOutput:

        async with self.uow:
            try:
                # проверяем наличие колоды
                if input_dto.deck_id:
                    deck = await self.uow.decks.get_by_id(input_dto.deck_id)
                    if not deck or deck.user_id != input_dto.user_id:
                        raise DeckNotExistsError(
                            deck_id=input_dto.deck_id, user_id=input_dto.user_id
                        )

                # получаем список карточек
                cards = await self.uow.cards.get_by_deck_id(
                    deck_id=input_dto.deck_id,
                )

            except DeckNotExistsError:
                raise
            except Exception as e:
                self.logger.error("Ошибка при получении карточек", error=str(e))
                raise

        return GetCardsOutput(cards=cards)
