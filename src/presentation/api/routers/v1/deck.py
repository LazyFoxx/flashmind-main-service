from typing import Annotated, Optional
from uuid import UUID

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, File, Form, UploadFile, status

from src.application.use_cases import CreateDeckInput, CreateDeckUseCase
from src.presentation.api.dependencies.auth import get_current_user_id
from src.presentation.api.dto.v1 import (
    CreateDeckRequest,
    CreateDeckResponse,
    ErrorMessageResponse,
)

router = APIRouter(prefix="/decks", tags=["decks"])


@router.post(
    "",
    response_model=CreateDeckResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новую колоду",
    description=(
        "Создает новую колоду с name ( уникальное название для пользователя )"
    ),
    responses={
        409: {
            "model": ErrorMessageResponse,
            "description": "Колода с таким названием уже существует",
        },
    },
)
@inject
async def get_user_profile(
    payload: CreateDeckRequest,
    use_case: FromDishka[CreateDeckUseCase],
    user_id: UUID = Depends(get_current_user_id),
) -> CreateDeckResponse:
    dto = CreateDeckInput(
        user_id=user_id, name=payload.name, description=payload.description
    )
    deck = await use_case.execute(input_dto=dto)

    return CreateDeckResponse(
        id=deck.deck_id, name=deck.name, description=deck.description
    )
