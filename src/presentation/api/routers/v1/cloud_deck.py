from typing import Annotated
from uuid import UUID

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import JSONResponse

from src.application.use_cases import (
    EnableSharingInput,
    EnableSharingUseCase,
    ImportDeckInput,
    ImportDeckUseCase,
    GetUserProfileUseCase,
    GetProfileUserInput,
    GetCloudDeckUseCase,
    GetCloudDeckInput,
    GetCloudCardsUseCase,
    GetCloudCardsInput,
    GetPublicDecksUseCase,
    DeleteCloudDeckUseCase,
    DeleteCloudDeckInput,
    CanTakeOwnershipUseCase,
    CanTakeOwnershipInput,
    TakeOwnershipUseCase,
    TakeOwnershipInput,
)
from src.presentation.api.dependencies.auth import get_current_user_id
from src.presentation.api.dto.v1 import (
    EnableSharingRequest,
    EnableSharingResponse,
    SyncStats,
    ImportDeckResponse,
    ImportDeckRequest,
    CloudDeckResponse,
    PublicDecksResponse,
    PublicDeckPreviewResponse,
    CanTakeOwnershipResponse,
    TakeOwnershipResponse,
    TakeOwnershipRequest
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
    responses={
            410: {
                "description": "Автор удалил эту колоду из общего облака",
                "content": {
                    "application/json": {
                        "example": {
                            "error_code": "CLOUD_DECK_NOT_EXIST",
                            "message": "Автор удалил эту колоду из общего облака"
                        }
                    }
                }
            },
        },
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


@router.post(
    "/import",
    response_model=ImportDeckResponse,
    status_code=status.HTTP_200_OK,
    summary="Импорт облачной колоды (Облачная -> Локальная)",
    description=(
        "Импортирует облачную колоду в локальное хранилище. "
        "Создает новые карточки, но не перезаписывает существующие."
    ),
    responses={
            410: {
                "description": "Автор удалил эту колоду из общего облака",
                "content": {
                    "application/json": {
                        "example": {
                            "error_code": "CLOUD_DECK_NOT_EXIST",
                            "message": "Автор удалил эту колоду из общего облака"
                        }
                    }
                }
            },
        },
)
@inject
async def import_deck(
    payload: ImportDeckRequest,
    use_case: FromDishka[ImportDeckUseCase],
    user_id: UUID = Depends(get_current_user_id),
) -> ImportDeckResponse:
    """
    Импортирует облачную колоду к себе.
    - Находит облачную колоду по cloud_uuid
    - Создает локальную копию с карточками
    - Не перезаписывает существующие карточки
    """
    dto = ImportDeckInput(
        user_id=user_id,
        cloud_uuid=payload.cloud_uuid,
    )
    result = await use_case.execute(input_dto=dto)
    
    return ImportDeckResponse(
        deck_id=str(result.deck_id),
        added=result.added,
        updated=result.updated,
    )

@router.get(
    "/{deck_id}",
    response_model=CloudDeckResponse,
    status_code=status.HTTP_200_OK,
    summary="Превью облачной колоды",
    description=(
         ""
      ),
    responses={
        410: {
            "description": "Автор удалил эту колоду из общего облака",
            "content": {
                "application/json": {
                    "example": {
                        "error_code": "CLOUD_DECK_NOT_EXIST",
                        "message": "Автор удалил эту колоду из общего облака"
                    }
                }
            }
        },
    },
)
@inject
async def get_cloud_deck(
    deck_id: UUID,
    cloud_deck_use_case: FromDishka[GetCloudDeckUseCase],
    author_use_case: FromDishka[GetUserProfileUseCase],
    get_cards_use_case: FromDishka[GetCloudCardsUseCase],
    # user_id: UUID = Depends(get_current_user_id),
) -> CloudDeckResponse:
    """
    
    """
    
    dto_deck = GetCloudDeckInput(deck_id=deck_id)
    deck = await cloud_deck_use_case.execute(input_dto=dto_deck)
    
    dto_author = GetProfileUserInput(user_id=deck.deck.author_id)
    author = await author_use_case.execute(input_dto=dto_author)
    
    dto_cards = GetCloudCardsInput(deck_id=deck.deck.id)
    cards = await get_cards_use_case.execute(input_dto=dto_cards)
    
    return CloudDeckResponse.from_entity(deck=deck.deck, author=author, cards=cards.cards)

@router.get(
    "",
    response_model=PublicDecksResponse,
    status_code=status.HTTP_200_OK,
    summary="Список публичных колод одобренных колод",
    description=(
        ""
    ),
)
@inject
async def get_public_decks(
    use_case: FromDishka[GetPublicDecksUseCase],
    # user_id: UUID = Depends(get_current_user_id),
) -> PublicDecksResponse:
    """
    
    """
    public_decks = await use_case.execute()

    return PublicDecksResponse(decks=[PublicDeckPreviewResponse.from_entity(deck) for deck in public_decks.decks])


@router.delete(
    "/{cloud_deck_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удаление колоды из облака",
    description=(
         "Удаляет облачную колоду и отвязывает все пользовательские колоды "
      ),
)
@inject
async def delete_cloud_deck(
    cloud_deck_id: UUID,
    use_case: FromDishka[DeleteCloudDeckUseCase],
    user_id: UUID = Depends(get_current_user_id),
) -> None:
    """
    Удаляет облачную колоду 
    - Находит облачную колоду по cloud_uuid
    - Удаляет ее физически с сервера и карточки связанные с ней
    - Удаляет все связи других пользователей колоды и делает их локальными
    """
    dto = DeleteCloudDeckInput(
        user_id=user_id,
        cloud_deck_id=cloud_deck_id,
    )
    result = await use_case.execute(input_dto=dto)
    
    if result:
        return None



@router.get(
    "/{deck_id}/can-take-ownership",
    response_model=CanTakeOwnershipResponse,
    status_code=status.HTTP_200_OK,
    summary="Проверить может ли пользователь стать автором колоды",
    description=(
           "Проверяет может ли пользователь стать автором облачной колоды. "
           "Проверяет: изменил ли пользователь описание колоды и имеет ли 20% своих карточек."
       ),
    responses={
            410: {
                "description": "Автор удалил эту колоду из общего облака",
                "content": {
                    "application/json": {
                        "example": {
                            "error_code": "CLOUD_DECK_NOT_EXIST",
                            "message": "Автор удалил эту колоду из общего облака"
                        }
                    }
                }
            },
        },
)
@inject
async def can_take_ownership(
    deck_id: UUID,
    use_case: FromDishka[CanTakeOwnershipUseCase],
    user_id: UUID = Depends(get_current_user_id),
) -> CanTakeOwnershipResponse:
    """
    Проверяет может ли пользователь стать автором колоды.
       - Находит локальную колоду по deck_id
       - Проверяет изменил ли пользователь описание
       - Проверяет имеет ли 20% своих карточек в колоде
    """
    dto = CanTakeOwnershipInput(
        user_id=user_id,
        deck_id=deck_id,
      )
    result = await use_case.execute(input_dto=dto)
    return CanTakeOwnershipResponse(
        description_changed=result.description_changed,
        cards_needed_count=result.cards_needed_count,
      )



@router.post(
    "/take-ownership",
    response_model=TakeOwnershipResponse,
    status_code=status.HTTP_200_OK,
    summary="Отвязаться от облачной колоды и стать автором",
    description=(
        "Отвязывает локальную колоду от оригинальной облачной колоды и создаёт "
        "новую облачную колоду где текущий пользователь становится автором. "
        "Обе колоды продолжают существовать."
    ),
    responses={
            400: {
                "description": "Пользователь не может быть автором колоды - не прошел проверку",
            },
    }
)
@inject
async def take_ownership(
    payload: TakeOwnershipRequest,
    use_case_check: FromDishka[CanTakeOwnershipUseCase],
    use_case: FromDishka[TakeOwnershipUseCase],
    user_id: UUID = Depends(get_current_user_id),
) -> TakeOwnershipResponse | CanTakeOwnershipResponse:
    """
    Отвязывает локальную колоду от чужой облачной и создаёт новую облачную колоду.
    - Проверяет может ли пользователь быть автором колоды
    - Находит текущую локальную колоду по deck_id
    - Создаёт новую облачную колоду с текущим пользователем как автором
    - Отвязывает локальную колоду от оригинальной облачной
    - Привязывает к новой облачной колоде
    """
    
    
    dto = CanTakeOwnershipInput(user_id=user_id, deck_id=payload.deck_id)
    
    result = await use_case_check.execute(input_dto=dto)
    
    if result.cards_needed_count != 0 or not result.description_changed:
        return JSONResponse(
            status_code=400,
            content={"message": "Пользователь не может быть автором колоды - не прошел проверку"},
         )
    
    
    dto = TakeOwnershipInput(
        user_id=user_id,
        deck_id=payload.deck_id,
    )
    result = await use_case.execute(input_dto=dto)
    
    return TakeOwnershipResponse(
        cloud_uuid=str(result.cloud_uuid),
        status="ACTIVE" if result.is_approved else "PENDING_APPROVAL",
        type=result.type,
        sync_stats=SyncStats(
            added=result.added,
            updated=result.updated,
            deleted=result.deleted,
            )
    )

