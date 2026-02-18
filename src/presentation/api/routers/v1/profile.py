from typing import Annotated, Optional
from uuid import UUID

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, File, Form, UploadFile, status

from src.application.use_cases import GetUserProfileUseCase, UpdateUserProfileUseCase
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
    summary="Получить профиль пользователя",
    description=("Возвращает имя, фамилию, ссылку на аватар и т д."),
)
@inject
async def get_user_profile(
    use_case: FromDishka[GetUserProfileUseCase],
    user_id: UUID = Depends(get_current_user_id),
) -> UserProfileResponse:
    dto = GetProfileUserInput(user_id=user_id)
    user_profile = await use_case.execute(input_dto=dto)

    return UserProfileResponse(
        first_name=user_profile.first_name,
        last_name=user_profile.last_name,
        avatar_url=user_profile.avatar_url,
        bio=user_profile.bio,
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
