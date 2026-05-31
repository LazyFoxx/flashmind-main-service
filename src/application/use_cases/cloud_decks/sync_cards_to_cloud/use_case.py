from uuid import UUID, uuid4
from typing import List

import structlog

from src.application.interfaces import AbstractUnitOfWork
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

    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow
        self.logger = structlog.get_logger(__name__)

    async def execute(self, input_dto: SyncCardsToCloudInput) -> SyncCardsToCloudOutput:
        """
        Выполняет синхронизацию в зависимости от роли.
        """
        if input_dto.is_owner:
            return await self._sync_owner(input_dto.deck_id, input_dto.cloud_deck_id)
        else:
            return await self._sync_user(input_dto.deck_id, input_dto.cloud_deck_id)

    async def _sync_owner(self, deck_id: UUID, cloud_deck_id: UUID) -> SyncCardsToCloudOutput:
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
                    if template.front != card.front or template.back != card.back:
                        template = template.set_front_and_back(front=card.front, back=card.back)
                        await self.uow.cloud_cards.update(template)
                        updated_count += 1
                else:
                     # Новая карточка -> создаем шаблон
                    new_template_id = uuid4()
                    new_template = CloudCardTemplate(
                        id=new_template_id,
                        cloud_deck_id=cloud_deck_id,
                        front=card.front,
                        back=card.back,
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

            await self.uow.commit()
            return SyncCardsToCloudOutput(added=added_count, updated=updated_count, deleted=deleted_count)

    async def _sync_user(self, deck_id: UUID, cloud_deck_id: UUID) -> SyncCardsToCloudOutput:
        """
        Синхронизация для Пользователя (Получателя).
        Облачное состояние -> Локальное хранилище.
        """
        async with self.uow:
             # 1. Получаем облачные шаблоны
            cloud_templates: List[CloudCardTemplate] = await self.uow.cloud_cards.get_by_deck_id(
                cloud_deck_id=cloud_deck_id
             )
            
            templates = [t for t in cloud_templates]
            
             # 2. Получаем локальные карточки
            local_cards: List[Card] = await self.uow.cards.get_by_deck_id(deck_id=deck_id)
            local_cards_map = {c.card_template_id: c for c in local_cards if c.card_template_id}
            
            added_count = 0
            for template in templates:
                if template.id in local_cards_map:
                     # Карточка уже есть -> НЕ ОБНОВЛЯЕМ!
                     # Мы сохраняем правки пользователя.
                    pass
                else:
                     # Карточки нет локально -> Создаем её
                    new_card = Card(
                        id=uuid4(), # Новый локальный ID
                        deck_id=deck_id,
                        card_template_id=template.id,
                        front=template.front,
                        back=template.back,
                     )
                    await self.uow.cards.add(new_card, )
                    added_count += 1

            await self.uow.commit()
            return SyncCardsToCloudOutput(added=added_count, updated=0, deleted=0)
