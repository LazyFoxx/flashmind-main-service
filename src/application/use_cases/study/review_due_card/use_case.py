from datetime import datetime, time, timedelta, timezone
from uuid import UUID, uuid4

import structlog
from fsrs import Card, Rating, ReviewLog, Scheduler, State

from src.application.exceptions import (
    CardNotExistsError,
    CardNotInLearningError,
    DeckNotExistsError,
)
from src.application.interfaces import (
    AbstractUnitOfWork,
)
from src.domain.entities import Card

from .dto import ReviewDueCardInput


class ReviewDueCardsUseCase:
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

    async def execute(self, input_dto: ReviewDueCardInput) -> Card | None:
        "Логика повторения просроченной карточки"

        async with self.uow:
            try:

                # получаем карточку из базы данных
                card = await self.uow.cards.get_by_id(input_dto.card_id)

                if card is None:
                    raise CardNotExistsError(card_id=input_dto.card_id)

                if not card.in_learning:
                    raise CardNotInLearningError(card_id=card.id)

                if input_dto.rating == 1:
                    rating = Rating.Again
                elif input_dto.rating == 2:
                    rating = Rating.Hard
                elif input_dto.rating == 3:
                    rating = Rating.Good
                elif input_dto.rating == 4:
                    rating = Rating.Easy
                else:
                    raise ValueError

                scheduler = Scheduler(
                    desired_retention=0.95,  # Стремиться к 95% шанса вспоминания
                    learning_steps=(
                        timedelta(minutes=1),
                        timedelta(minutes=10),
                    ),  # Короткие начальные интервалы для обучения
                    relearning_steps=(
                        timedelta(minutes=10),
                    ),  # Интервалы после забывания
                    maximum_interval=36500,  # Макс. ~100 лет
                    enable_fuzzing=True,  # Добавлять случайный fuzz к интервалам, чтобы избежать скоплений
                )

                card, review_log = card.review(scheduler=scheduler, rating=rating)

                await self.uow.cards.update(card)
                await self.uow.commit()

                now = datetime.now(timezone.utc)
                cutoff = await self._get_study_cutoff(now)

                flag_due_today = card.is_due(cutoff)

                if flag_due_today:
                    return card
                else:
                    return None

            except CardNotExistsError:
                raise
            except CardNotInLearningError:
                raise
            except Exception as e:
                # возможные не отловленные ошибки
                self.logger.error(
                    "Ошибка при извлечении или обновлении карточек", error=str(e)
                )
                raise
