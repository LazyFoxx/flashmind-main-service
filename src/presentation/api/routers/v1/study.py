from typing import Annotated, Optional
from uuid import UUID

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, File, Form, Query, Response, UploadFile, status

from src.application.use_cases import NewToStudyInput, NewToStudyUseCase
from src.presentation.api.dependencies.auth import get_current_user_id
from src.presentation.api.dto.v1 import (
    NewToStudyRequest,
    StudyCardListResponse,
    StudyCardResponse,
)

router = APIRouter(prefix="/study", tags=["study"])


@router.post(
    "",
    response_model=StudyCardListResponse,
    status_code=status.HTTP_201_CREATED,
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
