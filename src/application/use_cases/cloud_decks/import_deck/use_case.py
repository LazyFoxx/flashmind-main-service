from uuid import UUID, uuid4
from typing import List

import structlog

from src.application.interfaces import AbstractUnitOfWork
from src.domain.entities.cloud_card.cloud_card import CloudCardTemplate
from src.domain.entities.card.card import Card
from src.application.exceptions import DeckNotExistsError, DeckImportFromOwnAuthorError
from .dto import ImportDeckInput, ImportDeckOutput
from src.application.use_cases.cloud_decks.sync_cards_to_cloud.use_case import SyncCardsToCloudUseCase, SyncCardsToCloudInput
from src.domain.entities.deck.deck import Deck

class ImportDeckUseCase:
    """
    Импортирует облачную колоду в локальное хранилище пользователя.
    
    Логика:
    - Находит облачную колоду по cloud_uuid
    - Создает локальную копию колоды
    - Вызывает синхранизацию карточек
    """

    def __init__(self, uow: AbstractUnitOfWork, sync_cards_use_case: SyncCardsToCloudUseCase):
        self.uow = uow
        self.sync_cards_use_case = sync_cards_use_case
        self.logger = structlog.get_logger(__name__)

    async def execute(self, input_dto: ImportDeckInput) -> ImportDeckOutput:
        async with self.uow:
            # 1. Находим облачную колоду
            cloud_deck = await self.uow.cloud_decks.get_by_id(deck_id=input_dto.cloud_uuid)
            
            if not cloud_deck:
                self.logger.info("Облачная колода не найдена", cloud_uuid=input_dto.cloud_uuid)
                raise DeckNotExistsError(deck_id=input_dto.cloud_uuid, user_id=input_dto.user_id)

            # Проверяем, не пытается ли автор импортировать свою же колоду
            if cloud_deck.author_id == input_dto.user_id:
                self.logger.warning(
                     "Пользователь пытается импортировать свою же колоду",
                    cloud_uuid=input_dto.cloud_uuid,
                    user_id=input_dto.user_id
                )
                raise DeckImportFromOwnAuthorError(
                    deck_id=input_dto.cloud_uuid,
                    user_id=input_dto.user_id
            )

            # Проверяем, есть ли уже импорт этой облачной колоды
            local_deck = await self.uow.decks.get_by_cloud_deck_id(cloud_deck_id=input_dto.cloud_uuid,
                                                                   user_id=input_dto.user_id)
            
            
            if not local_deck:
                # Создаем новую локальную копию колоды
                local_deck_id = uuid4()
                local_deck = Deck(
                    id=local_deck_id,
                    name=cloud_deck.name,
                    description=cloud_deck.description,
                    user_id=input_dto.user_id,
                    cloud_deck_id=input_dto.cloud_uuid,
                    is_cloud_deck=True,
                    author_id=cloud_deck.author_id,
                )
                await self.uow.decks.add(local_deck)
                await self.uow.commit()

            
            input_sync = SyncCardsToCloudInput(deck_id=local_deck.id,
                                               cloud_deck_id=cloud_deck.id,
                                               is_owner=False)
            
            result = await self.sync_cards_use_case.execute(input_dto=input_sync)
            
            return ImportDeckOutput(
                deck_id=local_deck.id,
                added=result.added,
            )
