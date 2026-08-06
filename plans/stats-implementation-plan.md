# План реализации эндпоинта `/stats`

## Выполнено

### ✅ Шаг 10: Обновлён роутер GET /stats

**Файл:** `src/presentation/api/routers/v1/stats.py`

```python
from typing import Optional
from uuid import UUID

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, Query, status

from src.application.use_cases.stats.study_stat.dto import StudyStatInput, StudyStatOutput
from src.application.use_cases.stats.study_stat.use_case import StudyStatUseCase

from src.presentation.api.dependencies.auth import get_current_user_id
from src.presentation.api.dto.v1.stats import (
    CardTypeResponse,
    DifficultyDistributionResponse,
    ForecastResponse,
    HourlyBreakdownResponse,
    OneTimeMetricsResponse,
    ReviewCountResponse,
    ReviewTimeResponse,
    StabilityDistributionResponse,
    StudyStatsResponse,
)

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get(
    "/",
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
     # 1. Подготавливаем input DTO
    input_dto = StudyStatInput(user_id=user_id, deck_id=deck_id)
    
     # 2. Вызываем Use Case
    result: StudyStatOutput = await use_case.execute(input_dto=input_dto)
    
     # 3. Формируем ответ
    return StudyStatsResponse(
        one_time_metrics=OneTimeMetricsResponse(
            total_study_seconds=result.total_study_seconds,
         ),
        forecast=ForecastResponse(points=result.forecast_points),
        review_count=ReviewCountResponse(points=result.review_count_points),
        review_time=ReviewTimeResponse(points=result.review_time_points),
        hourly_breakdown=HourlyBreakdownResponse(points=result.hourly_breakdown_points),
        difficulty_distribution=DifficultyDistributionResponse(
            points=result.difficulty_distribution_points
         ),
        stability_distribution=StabilityDistributionResponse(
            points=result.stability_distribution_points
         ),
        card_types=CardTypeResponse(points=result.card_type_points),
     )
```

## Осталось сделать

| # | Задача | Статус |
|---|--------|--------|
| 1 | Обновить `StudyStatInput` — добавить `deck_id: Optional[UUID] = None` | ⏳ Ожидает |
| 2 | Обновить `StudyStatOutput` — добавить все 7 полей с типами | ⏳ Ожидает |
| 3 | Добавить `get_all_study_metrics()` в `AbstractReviewLogRepository` | ⏳ Ожидает |
| 4 | Реализовать `get_all_study_metrics()` в `ReviewLogRepository` | ⏳ Ожидает |
| 5 | Добавить `get_forecast_cards()` в `AbstractCardRepository` | ⏳ Ожидает |
| 6 | Реализовать `get_forecast_cards()` в `CardRepository` | ⏳ Ожидает |
| 7 | Добавить `get_cards_distribution()` в `AbstractCardRepository` | ⏳ Ожидает |
| 8 | Реализовать `get_cards_distribution()` в `CardRepository` | ⏳ Ожидает |
| 9 | Переписать `StudyStatUseCase.execute()` — 3 запроса + агрегация | ⏳ Ожидает |
| 10 | ✅ Обновить роутер `GET /stats` | ✅ Сделано |
| 11 | Проверить DI Container | ⏳ Ожидает |
