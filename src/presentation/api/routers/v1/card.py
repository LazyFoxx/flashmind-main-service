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
    CardLightResponse,
    CardListResponse,
    CardResponse,
    CreateCardRequest,
    ErrorMessageResponse,
    UpdateCardRequest,
)

router = APIRouter(prefix="/cards", tags=["cards"])


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


@router.put(
    "{card_id}",
    response_model=CardResponse,
    status_code=status.HTTP_200_OK,
    summary="Обновить поля карточки",
    description=(
        "Частично изменяет карточку. Даже если обновляется одно поле - обязательно отправлять все поля в том числе не измененные"
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
        front=payload.front,
        back=payload.back,
    )
    card = await use_case.execute(input_dto=dto)

    return CardResponse(
        id=card.card_id, deck_id=card.deck_id, front=card.front, back=card.back
    )


@router.delete(
    "{card_id}",
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
    summary="Получить все карточки пользователя, или по колоде ( опционально с пагинацией )",
    description=(""),
    status_code=200,
)
@inject
async def get_cards(
    use_case: FromDishka[GetCardsUseCase],
    user_id: UUID = Depends(get_current_user_id),
    deck_id: Optional[UUID] = Query(
        None,
        description="фильтр по id колод, если не указан то выводит карточки по всем колодам пользователя",
    ),
    page: Optional[int] = Query(None, ge=1, description="Номер страницы (None = все)"),
    per_page: Optional[int] = Query(
        None, ge=1, le=500, description="Карточек на странице (None = все)"
    ),
    sort_by: Optional[str] = Query(
        None,
        description="Поле для сортировки: 'created_at', 'difficulty', 'stability'",
    ),
    sort_order: Optional[str] = Query(
        None,
        description="Направление сортировки: 'asc' или 'desc'",
    ),
    
    
) -> CardListResponse:
    dto = GetCardsInput(user_id=user_id,
                        deck_id=deck_id,
                        page=page,
                        per_page=per_page,
                        sort_by=sort_by,
                        sort_order=sort_order
                        )

    result = await use_case.execute(dto)

    return CardListResponse(
        cards=[
            CardLightResponse(id=str(card[0]), deck_id=str(card[1]), front=str(card[2]), difficulty=card[3], stability=card[4])
            for card in result.cards
        ],
        total=result.total,
        page=page,
        per_page=per_page,
    )
