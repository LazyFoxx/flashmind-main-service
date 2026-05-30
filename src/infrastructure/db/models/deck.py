from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domain.entities import Deck
from src.infrastructure.db.base import Base

if TYPE_CHECKING:
    from src.infrastructure.db.models import CardModel


class DeckModel(Base):
    __tablename__ = "decks"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
        index=True,
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("user_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    cards: Mapped[list["CardModel"]] = relationship(
        "CardModel",
        back_populates="deck",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )
    
    desired_retention: Mapped[float] = mapped_column(
        Numeric(3, 2), nullable=False, default=0.90, server_default="0.90",
    )

    maximum_interval: Mapped[int] = mapped_column(
        Integer, nullable=False, default=36500, server_default="36500",
    )
    
    color: Mapped[str] = mapped_column(
        String(7),
        nullable=False,
        default="#4A90E2",   # Синий по умолчанию
        server_default="'#4A90E2'",   # Для существующих записей
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
    
    # --- Cloud Decks Fields ---
    
     # Ссылка на оригинальную облачную колоду (если это синхронизированная колода)
    cloud_deck_id: Mapped[Optional[UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("cloud_decks.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
     )

    # Флаг: является ли эта колода "облачной" (импортированной или синхронизируемой)
    is_cloud_deck: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
     )
    
    # Тип колоды: 'PUBLIC' или 'PRIVATE' (заполняется только для is_cloud_deck=True)
    cloud_type: Mapped[Optional[str]] = mapped_column(
        String(10),
        nullable=True,
        index=True,
      )

    # Для публичных колод: статус одобрения админом
    is_approved: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
     )

    # ID автора облачной колоды (кто её создал/публикует)
    author_id: Mapped[Optional[UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("user_profiles.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
     )


    def to_entity(self) -> Deck:
        return Deck(
            id=self.id,
            name=self.name,
            description=self.description or "",
            user_id=self.user_id,
            card_ids=[],
            desired_retention=float(self.desired_retention) if self.desired_retention is not None else 0.90,
            maximum_interval=self.maximum_interval or 36500,
            color=self.color or "#4A90E2",
            # Cloud fields
            cloud_deck_id=self.cloud_deck_id,
            is_cloud_deck=self.is_cloud_deck,
            cloud_type=self.cloud_type,
            is_approved=self.is_approved,
            author_id=self.author_id,
        )

    @classmethod
    def from_domain(cls, deck: Deck) -> "DeckModel":
        return DeckModel(
            id=deck.id,
            name=deck.name,
            description=deck.description,
            user_id=deck.user_id,
            desired_retention=getattr(deck, "desired_retention", 0.90),
            maximum_interval=getattr(deck, "maximum_interval", 36500),
            color=deck.color or "#4A90E2",
            # Cloud fields
            cloud_deck_id=getattr(deck, "cloud_deck_id", None),
            is_cloud_deck=getattr(deck, "is_cloud_deck", False),
            cloud_type=getattr(deck, "cloud_type", None),
            is_approved=getattr(deck, "is_approved", False),
            author_id=getattr(deck, "author_id", None),
        )
