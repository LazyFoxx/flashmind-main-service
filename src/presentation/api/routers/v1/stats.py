from typing import Optional
from uuid import UUID

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, Query, status

from src.application.use_cases.stats.study_stat.dto import StudyStatInput, StudyStatOutput
from src.application.use_cases.stats.study_stat.use_case import StudyStatUseCase

from src.presentation.api.dependencies.auth import get_current_user_id
from src.presentation.api.dto.v1.stats import (
    CardTypePoint,
    CardTypeResponse,
    DifficultyDistributionPoint,
    DifficultyDistributionResponse,
    ForecastPoint,
    ForecastResponse,
    HourlyBreakdownPoint,
    HourlyBreakdownResponse,
    OneTimeMetricsResponse,
    ReviewCountPoint,
    ReviewCountResponse,
    ReviewTimePoint,
    ReviewTimeResponse,
    StabilityDistributionPoint,
    StabilityDistributionResponse,
    StudyStatsResponse,
)

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get(
    "/stats",
    response_model=StudyStatsResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить статистику по всем колодам или опционально по конкретной колоде пользователя.",
    description="Возвращает полную статистику: общее время изучения, прогноз повторений, графики повторений, время, продуктивность по часам, распределение по сложности/стабильности, типы карт.",
)
@inject
async def get_study_stats(
    use_case: FromDishka[StudyStatUseCase],
    user_id: UUID = Depends(get_current_user_id),
    deck_id: Optional[UUID] = Query(
        None,
        description="фильтр по id колоды, если не указан то выводит статистику по всем колодам пользователя",
    ),
) -> StudyStatsResponse:
    # 1. Вызываем Use Case — получаем сырые данные
    input_dto = StudyStatInput(user_id=user_id, deck_id=deck_id, days=30)
    result: StudyStatOutput = await use_case.execute(input_dto=input_dto)

    # 2. Формируем финальный ответ из сырых данных (presentation level)
    
    # one_time_metrics
    one_time_metrics = OneTimeMetricsResponse(
        total_study_seconds=result.total_study_seconds,
        total_reviews=result.total_reviews,
    )

    # forecast — превращаем Dict[str, int] в list of ForecastPoint
    forecast_points = [
        ForecastPoint(date=date_str, count=count)
        for date_str, count in result.forecast.items()
    ]
    forecast = ForecastResponse(points=forecast_points)

    # review_count — превращаем daily_review_by_rating в list of ReviewCountPoint
    review_count_points = []
    for date_str in sorted(result.daily_review_by_rating.keys()):
        ratings = result.daily_review_by_rating[date_str]
        review_count_points.append(ReviewCountPoint(
            date=date_str,
            forgotten=ratings.get(1, 0),
            hard=ratings.get(2, 0),
            good=ratings.get(3, 0),
            easy=ratings.get(4, 0),
        ))
    review_count = ReviewCountResponse(points=review_count_points)

    # review_time — превращаем dict в list of ReviewTimePoint
    review_time_points = [
        ReviewTimePoint(date=date_str, seconds=seconds)
        for date_str, seconds in sorted(result.daily_review_time.items())
    ]
    review_time = ReviewTimeResponse(points=review_time_points)

    # hourly_breakdown — используем готовые проценты из result.hourly_breakdown
    hour_ranges = [
        '00:00-04:00', '04:00-08:00', '08:00-12:00',
        '12:00-16:00', '16:00-20:00', '20:00-24:00',
    ]
    hourly_breakdown_points = []
    for hr in hour_ranges:
        percentage = result.hourly_breakdown.get(hr, 0.0)
        hourly_breakdown_points.append(HourlyBreakdownPoint(
            hour_range=hr,
            percentage=round(percentage, 1),
        ))
    hourly_breakdown = HourlyBreakdownResponse(points=hourly_breakdown_points)

    # difficulty_distribution
    difficulty_distribution_points = [
        DifficultyDistributionPoint(range_label=range_label, count=count)
        for range_label, count in sorted(result.difficulty.items())
    ]
    difficulty_distribution = DifficultyDistributionResponse(
        points=difficulty_distribution_points
    )

    # stability_distribution
    stability_distribution_points = [
        StabilityDistributionPoint(range_label=range_label, count=count)
        for range_label, count in sorted(result.stability.items())
    ]
    stability_distribution = StabilityDistributionResponse(
        points=stability_distribution_points
    )

    # card_types
    card_type_points = [
        CardTypePoint(card_type=card_type, count=count)
        for card_type, count in result.card_types.items()
    ]
    card_types = CardTypeResponse(points=card_type_points)

    # 3. Возвращаем готовый ответ
    return StudyStatsResponse(
        one_time_metrics=one_time_metrics,
        forecast=forecast,
        review_count=review_count,
        review_time=review_time,
        hourly_breakdown=hourly_breakdown,
        difficulty_distribution=difficulty_distribution,
        stability_distribution=stability_distribution,
        card_types=card_types,
    )
