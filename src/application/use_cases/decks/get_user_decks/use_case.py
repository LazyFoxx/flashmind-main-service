from uuid import UUID
from datetime import datetime, time, timedelta, timezone

import structlog

from src.application.exceptions import UserNotFoundError
from src.application.interfaces import (
    AbstractUnitOfWork,
)

from src.application.use_cases.common.utils import get_current_datetime, get_study_cutoff
from .dto import GetUserDecksOutput, GetUserDecksInput


class GetUserDecksUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow
        self.logger = structlog.get_logger(__name__)
    
    
    async def execute(self, input_dto: GetUserDecksInput)  -> GetUserDecksOutput:
        async with self.uow:
            decks = await self.uow.decks.list_by_user(user_id=input_dto.user_id)

            if not decks:
                self.logger.debug("Пользователь пока не добавил колод", user_id=input_dto.user_id)
                return GetUserDecksOutput(decks=[])

            deck_ids = [deck.id for deck in decks]

            # Получаем общее количество карт по всем колодам
            list_deck_id_and_total_cards = (
                await self.uow.cards.get_total_cards_by_deck_ids(deck_ids=deck_ids)
            )
            
            user = await self.uow.users.get_by_id(input_dto.user_id)
            if user is None:
                self.logger.warning(
                        "Пользователь не найден",
                    user_id=input_dto.user_id,
                    )
                raise UserNotFoundError(user_id=str(input_dto.user_id))
            
            # Синхронизация timezone: если timezone из DTO отличается от пользовательского — обновляем
            if user.timezone != input_dto.timezone:
                old_tz = user.timezone  # <-- Сохраняем старое значение
                user = user.with_timezone(input_dto.timezone)
                await self.uow.users.update(user)
                self.logger.info(
                    "Пользовательская таймзона обновлена",
                    user_id=input_dto.user_id,
                    old_timezone=old_tz,
                    new_timezone=input_dto.timezone,
                )
            
            # Получаем время для сравнения 
            now = get_current_datetime(user.timezone)
            cutoff = get_study_cutoff(now)
            
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
                
                cloud_updated_at = await self.uow.cloud_decks.get_last_synced_at(cloud_deck_id=updated_deck.cloud_deck_id)
                
                if cloud_updated_at:
                    updated_deck = updated_deck.with_needs_sync(cloud_updated_at=cloud_updated_at)
                
                decks_with_total_cards.append(updated_deck)
                
                
            
        # self.logger.debug(f"Найдено {len(decks)} колоды", user_id=input_dto.user_id)

        return GetUserDecksOutput(decks=decks_with_total_cards)
