from typing import Optional
from uuid import UUID

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, Query, status

from src.application.use_cases.ai.analyze_study_stat.dto import (
    AIAnalyzeStudyStatInput,
    AIAnalyzeStudyStatOutput,
)
from src.application.use_cases.ai.analyze_study_stat.use_case import AIAnalyzeStudyStatUseCase

from src.presentation.api.dependencies.auth import get_current_user_id
from src.presentation.api.dto.v1.ai import (
    AIAnalyzeStudyStatResponse,
    AIInsightDTO,
    AIProblemAreaDTO,
    AIRecommendationDTO,
    AIGoalsDTO,
    AIInsufficientReviewsResponse,
)

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post(
     "/analyze-study-stat",
     response_model=AIAnalyzeStudyStatResponse,
     status_code=status.HTTP_200_OK,
     summary="AI-анализ статистики обучения",
     description="Запускает AI-анализ статистики обучения пользователя или конкретной колоды и возвращает структурированный анализ с рекомендациями.",
     responses={
         422: {
             "model": AIInsufficientReviewsResponse,
             "description": "Недостаточно повторов для AI-анализа",
         },
     },
 )
@inject
async def analyze_study_stat(
    use_case: FromDishka[AIAnalyzeStudyStatUseCase],
    user_id: UUID = Depends(get_current_user_id),
    deck_id: Optional[UUID] = Query(
        None,
        description="Опциональный ID колоды. Если не указан — анализ по всем колодам пользователя.",
    ),
) -> AIAnalyzeStudyStatResponse:
     # 1. Вызываем Use Case
    input_dto = AIAnalyzeStudyStatInput(user_id=user_id, deck_id=deck_id)
    result: AIAnalyzeStudyStatOutput = await use_case.execute(input_dto=input_dto)

     # 2. Формируем ответ
    return AIAnalyzeStudyStatResponse(
        analysis_date=result.analysis_date,
        analysis_next_date=result.analysis_next_date,
        analysis_success=result.analysis_success,
        insights=[AIInsightDTO(title=item.title, text=item.text) for item in result.insights],
        problem_areas=[AIProblemAreaDTO(title=item.title, text=item.text) for item in result.problem_areas],
        recommendations=[AIRecommendationDTO(title=item.title, text=item.text) for item in result.recommendations],
        goals=[AIGoalsDTO(title=item.title, text=item.text) for item in result.goals],
    )
