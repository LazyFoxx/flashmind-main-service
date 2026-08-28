from typing import Annotated, Optional
from uuid import UUID

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, File, Form, Query, Response, UploadFile, status

from src.application.use_cases import (
    CreateCardInput,
    CreateCardUseCase,
    DeleteCardInput,
    DeleteCardUseCase,
    GetCardsInput,
    GetCardsUseCase,
    GetCardUseCase,
    UpdateCardInput,
    UpdateCardUseCase,
)

from src.presentation.api.dependencies.auth import get_current_user_id
from src.presentation.api.dto.v1 import (
    CardListResponse,
    CardResponse,
    CreateCardRequest,
    ErrorMessageResponse,
    UpdateCardRequest,
    CardDetailResponse,
)

router = APIRouter(prefix="/cards", tags=["cards"])


@router.get(
     "/{card_id}",
    response_model=CardDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить карточку по ее id",
    description=("возвращает карточку со всеми полями включая историю ревью"),
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
) -> CardDetailResponse:

    result = await use_case.execute(card_id=card_id, user_id=user_id)

    return CardDetailResponse.from_entity(
        result.card,
        review_stats=result.review_stats,
      )


@router.post(
    "",
    response_model=CardResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новую карточку",
    description=("Создает новую карточку (title - уникально для колоды)"),
    responses={
        409: {
            "model": ErrorMessageResponse,
            "description": "Карточка с таким title уже существует в этой колоде",
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
        user_id=user_id,
        deck_id=payload.deck_id,
        title=payload.title,
        front=payload.front,
        back=payload.back,
        hint1=payload.hint1,
        hint2=payload.hint2,
    )
    
    result = await use_case.execute(input_dto=dto)

    return CardResponse.from_entity(result.card)


@router.put(
     "/{card_id}",
    response_model=CardResponse,
    status_code=status.HTTP_200_OK,
    summary="Обновить поля карточки (partial update)",
    description=(
        "Частично изменяет карточку. Передавай только те поля, которые хочешь обновить. "
        "Непереданные поля останутся без изменений."
     ),
    responses={
        404: {
            "model": ErrorMessageResponse,
            "description": "Карточка не найдена",
        },
    },
)
@inject
async def update_card(
    card_id: UUID,
    payload: UpdateCardRequest,
    use_case: FromDishka[UpdateCardUseCase],
    user_id: UUID = Depends(get_current_user_id),
) -> CardResponse:
    dto = UpdateCardInput(
        user_id=user_id,
        card_id=card_id,
        title=payload.title,
        front=payload.front,
        back=payload.back,
        hint1=payload.hint1,
        hint2=payload.hint2,
        is_suspended=payload.is_suspended,
    )
    result = await use_case.execute(input_dto=dto)

    return CardResponse.from_entity(result.card)


@router.delete(
    "/{card_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить карточку",
    description=("Удаляет карточку по id, иденпотентно"),
)
@inject
async def delete_card(
    card_id: UUID,
    use_case: FromDishka[DeleteCardUseCase],
    user_id: UUID = Depends(get_current_user_id),
) -> None:
    dto = DeleteCardInput(
        user_id=user_id,
        card_id=card_id,
    )

    await use_case.execute(input_dto=dto)

    return None


@router.get(
    "",
    response_model=CardListResponse,
    summary="Получить все карточки пользователя по колоде",
    description=(""),
    status_code=200,
)
@inject
async def get_cards(
    use_case: FromDishka[GetCardsUseCase],
    user_id: UUID = Depends(get_current_user_id),
    deck_id: UUID = Query(
        None,
        description="фильтр по id колод",
    ),
    
) -> CardListResponse:
    dto = GetCardsInput(user_id=user_id,
                        deck_id=deck_id,
                        )
    
    result = await use_case.execute(dto)

    return CardListResponse(
        cards=[CardResponse.from_entity(card) for card in result.cards],
    )
