from typing import Annotated, Optional
from uuid import UUID

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, File, Form, Query, Response, UploadFile, status

from src.application.use_cases import (
    GetStudyCardsInput,
    GetStudyCardsUseCase,
    NewToStudyInput,
    NewToStudyUseCase,
    ReviewDueCardInput,
    ReviewDueCardsUseCase,
)
from src.presentation.api.dependencies.auth import get_current_user_id
from src.presentation.api.dto.v1 import (
    NewToStudyRequest,
    ReviewDueCardRequest,
    StudyCardListResponse,
    StudyCardListWithStatsResponse,
    StudyCardResponse,
)

router = APIRouter(prefix="/study", tags=["study"])


@router.post(
    "",
    response_model=StudyCardListResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить список новых карточек на обучение",
    description=(
        "Принимает id колоды и количество карточек, которые надо перенесте из новых в изучаемые и возвращает их"
    ),
)
@inject
async def new_to_study_cards(
    payload: NewToStudyRequest,
    use_case: FromDishka[NewToStudyUseCase],
    user_id: UUID = Depends(get_current_user_id),
) -> StudyCardListResponse:
    dto = NewToStudyInput(
        deck_id=payload.deck_id,
        user_id=user_id,
        total=payload.total,
    )
    study_cards = await use_case.execute(input_dto=dto)

    return StudyCardListResponse(
        cards=[StudyCardResponse.from_entity(card) for card in study_cards.cards],
        total=study_cards.total,
    )


@router.get(
    "",
    response_model=StudyCardListWithStatsResponse,
    status_code=status.HTTP_200_OK,
    summary="Получение списка карточек “на изучении” + мета информация по колоде",
    description=(
        "принимает обязательный query параметр ?deck_id - id колоды. Возвращает карточки для обучения и информацию по колоде"
    ),
)
@inject
async def get_study_cards(
    use_case: FromDishka[GetStudyCardsUseCase],
    user_id: UUID = Depends(get_current_user_id),
    deck_id: UUID = Query(
        description="id колоды",
    ),
) -> StudyCardListWithStatsResponse:
    dto = GetStudyCardsInput(
        deck_id=deck_id,
        user_id=user_id,
    )
    study_cards = await use_case.execute(input_dto=dto)

    return StudyCardListWithStatsResponse(
        cards=[StudyCardResponse.from_entity(card) for card in study_cards.cards],
        total=study_cards.total,
        in_learning=study_cards.in_learning,
        learning_today=study_cards.learning_today,
        learned=study_cards.learned,
    )


@router.patch(
    "",
    response_model=StudyCardResponse,
    status_code=status.HTTP_200_OK,
    summary="Повторить карточку",
    description=(
        "принимает id карточки и оценку. В случае если карточка завершена возвращает status 204 No Content а иначе возвращает 200 OK и карточку"
    ),
)
@inject
async def update_cards_state(
    payload: ReviewDueCardRequest,
    use_case: FromDishka[ReviewDueCardsUseCase],
    user_id: UUID = Depends(get_current_user_id),
) -> StudyCardResponse | Response:
    dto = ReviewDueCardInput(
        card_id=payload.card_id,
        rating=payload.rating,
        user_id=user_id,
    )

    card = await use_case.execute(input_dto=dto)

    if card is None:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return StudyCardResponse.from_entity(card)
