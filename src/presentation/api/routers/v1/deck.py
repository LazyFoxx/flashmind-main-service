from typing import Annotated, Optional
from uuid import UUID

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, File, Form, Response, UploadFile, status

from src.application.use_cases import (
    CreateDeckInput,
    CreateDeckUseCase,
    DeleteDeckInput,
    DeleteDeckUseCase,
    GetUserDecksUseCase,
    UpdateDeckInput,
    UpdateDeckUseCase,
)
from src.presentation.api.dependencies.auth import get_current_user_id
from src.presentation.api.dto.v1 import (
    CreateDeckRequest,
    DeckResponse,
    ErrorMessageResponse,
    UserDecksResponse,
    UpdateDeckRequest,
    DeckResponseUpdate,
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
        user_id=user_id, name=payload.name, description=payload.description, color=payload.color
    )
    deck = await use_case.execute(input_dto=dto)

    return DeckResponse(id=deck.deck_id,
                        name=deck.name,
                        description=deck.description,
                        color=deck.color,
                        total_cards=deck.total_cards,
                        repeat_cards=deck.due_cards_count,
                        desired_retention=deck.desired_retention,
                        maximum_interval=deck.maximum_interval)


@router.get(
    "",
    response_model=UserDecksResponse,
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
) -> UserDecksResponse:
    decks = await use_case.execute(user_id=user_id)

    return UserDecksResponse(
        decks=[DeckResponse.from_entity(deck) for deck in decks.decks]
    )


@router.put(
    "{deck_id}",
    response_model=UpdateDeckRequest,
    status_code=status.HTTP_200_OK,
    summary="Обновить поля колоды",
    description=(
        "Частично изменяет колоду. Даже если обновляется одно поля - обязательно отправлять все поля в том числе не измененные"
    ),
)
@inject
async def update_deck(
    deck_id: UUID,
    payload: UpdateDeckRequest,
    use_case: FromDishka[UpdateDeckUseCase],
    user_id: UUID = Depends(get_current_user_id),
) -> DeckResponseUpdate:
    dto = UpdateDeckInput(
        user_id=user_id,
        deck_id=deck_id,
        name=payload.name,
        description=payload.description,
        desired_retention=payload.desired_retention,
        maximum_interval=payload.maximum_interval,
        color=payload.color,
    )
    deck = await use_case.execute(input_dto=dto)

    return DeckResponseUpdate(id=deck.deck_id,
                        name=deck.name,
                        description=deck.description,
                        desired_retention=deck.desired_retention,
                        maximum_interval=deck.maximum_interval,
                        color=deck.color)


@router.delete(
    "{deck_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить колоду",
    description=("Удаляет колоду и все связанные с ней карточки"),
)
@inject
async def delete_deck(
    deck_id: UUID,
    use_case: FromDishka[DeleteDeckUseCase],
    user_id: UUID = Depends(get_current_user_id),
) -> None:
    dto = DeleteDeckInput(
        user_id=user_id,
        deck_id=deck_id,
    )

    await use_case.execute(input_dto=dto)

    return None
