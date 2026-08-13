from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import DateTime, Text, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.db.base import Base
from src.application.interfaces import AiAnalysisDto


class AiAnalysisModel(Base):
    """ORM-модель для хранения AI-анализов статистики обучения.
    
    Хранит:
        - stats_json: данные статистики, отправленные в AI
        - analysis_text: ответ AI (анализ + рекомендации)
        - analysis_date: дата, за которую анализ (месячный срез)
        - user_id / deck_id: владелец анализа
    """
    __tablename__ = "ai_analyses"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
    )

    # Владелец анализа
    user_id: Mapped[Optional[UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=True,
        index=True,
    )
    deck_id: Mapped[Optional[UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=True,
        index=True,
    )

    # Дата, за которую сделан анализ (месячный срез)
    analysis_date: Mapped[datetime] = mapped_column(
        DateTime(),
        nullable=False,
        index=True,
    )

    # Отправленные данные и полученный ответ
    stats_json: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    analysis_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    # Дата создания/обновления (обновляется при каждом UPDATE)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(),
        nullable=False,
        server_default=func.now(),
        server_onupdate=func.now(),
    )

    def to_dto(self) -> AiAnalysisDto:
        """Конвертирует ORM-модель в DTO."""
        return AiAnalysisDto(
            id=self.id,
            user_id=self.user_id,
            deck_id=self.deck_id,
            analysis_date=self.analysis_date,
            stats_json=self.stats_json,
            analysis_text=self.analysis_text,
        )

    @classmethod
    def from_dto(cls, dto: AiAnalysisDto) -> "AiAnalysisModel":
        """Создаёт модель из DTO."""
        return cls(
            id=dto.id,
            user_id=dto.user_id,
            deck_id=dto.deck_id,
            analysis_date=dto.analysis_date,
            stats_json=dto.stats_json,
            analysis_text=dto.analysis_text,
        )
