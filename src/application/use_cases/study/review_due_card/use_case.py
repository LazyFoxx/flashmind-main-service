from datetime import datetime, time, timedelta, timezone
from uuid import UUID, uuid4

import structlog
from fsrs import Rating, Scheduler, State

from src.application.exceptions import (
    CardNotExistsError,
    CardNotInLearningError,
)
from src.application.interfaces import (
    AbstractUnitOfWork,
    ReviewLogDto,
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
        """Логика повторения просроченной карточки"""
        
        
        async with self.uow:
            try:
                # 1. Получаем карточку из базы данных
                previous_card = await self.uow.cards.get_by_id(input_dto.card_id)
                if previous_card is None:
                    raise CardNotExistsError(card_id=input_dto.card_id)
                
                # 6. Проверяем нужно ли сегодня повторять карточку
                now = datetime.now(timezone.utc)
                cutoff = await self._get_study_cutoff(now)

                if not previous_card.is_due(cutoff):
                    return None
                
                # Получаем колоду для параметров scheduler
                deck = await self.uow.decks.get_by_id(previous_card.deck_id)
                if deck is None:
                    raise ValueError(f"Deck {previous_card.deck_id()} not found")

                if not previous_card.in_learning:
                    raise CardNotInLearningError(card_id=previous_card.id)

                # 2. Определяем рейтинг FSRS
                rating_map = {
                    1: Rating.Again,
                    2: Rating.Hard,
                    3: Rating.Good,
                    4: Rating.Easy,
                }
                if input_dto.rating not in rating_map:
                    raise ValueError(f"Invalid rating: {input_dto.rating}")
                
                fsrs_rating = rating_map[input_dto.rating]

                # 3. Настраиваем планировщик
                scheduler = Scheduler(
                    desired_retention=deck.desired_retention,
                    learning_steps=(
                        timedelta(minutes=1),
                        timedelta(minutes=10),
                    ),
                    relearning_steps=(
                        timedelta(minutes=10),
                    ),
                    maximum_interval=deck.maximum_interval,
                    enable_fuzzing=True,
                )

                # 4. Выполняем повторение
                new_card, _ = previous_card.review(scheduler=scheduler, rating=fsrs_rating)
                
                 # 5. Сохраняем лог
                review_dt = datetime.now(timezone.utc)
                
                 # Получаем следующую дату повторения из обновленной карточки
                next_review_dt = new_card._fsrs_card.due

                # Вычисляем интервал как разницу в днях между следующей датой и текущей
                # interval_days = next_review_dt.day - review_dt.day
                interval_days = (next_review_dt - review_dt).days

                log_dto = ReviewLogDto(
                    id=uuid4(),
                    card_id=new_card.id,
                    deck_id=deck.id,
                    user_id=input_dto.user_id,
                    rating=input_dto.rating,
                    review_datetime=review_dt,
                    next_review_datetime=next_review_dt,
                    interval=interval_days,
                    review_duration=input_dto.review_duration,
                    previous_stability=previous_card._fsrs_card.stability or new_card._fsrs_card.stability,
                    previous_difficulty=previous_card._fsrs_card.difficulty or new_card._fsrs_card.difficulty,
                    new_stability=new_card._fsrs_card.stability,
                    new_difficulty=new_card._fsrs_card.difficulty,
                )

                await self.uow.review_logs.save(log_dto)                
                await self.uow.user_stats.autoincr_review(user_id=input_dto.user_id)

                # Обновляем карточку в БД
                await self.uow.cards.update(new_card)
                await self.uow.commit()

                # 6. Определяем, возвращать ли карточку на повтор сейчас
                if new_card.is_due(cutoff):
                    return new_card
                else:
                    return None

            except CardNotExistsError:
                raise
            except CardNotInLearningError:
                raise
            except Exception as e:
                self.logger.error(
                    "Ошибка при извлечении или обновлении карточки", error=str(e)
                )
                raise

