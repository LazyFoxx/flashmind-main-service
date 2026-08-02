from uuid import UUID
from datetime import datetime, time, timedelta, timezone

import structlog

from src.application.interfaces import (
    AbstractUnitOfWork,
)

from src.application.exceptions import DeckNotExistsError, UserIsNotAuthor
from .dto import CanTakeOwnershipInput, CanTakeOwnershipOutput


class CanTakeOwnershipUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow
        self.logger = structlog.get_logger(__name__)
    
    async def execute(self, input_dto: CanTakeOwnershipInput) -> CanTakeOwnershipOutput:
        try:
            async with self.uow:
                
                description_changed =True # если колоды нет облачной то описание считаем измененным
                cards_needed_count = 0
                
                deck = await self.uow.decks.get_by_id(deck_id=input_dto.deck_id, user_id=input_dto.user_id)
                if not deck:
                    self.logger.warning("Колода не найдена", deck_id=input_dto.deck_id)
                    raise DeckNotExistsError(deck_id=input_dto.deck_id, user_id=input_dto.user_id)
                
                if not deck.is_cloud_deck:
                    self.logger.warning("Колода должна быть привязана к облаку", deck_id=input_dto.deck_id)
                    raise DeckNotExistsError(deck_id=input_dto.deck_id, user_id=input_dto.user_id)
                
                
                cloud_deck = await self.uow.cloud_decks.get_by_id(deck_id=deck.cloud_deck_id)

                if cloud_deck:
                #сравниваем описание 
                    if cloud_deck.description == deck.description:
                        description_changed = False
                
                cards = await self.uow.cards.get_by_deck_id(deck_id=deck.id)
                
                total_author_cards = len( [card for card in cards if card.card_template_id] )
                total_local_cards = len( [card for card in cards if card.is_updated or not card.card_template_id] )
                
                # total_local_cards должен быть не менее  20% от total_author_cards
                all_need_cards = int(total_author_cards * 0.2)
                need_cards = all_need_cards - total_local_cards
                
                if need_cards <= 0:
                    cards_needed_count = 0
                else:
                    cards_needed_count = need_cards
                

                return CanTakeOwnershipOutput(description_changed=description_changed,
                                              cards_needed_count=cards_needed_count,
                                              allowed=True if description_changed and cards_needed_count == 0 else False
                                              )
                
        except (DeckNotExistsError):
            # Перебрасываем уже известные ошибки
            raise
        except Exception as e:
            self.logger.error("Ошибка при проверке на возможность стать автором", error=str(e), deck_id=input_dto.deck_id)
            raise
