from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date
from typing import Any, List, Optional
from pydantic import BaseModel
from src.domain.entities import Card, Deck

# ─── DTO РЕЗУЛЬТАТА AI-АНАЛИЗА ───────────────────────────────────────

class AIInsight(BaseModel):
    """Инсайт когнитивного анализа."""
    title: str
    text: str


class AIProblemArea(BaseModel):
    """Проблемная зона."""
    title: str
    text: str


class AIRecommendation(BaseModel):
    """Рекомендация."""
    title: str
    text: str

class AIGoals(BaseModel):
    """Цели на неделю."""
    title: str
    text: str

class AIStudyAnalysisResult(BaseModel):
    """Структурированный результат AI-анализа статистики обучения.
    
    Содержит:
      - insights: инсайты (удержание, регулярность, время)
      - problem_areas: проблемные зоны (рост долга, усталость)
      - recommendations: рекомендации на следующую неделю
      - goals: цели на неделю
    """
    
    insights: List[AIInsight] = []
    problem_areas: List[AIProblemArea] = []
    recommendations: List[AIRecommendation] = []
    goals: List[AIGoals] = []


# ─── ИМПОРТЫ И ВВОД ──────────────────────────────────────────────────

@dataclass(frozen=True, slots=True)
class ModerationResult:
    """Результат модерации колоды."""
    approved: bool
    reason: str      # Причина одобрения/отклонения
    severity: str      # "low", "medium", "high"


@dataclass(frozen=True, slots=True)
class AnalyzeStatsInput:
    # Обязательные поля
    stats_json: str                                           # Текущая статистика в формате JSON
    user_name: str                                            # Имя пользователя
    
    # Опциональные поля для сравнения
    previous_stats_json: Optional[str] = None                 # Статистика за прошлую неделю
    previous_answer: Optional[str] = None                     # Предыдущий ответ DeepSeek
    previous_date: Optional[date] = None                      # Дата предыдущего анализа


@dataclass(frozen=True, slots=True)
class AnalyzeStudyStatsResult:
    """Результат анализа статистики.
    
    При status=True — result содержит AIStudyAnalysisResult с DTO по параметрам.
    При status=False — result равен None (ошибка обрабатывается в сервисе).
    """
    status: bool
    result: Optional[AIStudyAnalysisResult] = None


class AbstractAIService(ABC):
    """Абстрактный сервис AI для получения подсказок и объяснений."""

    @abstractmethod
    async def moderate_public_deck(
        self,
        deck_name: str,
        deck_description: str,
        user_name: str,
        user_bio: Optional[str],
        sample_cards: list[tuple[str, str]],     # List of (front, back)
    ) -> ModerationResult:
        raise NotImplementedError

    @abstractmethod
    async def analyze_study_stats(
        self,
        input_data: AnalyzeStatsInput,
    ) -> AnalyzeStudyStatsResult:
        """Анализировать статистику обучения пользователя.

        Принимает DTO с текущей статистикой и опционально предыдущие данные
        для сравнения и выявления трендов.

        Args:
            input_data: DTO с данными для анализа:
                - stats_json: текущая статистика (обязательно)
                - user_name: имя пользователя (обязательно)
                - previous_stats_json: статистика за прошлую неделю (опционально)
                - previous_answer: предыдущий ответ DeepSeek (опционально)
                - previous_date: дата предыдущего анализа (опционально)

        Returns:
            AnalyzeStudyStatsResult с результатом анализа

        Логика метода:
            1. Если есть previous_stats_json и previous_answer —
              формируем контекст сравнения для AI
            2. Формируем промпт с текущей статистикой
            3. Если есть данные для сравнения — добавляем их в промпт
            4. AI должен вернуть:
                - Главные инсайты
                - Что стало лучше за неделю
                - Что стало хуже за неделю
                - Новые цели и рекомендации
        """
        raise NotImplementedError
