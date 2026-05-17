from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import ForeignKey, Integer, Numeric, String, Text, func
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
        check_constraint="desired_retention BETWEEN 0.85 AND 0.95",
    )

    maximum_interval: Mapped[int] = mapped_column(
        Integer, nullable=False, default=36500, server_default="36500",
        check_constraint="maximum_interval BETWEEN 30 AND 99999",
    )
    
    color: Mapped[str] = mapped_column(
        String(7),
        nullable=False,
        default="#4A90E2",  # Синий по умолчанию
        server_default="'#4A90E2'",  # Для существующих записей
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

    def to_entity(self) -> Deck:
        """
        Преобразует ORM-модель в чистую доменную сущность.
        card_ids НЕ загружаются автоматически — их нужно подгружать отдельно,
        если они действительно нужны в данном контексте.
        """
        return Deck(
            id=self.id,
            name=self.name,
            description=self.description or "",
            user_id=self.user_id,
            card_ids=[],
            desired_retention=getattr(self, "desired_retention", 0.90),
            maximum_interval=getattr(self, "maximum_interval", 36500),
            color=self.color or "#4A90E2",
        )

    @classmethod
    def from_domain(cls, deck: Deck) -> "DeckModel":
        """
        Создаёт ORM-модель из доменной сущности.
        card_ids игнорируются — они хранятся в отдельной таблице cards.
        """
        return DeckModel(
            id=deck.id,
            name=deck.name,
            description=deck.description,
            user_id=deck.user_id,
            desired_retention=getattr(deck, "desired_retention", 0.90),
            maximum_interval=getattr(deck, "maximum_interval", 36500),
            color=deck.color or "#4A90E2",
        )
