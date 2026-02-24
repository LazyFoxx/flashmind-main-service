from datetime import datetime, time, timedelta, timezone
from uuid import UUID, uuid4

import structlog

from src.application.exceptions import CardAlreadyExistsError, DeckNotExistsError
from src.application.interfaces import (
    AbstractUnitOfWork,
)
from src.domain.entities import Card

from .dto import GetStudyCardsInput, GetStudyCardsOutput


class GetStudyCardsUseCase:
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

    async def execute(self, input_dto: GetStudyCardsInput) -> GetStudyCardsOutput:
        "Получает карточки к повтору сегодня и возвращает их с мета информацией по колоде"

        async with self.uow:
            try:
                # проверяем существование колоды у пользователя
                deck = await self.uow.decks.get_by_id(
                    deck_id=input_dto.deck_id, user_id=input_dto.user_id
                )
                if not deck:
                    raise DeckNotExistsError(
                        deck_id=input_dto.deck_id, user_id=input_dto.user_id
                    )

                # получаем время для сравнения ( 3 ночи следующего дня)
                now = datetime.now(timezone.utc)
                cutoff = await self._get_study_cutoff(now)
                # извлекаем карточки для повторения сегодня
                cards = await self.uow.cards.get_due_cards(
                    input_dto.deck_id, due_before=cutoff
                )

                # получаем статистику по колоде
                deck_stats = await self.uow.decks.get_info(deck_id=input_dto.deck_id)

            except DeckNotExistsError:
                raise
            except Exception as e:
                # возможные не отловленные ошибки
                self.logger.error(
                    "Ошибка при извлечении или обновлении карточек", error=str(e)
                )
                raise

        return GetStudyCardsOutput(
            learning_today=len(cards),
            cards=cards,
            total=deck_stats.get("total_cards") or 0,
            learned=deck_stats.get("learned") or 0,
            in_learning=deck_stats.get("in_learning") or 0,
        )
