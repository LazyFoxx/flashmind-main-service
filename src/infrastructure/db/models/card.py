from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional
from uuid import UUID

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domain.entities.card.card import Card
from src.infrastructure.db.base import Base

if TYPE_CHECKING:
    from src.infrastructure.db.models import DeckModel


class CardModel(Base):
    __tablename__ = "cards"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
    )

    deck_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("decks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    front: Mapped[str] = mapped_column(
        String(512),
        nullable=False,
    )

    back: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    fsrs_state: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default="{}",
    )

    # Колонка ТОЛЬКО для быстрой сортировки и фильтрации по due
    # Никогда не используй её в бизнес-логике — только в запросах
    next_due: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    # Тоже самое!
    difficulty: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    deck: Mapped["DeckModel"] = relationship(
        "DeckModel",
        back_populates="cards",
        lazy="raise",
    )

    def to_entity(self) -> Card:
        """
        Преобразует ORM-модель в доменную сущность Card.
        """
        from fsrs import Card as FSRS_Card

        fsrs_card = FSRS_Card.from_json(self.fsrs_state)

        return Card(
            id=self.id,
            deck_id=self.deck_id,
            front=self.front,
            back=self.back,
            _fsrs_card=fsrs_card,
        )

    @classmethod
    def from_domain(cls, card: Card) -> "CardModel":
        """
        Создаёт ORM-модель из доменной сущности.
        """
        return CardModel(
            id=card.id,
            deck_id=card.deck_id,
            front=card.front,
            back=card.back,
            fsrs_state=card._fsrs_card.to_json(),
            next_due=card._fsrs_card.due,
            difficulty=card._fsrs_card.difficulty,
        )
