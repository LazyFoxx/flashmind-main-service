from typing import Annotated, Optional
from uuid import UUID

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, File, Form, UploadFile, status

from src.application.use_cases import GetUserProfileUseCase, UpdateUserProfileUseCase, DailyReviewStatUseCase, DailyReviewStatInput
from src.application.use_cases.users.get_user_profile.dto import GetProfileUserInput
from src.application.use_cases.users.update_user_profile.dto import (
    UpdateProfileUserInput,
)
from src.presentation.api.dependencies.auth import get_current_user_id
from src.presentation.api.dto.v1 import (
    UserProfileResponse,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/profile",
    response_model=UserProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить профиль пользователя со статистикой",
    description=("Возвращает имя, фамилию, ссылку на аватар и статистику повторений"),
)
@inject
async def get_user_profile(
    profile_use_case: FromDishka[GetUserProfileUseCase],
    stats_use_case: FromDishka[DailyReviewStatUseCase],
    user_id: UUID = Depends(get_current_user_id),
) -> UserProfileResponse:
     # 1. Вызываем Use Case для профиля
    profile_input = GetProfileUserInput(user_id=user_id)
    user_profile = await profile_use_case.execute(input_dto=profile_input)
    
     # 2. Вызываем Use Case для статистики
    stats_input = DailyReviewStatInput(user_id=user_id, days=28)
    stats = await stats_use_case.execute(input_dto=stats_input)

     # 3. Объединяем результаты
    return UserProfileResponse(
        first_name=user_profile.first_name,
        last_name=user_profile.last_name,
        avatar_url=user_profile.avatar_url,
        bio=user_profile.bio or "",
        total_reviews=stats.total_reviews,
        review_series=stats.review_series,
        daily_review_counts=stats.daily_review_counts,
    )


@router.patch(
    "/profile",
    response_model=UserProfileResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Обновляет профиль пользователя",
    description=(
        "Обновляет переданные поля на новые в профиле пользователя, в том числе фотографию"
    ),
)
@inject
async def update_user_profile(
    use_case: FromDishka[UpdateUserProfileUseCase],
    user_id: UUID = Depends(get_current_user_id),
    first_name: Annotated[Optional[str], Form(min_length=2, max_length=35)] = None,
    last_name: Annotated[Optional[str], Form(min_length=2, max_length=35)] = None,
    bio: Annotated[Optional[str], Form(max_length=500)] = None,
    avatar_file: Annotated[Optional[UploadFile], File()] = None,
) -> UserProfileResponse:
    dto = UpdateProfileUserInput(
        user_id=user_id,
        first_name=first_name,
        last_name=last_name,
        bio=bio,
        avatar_file=avatar_file,
    )

    user_profile = await use_case.execute(input_dto=dto)

    return UserProfileResponse(
        first_name=user_profile.first_name,
        last_name=user_profile.last_name,
        avatar_url=user_profile.avatar_url,
        bio=user_profile.bio,
    )




