from uuid import UUID
from datetime import datetime, time, timedelta, timezone

import structlog

from src.application.interfaces import (
    AbstractUnitOfWork,
)

from .dto import GetUserDecksOutput


class GetUserDecksUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow
        self.logger = structlog.get_logger(__name__)
    
    async def _get_study_cutoff(
        self, now: datetime, rollover_hour: int = 3
    ) -> datetime:
        study_day = now.date()
        cutoff = datetime.combine(
            study_day + timedelta(days=1), time(rollover_hour, 0), tzinfo=now.tzinfo
        )
        return cutoff

    async def execute(self, user_id: UUID) -> GetUserDecksOutput:
        async with self.uow:
            decks = await self.uow.decks.list_by_user(user_id=user_id)

            if not decks:
                self.logger.debug("Пользователь пока не добавил колод", user_id=user_id)
                return GetUserDecksOutput(decks=[])

            deck_ids = [deck.id for deck in decks]

            # Получаем общее количество карт по всем колодам
            list_deck_id_and_total_cards = (
                await self.uow.cards.get_total_cards_by_deck_ids(deck_ids=deck_ids)
            )
            
            # Получаем время для сравнения (3 ночи следующего дня)
            now = datetime.now(timezone.utc)
            cutoff = await self._get_study_cutoff(now)
            
            # Получаем количество просроченных карт по всем колодам
            list_deck_id_and_due_cards = (
                await self.uow.cards.get_total_due_cards_by_deck_ids(deck_ids=deck_ids, due_before=cutoff)
            )

            # Исправлено: используем dict() для преобразования списка кортежей в словарь
            cards_count_map = dict(list_deck_id_and_total_cards)
            cards_due_count_map = dict(list_deck_id_and_due_cards)
            
            decks_with_total_cards = []
            for deck in decks:
                total_cards = cards_count_map.get(deck.id, 0)
                due_cards_count = cards_due_count_map.get(deck.id, 0)
                
                updated_deck = deck.with_updated_total_cards(new_total_cards=total_cards)
                updated_deck = updated_deck.with_updated_due_cards_count(new_due_cards_count=due_cards_count)
                
                decks_with_total_cards.append(updated_deck)
            
        self.logger.debug(f"Найдено {len(decks)} колоды", user_id=user_id)

        return GetUserDecksOutput(decks=decks_with_total_cards)
