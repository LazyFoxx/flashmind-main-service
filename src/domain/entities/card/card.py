from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from fsrs import Card as FSRS_Card
from fsrs import Rating, Scheduler


@dataclass(slots=True, frozen=True)
class Card:
    """
    Доменная сущность карточки. Immutable, с FSRS для интервального повторения.
    """

    id: UUID
    deck_id: UUID
    front: str
    back: str
    in_learning: bool = False
    _fsrs_card: Optional[FSRS_Card] = None

    def review(self, scheduler: Scheduler, rating: Rating) -> "Card":
        """Бизнес-метод: повторить, верни новую immutable Card."""
        new_fsrs, _ = scheduler.review_card(self._fsrs_card, rating)
        return Card(
            id=self.id,
            deck_id=self.deck_id,
            front=self.front,
            back=self.back,
            _fsrs_card=new_fsrs,
        )

    def is_due(self, now: datetime) -> bool:
        """Проверить, пора ли повторять."""
        if self._fsrs_card is None:
            return False

        due_time: datetime = self._fsrs_card.due
        return now >= due_time
