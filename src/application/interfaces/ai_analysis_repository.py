from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional
from uuid import UUID

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AiAnalysisDto:
    """DTO для передачи данных AI-анализа между слоями."""
    id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    deck_id: Optional[UUID] = None
    analysis_date: Optional[datetime] = None
    stats_json: Optional[str] = None
    analysis_text: Optional[str] = None


class AbstractAiAnalysisRepository(ABC):
    """Интерфейс репозитория для хранения AI-анализов."""

    @abstractmethod
    async def upsert(self, dto: AiAnalysisDto) -> UUID:
        """Upsert: создать новый или обновить существующий.
        
        Если запись уже существует — обновить stats_json и analysis_text.
        created_at обновляется при update.
        
        Args:
            dto: DTO с данными анализа
            
        Returns:
            UUID записи (созданной или существующей)
        """
        ...

    @abstractmethod
    async def get_latest_by_user(self, user_id: UUID) -> Optional[AiAnalysisDto]:
        """Получить самый свежий анализ по пользователю (все колоды).
        
        Args:
            user_id: ID пользователя
            
        Returns:
            AiAnalysisDto или None
        """
        ...

    @abstractmethod
    async def get_latest_by_deck(self, deck_id: UUID) -> Optional[AiAnalysisDto]:
        """Получить самый свежий анализ по колоде.
        
        Args:
            deck_id: ID колоды
            
        Returns:
            AiAnalysisDto или None
        """
        ...
