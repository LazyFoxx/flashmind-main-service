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

        # если page или per_page не переданы то offset, limit = None
        if input_dto.page is not None and input_dto.per_page is not None:
            offset = (
                (input_dto.page - 1) * input_dto.per_page if input_dto.per_page else 0
            )
            limit = input_dto.per_page
        else:
            offset = None
            limit = None

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
                cards = await self.uow.cards.get_all_light_by_user_and_deck(
                    user_id=input_dto.user_id,
                    deck_id=input_dto.deck_id,
                    offset=offset,
                    limit=limit,
                )

            except DeckNotExistsError:
                raise
            except Exception as e:
                # возможные не отловленные ошибки
                self.logger.error("Ошибка при добавлении карточки в БД", error=str(e))
                raise

        return GetCardsOutput(total=len(cards), cards=cards)
