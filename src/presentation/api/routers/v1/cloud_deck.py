from typing import Annotated
from uuid import UUID

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, Response, status

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
    GetCloudCardUseCase,
    GetPublicDecksUseCase,
)
from src.presentation.api.dependencies.auth import get_current_user_id
from src.presentation.api.dto.v1 import (
    EnableSharingRequest,
    EnableSharingResponse,
    SyncStats,
    ImportDeckResponse,
    ImportDeckRequest,
    CloudDeckResponse,
    CloudTemplateCardResponse,
    PublicDecksResponse,
    PublicDeckPreviewResponse,
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


@router.post(
    "/import",
    response_model=ImportDeckResponse,
    status_code=status.HTTP_200_OK,
    summary="Импорт облачной колоды (Облачная -> Локальная)",
    description=(
        "Импортирует облачную колоду в локальное хранилище. "
        "Создает новые карточки, но не перезаписывает существующие."
    ),
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
    )

@router.get(
    "/{deck_id}",
    response_model=CloudDeckResponse,
    status_code=status.HTTP_200_OK,
    summary="Превью облачной колоды",
    description=(
        ""
    ),
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
    "/cards/{card_id}",
    response_model=CloudTemplateCardResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить шаблон карточки по ее id",
    description=("возвращает карточку со всеми основными полями"),

)
@inject
async def get_card(
    card_id: UUID,
    use_case: FromDishka[GetCloudCardUseCase],
    # user_id: UUID = Depends(get_current_user_id),
) -> CloudTemplateCardResponse:

    card = await use_case.execute(card_id=card_id)

    return CloudTemplateCardResponse(
        id=card.card_id, front=card.front, back=card.back
    )



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


# @router.delete(
#     "/{deck_id}",
#     status_code=status.HTTP_204_NO_CONTENT,
#     summary="Удаление колоды из облака",
#     description=(
#         "Удаляет облачную колоду и отвязывает все пользовательские колоды "
#     ),
# )
# @inject
# async def delete_cloud_deck(
#     deck_id: UUID,
#     use_case: FromDishka[ImportDeckUseCase],
#     user_id: UUID = Depends(get_current_user_id),
# ) -> None:
#     """
#     Удаляет облачную колоду 
#     - Находит облачную колоду по cloud_uuid
#     - Удаляет ее физически с сервера и карточки связанные с ней
#     - Удаляет все связи других пользователей колоды и делает их локальными
#     """
#     # dto = ImportDeckInput(
#     #     user_id=user_id,
#     #     cloud_uuid=payload.cloud_uuid,
#     # )
#     # result = await use_case.execute(input_dto=dto)
    
#     return None