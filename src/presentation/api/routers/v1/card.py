from typing import Annotated, Optional
from uuid import UUID

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, File, Form, Response, UploadFile, status

from src.application.use_cases import CreateCardInput, CreateCardUseCase, GetCardUseCase
from src.presentation.api.dependencies.auth import get_current_user_id
from src.presentation.api.dto.v1 import (
    CardResponse,
    CreateCardRequest,
    ErrorMessageResponse,
)

router = APIRouter(prefix="/cards", tags=["cards"])


@router.post(
    "",
    response_model=CardResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новую карточку",
    description=("Создает новую карточку с front ( уникальное для колоды )"),
    responses={
        409: {
            "model": ErrorMessageResponse,
            "description": "Карточка с таким front уже существует в этой колоде",
        },
        404: {
            "model": ErrorMessageResponse,
            "description": "У пользователя нет такой колоды",
        },
    },
)
@inject
async def create_card(
    payload: CreateCardRequest,
    use_case: FromDishka[CreateCardUseCase],
    user_id: UUID = Depends(get_current_user_id),
) -> CardResponse:
    dto = CreateCardInput(
        user_id=user_id, deck_id=payload.deck_id, front=payload.front, back=payload.back
    )
    card = await use_case.execute(input_dto=dto)

    return CardResponse(
        id=card.card_id, deck_id=card.deck_id, front=card.front, back=card.back
    )


@router.get(
    "{card_id}",
    response_model=CardResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить карточку по ее id",
    description=("возвращает карточку со всеми основными полями"),
    responses={
        404: {
            "model": ErrorMessageResponse,
            "description": "Карточка не найдена",
        },
    },
)
@inject
async def get_card(
    card_id: UUID,
    use_case: FromDishka[GetCardUseCase],
    user_id: UUID = Depends(get_current_user_id),
) -> CardResponse:

    card = await use_case.execute(card_id=card_id)

    return CardResponse(
        id=card.card_id, deck_id=card.deck_id, front=card.front, back=card.back
    )
