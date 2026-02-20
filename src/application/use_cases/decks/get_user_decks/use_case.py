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

            deck_ids = [deck.id for deck in decks]

            list_deck_id_and_total_cards = (
                await self.uow.cards.get_total_cards_by_deck_ids(deck_ids=deck_ids)
            )
            decks_with_total_cards = []
            for deck in decks:
                for deck_id, total_cards in list_deck_id_and_total_cards:
                    if deck_id == deck.id:
                        updated_deck = deck.with_updated_total_cards(
                            new_total_cards=total_cards
                        )
                        decks_with_total_cards.append(updated_deck)
                        break

        if not decks:
            self.logger.debug("Пользователь пока не добавил колод", user_id=user_id)
        self.logger.debug(f"Найдено {len(decks)} колоды", user_id=user_id)

        return GetUserDecksOutput(decks=decks_with_total_cards)
