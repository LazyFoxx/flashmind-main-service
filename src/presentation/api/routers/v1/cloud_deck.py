from typing import Annotated
from uuid import UUID

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, Response, status

from src.application.use_cases import (
    EnableSharingInput,
    EnableSharingUseCase,
)
from src.presentation.api.dependencies.auth import get_current_user_id
from src.presentation.api.dto.v1 import (
    EnableSharingRequest,
    EnableSharingResponse,
    SyncStats,
)

router = APIRouter(prefix="/cloud_decks", tags=["cloud_decks"])

@router.post(
    "/share",
    response_model=EnableSharingResponse,
    status_code=status.HTTP_200_OK,
    summary="Включить шаринг (Локальная -> Облачная)",
    description=(
        "Превращает локальную колоду в облачную. "
        "Генерирует уникальный UUID и ссылку для шаринга. "
        "Колода становится приватной по умолчанию, но доступна по ссылке."
    ),
)
@inject
async def enable_sharing(
    payload: EnableSharingRequest,
    use_case: FromDishka[EnableSharingUseCase],
    user_id: UUID = Depends(get_current_user_id),
) -> EnableSharingResponse:
    """
    Активирует шаринг для локальной колоды.
    - Создает запись в cloud_decks. если еще не создана.
    - Если ранее была связана то проводит синхранизацию карточек.
    - Генерирует cloud_uuid. для новой или берет уже созданный
    - Обновляет локальную колоду, связывая её с облаком. если еще не связана.
    """
    dto = EnableSharingInput(
        user_id=user_id,
        deck_id=payload.deck_id,
        type=payload.type.value
    )
    result = await use_case.execute(input_dto=dto)
    return EnableSharingResponse(
        cloud_uuid=result.cloud_uuid,
        status="ACTIVE" if result.is_approved else "PENDING_APPROVAL",
        type=result.type,
        sync_stats=SyncStats(
            added=result.added,
            updated=result.updated,
            deleted=result.deleted,
         )
     )


