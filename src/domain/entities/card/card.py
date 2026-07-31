from dataclasses import dataclass, field, replace
from datetime import datetime
from typing import Any, Optional
from uuid import UUID, uuid4

from fsrs import Card as FSRS_Card
from fsrs import Rating, ReviewLog, Scheduler


@dataclass(slots=True, frozen=True)
class Card:
    """
    Доменная сущность карточки. Immutable, с FSRS для интервального повторения.
    """

    id: UUID
    deck_id: UUID
    front: str
    back: str
    difficulty: Optional[float] = None
    stability: Optional[float] = None
    in_learning: bool = False
    _fsrs_card: Optional[FSRS_Card] = None
    
    card_template_id: Optional[UUID] = None   # Ссылка на шаблон из облака (nullable)
    is_deleted: bool = False                  # Мягкое удаление

    def _copy(self, **kwargs: Any) -> "Card":
        """Создаёт копию текущей карточки с возможностью изменения некоторых параметров."""
        return Card(
            id=self.id,
            deck_id=self.deck_id,
            front=self.front,
            back=self.back,
            card_template_id=self.card_template_id,
            is_deleted=self.is_deleted,
            in_learning=kwargs.get("in_learning", self.in_learning),
            _fsrs_card=kwargs.get("_fsrs_card", self._fsrs_card),
        )

    def change_learning(self, in_learning: bool) -> "Card":
        """Бизнес-метод: переводит карточку в состояние обучения и назначает ей параметры FSRS или сбрасывает в None"""

        if in_learning:
            # Возвращаем новую карточку с FSRS
            return self._copy(in_learning=True, _fsrs_card=FSRS_Card())

        # Возвращаем карточку без FSRS, завершая процесс обучения
        return self._copy(in_learning=False, _fsrs_card=None)

    def review(self, scheduler: Scheduler, rating: Rating) -> tuple["Card", ReviewLog]:
        """Бизнес-метод: повторить, верни новую immutable Card. и лог"""

        if self._fsrs_card is None:
            raise ValueError("Карточка не в состоянии обучения")

        new_fsrs, review_log = scheduler.review_card(self._fsrs_card, rating)
        return (
            Card(
                id=self.id,
                deck_id=self.deck_id,
                front=self.front,
                back=self.back,
                in_learning=self.in_learning,
                _fsrs_card=new_fsrs,
            ),
            review_log,
        )

    def is_due(self, now: datetime) -> bool:
        """Проверить, пора ли повторять."""
        if self._fsrs_card is None:
            return False

        due_time: datetime = self._fsrs_card.due
        return due_time <= now
    
    def set_card_template_id(self, card_template_id: UUID) -> "Card":
        """устанавливает card template id."""
        return replace(self, card_template_id=card_template_id)
