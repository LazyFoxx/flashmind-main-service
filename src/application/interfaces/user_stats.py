from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from uuid import UUID
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class UserStatsDto:
    """
    DTO для user stats.
    """
    user_id: UUID
    max_days_streak: int
    current_days_streak: int
    update_at: Optional[datetime] = None



class AbstractUserStatsRepository:
    """Репозиторий для статистики пользователя."""

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> Optional[UserStatsDto]:
        """Получить статистику пользователя по ID.
        Args:
            user_id: UUID пользователя
            
        Returns:
            UserStatsDto / None
         """
        ...
    
    @abstractmethod
    async def update(self, user_id: UUID, stats: UserStatsDto) -> None:
        """Обновляет статистику пользователя.
        Args:
            stats: UserStatsDto
            
        Returns:
            None
         """
        ...

