from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import Float, ForeignKey, Integer, String, func, DateTime
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.db.base import Base

class ReviewLogModel(Base):
    __tablename__ = "review_logs"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
    )

    card_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("cards.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    deck_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("decks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("user_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    rating: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="1: Again, 2: Hard, 3: Good, 4: Easy",
        index=True,
    )

    review_datetime: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )

    next_review_datetime: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    interval: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="Интервал в днях после ревью",
    )

    review_duration: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Длительность ревью в миллисекундах",
    )

    previous_stability: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="Стабильность до ревью",
    )

    previous_difficulty: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="Сложность до ревью",
    )

    new_stability: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="Стабильность после ревью",
    )

    new_difficulty: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="Сложность после ревью",
    )
