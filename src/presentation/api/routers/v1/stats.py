from typing import Optional
from uuid import UUID

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status

# from src.application.use_cases import StudyStatUseCase, StudyStatInput

from src.presentation.api.dependencies.auth import get_current_user_id
from src.presentation.api.dto.v1 import (
    StudyStatsResponse,
)

router = APIRouter(prefix="/stats", tags=["stats"])


# @router.get(
#     "/",
#     response_model=StudyStatsResponse,
#     status_code=status.HTTP_200_OK,
#     summary="Получить статистику по всем колодам или опционально по конкретной колоде пользователя.",
#     description=(""),
# )
# @inject
# async def get_study_stats(
#     use_case: FromDishka[StudyStatUseCase],
#     user_id: UUID = Depends(get_current_user_id),
#     deck_id: Optional[UUID] = Query(
#         None,
#         description="фильтр по id колод, если не указан то выводит статистику по всем колодам пользователя",
#     ),
# ) -> StudyStatsResponse:
#      # 1. Вызываем Use Case для профиля
#     input_dto = StudyStatInput(user_id=user_id, deck_id=deck_id)
#     result = await use_case.execute(input_dto=input_dto)

#      # 3. Объединяем результаты
#     return StudyStatsResponse(

#     )
