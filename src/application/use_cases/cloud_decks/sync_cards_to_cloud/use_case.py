from uuid import UUID, uuid4
from typing import List

import structlog

from src.application.interfaces import AbstractUnitOfWork, AbstractCacheService
from src.domain.entities.cloud_card.cloud_card import CloudCardTemplate
from src.domain.entities.card.card import Card
from .dto import SyncCardsToCloudInput, SyncCardsToCloudOutput

class SyncCardsToCloudUseCase:
    """
    Синхронизирует карточки с облаком.
    
    Аргумент is_owner:
     - True: Автор синхронизирует своё облако с локальной копией.
       Локальные изменения (включая удаления) применяются к облаку.
     - False: Пользователь синхронизирует своё локальное хранилище с облаком.
       Облачные изменения применяются к локальному хранилищу сохраняя данные пользователя.
    """

    def __init__(self, uow: AbstractUnitOfWork, cache: AbstractCacheService):
        self.uow = uow
        self.logger = structlog.get_logger(__name__)
        self.cache = cache

    async def execute(self, input_dto: SyncCardsToCloudInput) -> SyncCardsToCloudOutput:
        """
        Выполняет синхронизацию в зависимости от роли.
        """
        try:
            if input_dto.is_owner:
                return await self._sync_owner(input_dto.deck_id,
                                              input_dto.cloud_deck_id,
                                              input_dto.is_public,
                                              input_dto.is_approved,
                                              )
            else:
                return await self._sync_user(input_dto.deck_id, input_dto.cloud_deck_id)
        except Exception as e:
            self.logger.error(
                "Ошибка при синхронизации карточек",
                error=str(e),
                deck_id=input_dto.deck_id,
                cloud_deck_id=input_dto.cloud_deck_id,
                is_owner=input_dto.is_owner,
            )
            raise

    async def _sync_owner(self, deck_id: UUID, cloud_deck_id: UUID, is_public: bool, is_approved: bool) -> SyncCardsToCloudOutput:
        """
        Синхронизация для Владельца (Авторa).
        Локальное состояние -> Эталон в облаке.
        """
        async with self.uow:
             # 1. Получаем локальные карточки
            local_cards = await self.uow.cards.get_by_deck_id(deck_id=deck_id)
            
            # 2. Получаем текущие облачные шаблоны
            existing_templates = await self.uow.cloud_cards.get_by_deck_id(
                cloud_deck_id=cloud_deck_id
             )
            
            templates_map = {t.id: t for t in existing_templates}
            touched_template_ids = set()

            added_count = 0
            updated_count = 0
            deleted_count = 0

            for card in local_cards:
                 # Если у карточки есть шаблон -> обновляем эталон
                if card.card_template_id  in templates_map:
                    template = templates_map[card.card_template_id]
                    if (
                        template.front != card.front
                        or template.back != card.back
                        or template.title != card.title
                        or template.hint1 != card.hint1
                        or template.hint2 != card.hint2
                    ):
                        template = template.set_content(
                            front=card.front,
                            back=card.back,
                            title=card.title,
                            hint1=card.hint1,
                            hint2=card.hint2,
                        )
                        await self.uow.cloud_cards.update(template)
                        updated_count += 1
                else:
                     # Новая карточка -> создаем шаблон
                    new_template_id = uuid4()
                    new_template = CloudCardTemplate(
                        id=new_template_id,
                        cloud_deck_id=cloud_deck_id,
                        title=card.title,
                        front=card.front,
                        back=card.back,
                        hint1=card.hint1,
                        hint2=card.hint2,
                    )
                    await self.uow.cloud_cards.add(new_template)
                    card = card.set_card_template_id(card_template_id=new_template_id)
                    await self.uow.cards.update(card)
                    
                    added_count += 1
                
                touched_template_ids.add(card.card_template_id)
            
            # удалять шаблоны, которых нет локально:
            for template in existing_templates:
                if template.id not in touched_template_ids:
                    await self.uow.cloud_cards.delete(template.id)
                    deleted_count += 1

            await self.uow.cloud_decks.update_last_synced_at(cloud_deck_id=cloud_deck_id)
            
            # Сброс кеша только для автора PUBLIC одобренной колоды ( если были изменения )
            if (is_public and is_approved) and (added_count or updated_count or deleted_count):
                await self.cache.invalidate(key="public_decks_approved:all")
            
            await self.uow.commit()
            return SyncCardsToCloudOutput(added=added_count, updated=updated_count, deleted=deleted_count)

    async def _sync_user(self, deck_id: UUID, cloud_deck_id: UUID) -> SyncCardsToCloudOutput:
        """
        Синхронизация для Пользователя (Получателя).
        Облачное состояние -> Локальное хранилище.
        
        Логика:
        - Если карточка НЕ была отредактирована (is_updated=False) → обновляем из облака
        - Если карточка была отредактирована (is_updated=True) → пропускаем, сохраняем правки
        - Если карточка мягко удалена локально то она пропускается ( не обновляется и не добавляется )
        """
        async with self.uow:
             # 1. Получаем облачные шаблоны
            cloud_templates = await self.uow.cloud_cards.get_by_deck_id(cloud_deck_id=cloud_deck_id)
            local_cards = await self.uow.cards.get_by_deck_id(deck_id=deck_id, include_deleted=True)
            local_cards_map = {c.card_template_id: c for c in local_cards if c.card_template_id}
            
            added_count = 0
            updated_count = 0
            
            for template in cloud_templates:
                if template.id in local_cards_map:
                    local_card = local_cards_map[template.id]
                    
                    # ПРОВЕРКА В ПАМЯТИ — не лезем в БД без необходимости
                    if (
                        local_card.front != template.front
                        or local_card.back != template.back
                        or local_card.title != template.title
                        or local_card.hint1 != template.hint1
                        or local_card.hint2 != template.hint2
                    ):
                        if not local_card.is_updated and not local_card.is_deleted:
                            updated_card = local_card._copy(
                                front=template.front,
                                back=template.back,
                                title=template.title,
                                hint1=template.hint1,
                                hint2=template.hint2,
                            )
                            await self.uow.cards.update(updated_card)
                            updated_count += 1

                else:
                     # Карточки нет локально -> Создаем её
                    new_card = Card(
                        id=uuid4(), # Новый локальный ID
                        deck_id=deck_id,
                        card_template_id=template.id,
                        title=template.title,
                        front=template.front,
                        back=template.back,
                        hint1=template.hint1,
                        hint2=template.hint2,
                     )
                    await self.uow.cards.add(new_card)
                    added_count += 1

            await self.uow.decks.update_last_synced_at(deck_id=deck_id)
            await self.uow.commit()
            return SyncCardsToCloudOutput(added=added_count, updated=updated_count, deleted=0)
