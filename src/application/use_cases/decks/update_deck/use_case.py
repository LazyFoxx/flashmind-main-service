from uuid import UUID, uuid4

import structlog

from src.application.exceptions import DeckAlreadyExistsError, DeckNotExistsError
from src.application.interfaces import (
    AbstractUnitOfWork,
)
from datetime import datetime, time, timedelta, timezone
from src.domain.entities import Deck

from .dto import UpdateDeckInput, UpdateDeckOutput


class UpdateDeckUseCase:
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

    async def execute(self, input_dto: UpdateDeckInput) -> UpdateDeckOutput:
        
        async with self.uow:
            try:
                
                deck_ids = [input_dto.deck_id]

                 # Получаем общее количество карт по всем колонам
                list_deck_id_and_total_cards = (
                    await self.uow.cards.get_total_cards_by_deck_ids(deck_ids=deck_ids)
                  )
                
                 # Получаем время для сравнения (3 ночи следующего дня)
                now = datetime.now(timezone.utc)
                cutoff = await self._get_study_cutoff(now)
                
                 # Получаем количество просроченных карт по всем колонам
                list_deck_id_and_due_cards = (
                    await self.uow.cards.get_total_due_cards_by_deck_ids(deck_ids=deck_ids, due_before=cutoff)
                  )
                
                 # Получаем существующую колоду с проверкой по user_id
                deck = await self.uow.decks.get_by_id(input_dto.deck_id, user_id=input_dto.user_id)
                
                if deck is None:
                    raise DeckNotExistsError(
                        deck_id=input_dto.deck_id, user_id=input_dto.user_id
                    )

                 # Вычисляем новые значения total_cards и due_cards_count
                total_cards = list_deck_id_and_total_cards[0][1] if list_deck_id_and_total_cards else 0
                due_cards_count = list_deck_id_and_due_cards[0][1] if list_deck_id_and_due_cards else 0
                
                 # Используем _copy() для обновления только изменяемых полей,
                 # сохраняя все облачные параметры без изменений
                updated_deck = deck._copy(
                    name=input_dto.name,
                    description=input_dto.description,
                    desired_retention=input_dto.desired_retention,
                    maximum_interval=input_dto.maximum_interval,
                    color=input_dto.color,
                    total_cards=total_cards,
                    due_cards_count=due_cards_count,
                 )

                await self.uow.decks.update(updated_deck)
                await self.uow.commit()
                self.logger.info(
                      "Колода успешно обновлена",
                    deck_name=updated_deck.name,
                    user_id=updated_deck.user_id,
                 )
            except Exception as e:
                  # возможные не отловленные ошибки
                self.logger.error("Ошибка при обновлении колоды", error=str(e))
                raise

        return UpdateDeckOutput(
            deck=updated_deck
         )
