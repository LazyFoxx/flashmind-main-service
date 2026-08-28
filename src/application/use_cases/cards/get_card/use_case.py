from typing import Optional
from uuid import UUID

import structlog

from src.application.exceptions import CardNotExistsError
from src.application.interfaces import (
    AbstractUnitOfWork,
)

from .dto import GetCardOutput, ReviewHistoryItem, CardReviewStats

class GetCardUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow
        self.logger = structlog.get_logger(__name__)

    async def execute(self, card_id: UUID, user_id: UUID) -> GetCardOutput:

        async with self.uow:
            try:
                card = await self.uow.cards.get_by_id(card_id=card_id)
                await self.uow.commit()

                if not card:
                    raise CardNotExistsError(card_id=card_id)
                

                self.logger.debug(
                    "Карточка найдена",
                    title=card.title,
                )
            except CardNotExistsError:
                raise
            except Exception as e:
                # возможные не отловленные ошибки
                self.logger.error("Ошибка при получении карточки", error=str(e))
                raise
            
            # Получаем историю ревью карточки
            review_history_raw = []
            try:
                review_history_raw = await self.uow.review_logs.get_card_review_history(
                    card_id=card_id
                 )
            except Exception as e:
                self.logger.warning(
                     "Не удалось получить историю ревью",
                    card_id=str(card_id),
                    error=str(e),
                 )
            
            # Формируем статистику ревью
            review_stats: Optional[CardReviewStats] = None
            if review_history_raw:
                last_review = review_history_raw[-1]
                last_review_datetime = last_review['review_datetime']

                review_history = [
                    ReviewHistoryItem(
                        review_datetime=item['review_datetime'],
                        rating=item['rating'],
                        difficulty=item['difficulty'],
                        stability=item['stability'],
                        review_duration_ms=item['review_duration_ms'] or 0,
                     )
                    for item in review_history_raw
                 ]

                next_review_datetime = None
                if card._fsrs_card is not None:
                    next_review_datetime = card._fsrs_card.due

                review_stats = CardReviewStats(
                    last_review_datetime=last_review_datetime,
                    next_review_datetime=next_review_datetime,
                    review_history=review_history,
                 )

        return GetCardOutput(
            card=card,
            review_stats=review_stats,
         )
