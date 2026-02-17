from typing import Annotated, Optional
from uuid import UUID

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, File, Form, UploadFile, status

from src.application.use_cases import (
    CreateDeckInput,
    CreateDeckUseCase,
    GetUserDecksUseCase,
)
from src.presentation.api.dependencies.auth import get_current_user_id
from src.presentation.api.dto.v1 import (
    CreateDeckRequest,
    DeckResponse,
    ErrorMessageResponse,
    GetUserDecksResponse,
)

router = APIRouter(prefix="/decks", tags=["decks"])


@router.post(
    "",
    response_model=DeckResponse,
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
async def create_deck(
    payload: CreateDeckRequest,
    use_case: FromDishka[CreateDeckUseCase],
    user_id: UUID = Depends(get_current_user_id),
) -> DeckResponse:
    dto = CreateDeckInput(
        user_id=user_id, name=payload.name, description=payload.description
    )
    deck = await use_case.execute(input_dto=dto)

    return DeckResponse(id=deck.deck_id, name=deck.name, description=deck.description)


@router.get(
    "",
    response_model=GetUserDecksResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить список колод пользователя",
    description=(
        "Получает список всех колод пользователя по user_id (передается с токеном)"
    ),
)
@inject
async def get_user_decks(
    use_case: FromDishka[GetUserDecksUseCase],
    user_id: UUID = Depends(get_current_user_id),
) -> GetUserDecksResponse:
    decks = await use_case.execute(user_id=user_id)

    return GetUserDecksResponse(
        decks=[DeckResponse.from_entity(deck) for deck in decks.decks]
    )
