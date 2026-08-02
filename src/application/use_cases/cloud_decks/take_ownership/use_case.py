from uuid import UUID

import structlog

from src.domain.entities.deck.deck import Deck
from src.application.interfaces import (
    AbstractUnitOfWork, 
)

from src.application.use_cases import EnableSharingUseCase, EnableSharingInput

from src.application.exceptions import DeckNotExistsError, UserIsNotAuthor
from .dto import TakeOwnershipInput, TakeOwnershipOutput


class TakeOwnershipUseCase:
    def __init__(self, uow: AbstractUnitOfWork, enable_sharing_user_case: EnableSharingUseCase):
        self.uow = uow
        self.logger = structlog.get_logger(__name__)
        self.enable_sharing = enable_sharing_user_case
        
    
    async def execute(self, input_dto: TakeOwnershipInput) -> TakeOwnershipOutput:
        try:
            async with self.uow:
                
                deck = await self.uow.decks.get_by_id(deck_id=input_dto.deck_id, user_id=input_dto.user_id)
                
                if not deck:
                    self.logger.warning(
                        "Локальная колода не найдена",
                        deck_id=input_dto.deck_id,
                    )
                    raise DeckNotExistsError(deck_id=input_dto.deck_id, user_id=input_dto.user_id)
                
                old_cloud_uuid = deck.cloud_deck_id
                
                enable_dto = EnableSharingInput(user_id=input_dto.user_id, deck_id=input_dto.deck_id, type="PRIVATE", new_author=True)
                result = await self.enable_sharing.execute(input_dto=enable_dto)
                
                # Добавляем старого автора в previous_authors новой колоды
                if old_cloud_uuid:
                    old_cloud_deck = await self.uow.cloud_decks.get_by_id(deck_id=old_cloud_uuid)
                    if old_cloud_deck:
                        # Создаём список previous_authors со старым автором
                        previous_authors = old_cloud_deck.previous_authors + [old_cloud_deck.author_id]
                        print(previous_authors)

                        # Получаем НОВУЮ облачную колоду
                        new_cloud_deck = await self.uow.cloud_decks.get_by_id(deck_id=result.cloud_uuid)
                        if new_cloud_deck:
                            # Устанавливаем previous_authors новой колоде
                            print(new_cloud_deck)
                            new_cloud_deck = new_cloud_deck.set_previous_authors(previous_authors)
                            print(new_cloud_deck)
                            await self.uow.cloud_decks.update(new_cloud_deck)
                            await self.uow.commit()

            
            
            
            return TakeOwnershipOutput(old_cloud_uuid=old_cloud_uuid,
                                       cloud_uuid=result.cloud_uuid,
                                       type=result.type,
                                       is_approved=result.is_approved,
                                       added=result.added,
                                       updated=result.updated,
                                       deleted=result.deleted)    

                
        except (DeckNotExistsError):
            # Перебрасываем уже известные ошибки
            raise
        except Exception as e:
            self.logger.error("Ошибка при проверке на возможность стать автором", error=str(e), deck_id=input_dto.deck_id)
            raise
