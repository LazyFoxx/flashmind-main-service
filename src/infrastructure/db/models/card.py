# src/infrastructure/db/models/card.py
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional
from uuid import UUID

from fsrs import Card as FSRS_Card
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domain.entities.card.card import Card
from src.infrastructure.db.base import Base

if TYPE_CHECKING:
    from src.infrastructure.db.models import DeckModel
    from src.infrastructure.db.models.review_log import ReviewLogModel


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
    
    title: Mapped[str] = mapped_column(
        String(512),
        nullable=False,
        index=True,
     )

    front: Mapped[Any] = mapped_column(
        JSONB,
        nullable=False,
     )

    back: Mapped[Any] = mapped_column(
        JSONB,
        nullable=False,
     )
    
    hint1: Mapped[str] = mapped_column(
        String(512),
        nullable=True,
        index=True,
     )

    hint2: Mapped[str] = mapped_column(
        String(512),
        nullable=True,
        index=True,
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

    stability: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        index=True,
     )

    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        nullable=False,
     )

    deck: Mapped["DeckModel"] = relationship(
         "DeckModel",
        back_populates="cards",
        lazy="raise",
     )
    
     # параметры необходимые для облачных колод
    card_template_id: Mapped[Optional[UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("cloud_card_templates.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
     )
    
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default="false",
        nullable=False,
        index=True,
     )
    
    is_updated: Mapped[bool] = mapped_column(
            Boolean,
            default=False,
            server_default="false",
            nullable=False,
            index=True,
    )
    
    is_suspended: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default="false",
        nullable=False,
        index=True,
    )


    def to_entity(self) -> Card:
        from fsrs import Card as FSRS_Card

        if not self.in_learning:
            return Card(
                id=self.id,
                deck_id=self.deck_id,
                title=self.title,
                front=self.front,
                back=self.back,
                hint1=self.hint1,
                hint2=self.hint2,
                difficulty=self.difficulty,
                stability=self.stability,
                is_deleted=self.is_deleted,
                is_updated=self.is_updated,
                is_suspended=self.is_suspended,
                card_template_id=self.card_template_id,
                _fsrs_card=None,
                in_learning=False,
                created_at=self.created_at,
             )

        return Card(
            id=self.id,
            deck_id=self.deck_id,
            title=self.title,
            front=self.front,
            back=self.back,
            hint1=self.hint1,
            hint2=self.hint2,
            difficulty=self.difficulty,
            stability=self.stability,
            is_deleted=self.is_deleted,
            is_updated=self.is_updated,
            is_suspended=self.is_suspended,
            card_template_id=self.card_template_id,
             _fsrs_card=FSRS_Card.from_json(self.fsrs_state),
            in_learning=True,
            created_at=self.created_at,
         )

    @classmethod
    def from_domain(cls, card: Card) -> "CardModel":
      if not card.in_learning:
          return CardModel(
                id=card.id,
                deck_id=card.deck_id,
                title=card.title,
                front=card.front,
                back=card.back,
                hint1=card.hint1,
                hint2=card.hint2,
                in_learning=False,
                fsrs_state=None,
                next_due=None,
                difficulty=None,
                stability=None,
                is_deleted=card.is_deleted,
                is_updated=card.is_updated,
                is_suspended=card.is_suspended,
                card_template_id=card.card_template_id,
           )

      # in_learning = True → берем параметры
      fsrs_card = card._fsrs_card or FSRS_Card()
      return CardModel(
            id=card.id,
            deck_id=card.deck_id,
            title=card.title,
            front=card.front,
            back=card.back,
            hint1=card.hint1,
            hint2=card.hint2,
            in_learning=True,
            fsrs_state=fsrs_card.to_json(),
            next_due=fsrs_card.due,
            difficulty=fsrs_card.difficulty,
            stability=fsrs_card.stability,
            is_deleted=card.is_deleted,
            is_updated=card.is_updated,
            is_suspended=card.is_suspended,
            card_template_id=card.card_template_id,
       )
