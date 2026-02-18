from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional
from uuid import UUID

from fsrs import Card as FSRS_Card
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, func
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

    in_learning: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default="false",
        nullable=False,
        index=True,
    )

    # Поля FSRS заполняются ТОЛЬКО когда in_learning = True
    fsrs_state: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
    )
    next_due: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )
    difficulty: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
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

        if not self.in_learning:
            return Card(
                id=self.id,
                deck_id=self.deck_id,
                front=self.front,
                back=self.back,
                _fsrs_card=None,
            )

        return Card(
            id=self.id,
            deck_id=self.deck_id,
            front=self.front,
            back=self.back,
            _fsrs_card=FSRS_Card.from_json(self.fsrs_state),
        )

    @classmethod
    def from_domain(cls, card: Card) -> "CardModel":
        if not card.in_learning:
            return CardModel(
                id=card.id,
                deck_id=card.deck_id,
                front=card.front,
                back=card.back,
                in_learning=False,
                fsrs_state=None,
                next_due=None,
                difficulty=None,
            )

        # in_learning = True → берем параметры
        fsrs_card = card._fsrs_card or FSRS_Card()
        return CardModel(
            id=card.id,
            deck_id=card.deck_id,
            front=card.front,
            back=card.back,
            in_learning=True,
            fsrs_state=fsrs_card.to_json(),
            next_due=fsrs_card.due,
            difficulty=fsrs_card.difficulty,
        )
