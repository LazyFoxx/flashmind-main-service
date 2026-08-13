from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class AIInsightDTO(BaseModel):
    title: str = Field(..., description="Заголовок инсайта")
    text: str = Field(..., description="Текст инсайта")


class AIProblemAreaDTO(BaseModel):
    title: str = Field(..., description="Заголовок проблемной зоны")
    text: str = Field(..., description="Текст проблемной зоны")


class AIRecommendationDTO(BaseModel):
    title: str = Field(..., description="Заголовок рекомендации")
    text: str = Field(..., description="Текст рекомендации")


class AIGoalsDTO(BaseModel):
    title: str = Field(..., description="Заголовок цели")
    text: str = Field(..., description="Текст цели")


class AIAnalyzeStudyStatResponse(BaseModel):
    """Ответ на AI-анализ статистики обучения."""
    analysis_date: datetime = Field(
        ...,
        description="Дата и время когда был сделан анализ",
        examples=["2026-08-09T22:30:00"],
    )
    analysis_next_date: datetime = Field(
        ...,
        description="Дата когда можно будет получить следующий анализ (через 7 дней)",
        examples=["2026-08-16T22:30:00"],
    )
    analysis_success: bool = Field(
        ...,
        description="Успешно ли выполнен анализ",
        examples=[True],
    )

    # Structured fields
    insights: List[AIInsightDTO] = Field(default_factory=list)
    problem_areas: List[AIProblemAreaDTO] = Field(default_factory=list)
    recommendations: List[AIRecommendationDTO] = Field(default_factory=list)
    goals: List[AIGoalsDTO] = Field(default_factory=list)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "analysis_date": "2026-08-09T22:30:00",
                    "analysis_next_date": "2026-08-16T22:30:00",
                    "analysis_success": True,
                    "insights": [
                        {"title": "Отличный прогресс", "text": "Вы хорошо усваиваете материал"}
                    ],
                    "problem_areas": [],
                    "recommendations": [
                        {"title": "Увеличьте нагрузку", "text": "Попробуйте добавлять больше карточек"}
                    ],
                    "goals": [
                        {"title": "Снизить бэклог", "text": "Повторяйте хотя бы 20 карточек в день"}
                    ],
                }
            ]
        }
    }


class AIInsufficientReviewsResponse(BaseModel):
    """Ответ при недостатке повторов для AI-анализа."""
    error: str = Field(
        default="INSUFFICIENT_REVIEWS",
        description="Код ошибки",
    )
    message: str = Field(
        ...,
        description="Сообщение об ошибке с указанием количества повторов",
        examples=[
            "Недостаточно повторов для AI-анализа. У вас 45 из 100. Необходимо еще 55.",
        ],
    )
    total_reviews: int = Field(
        ...,
        description="Текущее количество повторов",
        examples=[45],
    )
    remaining_reviews: int = Field(
        ...,
        description="Сколько еще нужно повторов",
        examples=[55],
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "error": "INSUFFICIENT_REVIEWS",
                    "message": "Недостаточно повторов для AI-анализа. У вас 45 из 100. Необходимо еще 55.",
                    "total_reviews": 45,
                    "remaining_reviews": 55,
                }
            ]
        }
    }
