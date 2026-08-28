from uuid import UUID

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, File, Form, Query, status

from src.application.use_cases import (
    NewToStudyInput,
    NewToStudyUseCase,
    ReviewDueCardInput,
    ReviewDueCardsUseCase,
)
from src.presentation.api.dependencies.auth import get_current_user_id
from src.presentation.api.dto.v1 import (
    NewToStudyRequest,
    ReviewDueCardRequest,
    ReviewDueCardResponse,
    CardListResponse,
    CardResponse,
)

router = APIRouter(prefix="/study", tags=["study"])


@router.post(
    "",
    response_model=CardListResponse,
    status_code=status.HTTP_200_OK,
    summary="Перевести карточки из новых в изучаемые",
    description=(
        "Принимает id колоды и количество карточек, которые надо перенести из новых в изучаемые и возвращает список этих карточек"
    ),
)
@inject
async def new_to_study_cards(
    payload: NewToStudyRequest,
    use_case: FromDishka[NewToStudyUseCase],
    user_id: UUID = Depends(get_current_user_id),
) -> CardListResponse:
    dto = NewToStudyInput(
        deck_id=payload.deck_id,
        user_id=user_id,
        total=payload.total,
    )
    result = await use_case.execute(input_dto=dto)

    return CardListResponse(
            cards=[CardResponse.from_entity(card) for card in result.cards],
        )

@router.patch(
    "",
    response_model=ReviewDueCardResponse,
    status_code=status.HTTP_200_OK,
    summary="Повторить карточку",
    description=(
        "принимает id карточки и оценку. Возвращает карточку и результат. success=True значит карточка прошла повтор на сегодня, иначе требует еще повтор сегодня"
    ),
)
@inject
async def update_cards_state(
    payload: ReviewDueCardRequest,
    use_case: FromDishka[ReviewDueCardsUseCase],
    user_id: UUID = Depends(get_current_user_id),
) -> ReviewDueCardResponse:
    dto = ReviewDueCardInput(
        card_id=payload.card_id,
        rating=payload.rating,
        user_id=user_id,
        review_duration=payload.review_duration
    )

    result = await use_case.execute(input_dto=dto)

    return ReviewDueCardResponse(card=CardResponse.from_entity(card=result.card), success=result.success)
