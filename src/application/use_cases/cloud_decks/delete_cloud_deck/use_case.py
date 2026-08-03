import structlog

from src.domain.entities import Deck
from src.application.interfaces import (
    AbstractUnitOfWork, AbstractCacheService
)

from src.application.exceptions import DeckNotExistsError, UserIsNotAuthor
from .dto import DeleteCloudDeckInput, DeleteCloudDeckOutput


class DeleteCloudDeckUseCase:
    def __init__(self, uow: AbstractUnitOfWork, cache: AbstractCacheService,):
        self.uow = uow
        self.logger = structlog.get_logger(__name__)
        self.cache = cache
    
    async def execute(self, input_dto: DeleteCloudDeckInput) -> DeleteCloudDeckOutput:
        try:
            async with self.uow:
                cloud_deck = await self.uow.cloud_decks.get_by_id(deck_id=input_dto.cloud_deck_id)

                if not cloud_deck:
                    self.logger.debug("Облачная колода не найдена", deck_id=input_dto.cloud_deck_id)
                    raise DeckNotExistsError(f"Cloud deck {input_dto.cloud_deck_id} not found")
                
                if cloud_deck.author_id != input_dto.user_id:
                    self.logger.warning("Колоду может удалить только автор колоды!", cloud_deck_id=input_dto.cloud_deck_id, user_id=input_dto.user_id)
                    raise UserIsNotAuthor(user_id=input_dto.user_id, message="Колоду может удалить только автор колоды!")
                
                
                deck: Deck = await self.uow.decks.get_by_cloud_deck_id(cloud_deck_id=cloud_deck.id, user_id=input_dto.user_id)
                
                if not deck:
                    self.logger.warning(
                        "Локальная колода не найдена",
                        cloud_deck_id=input_dto.cloud_deck_id,
                    )
                    raise DeckNotExistsError(f"Cloud deck {input_dto.cloud_deck_id} not found")
                

                await self.uow.cloud_decks.delete(cloud_deck_id=cloud_deck.id)
                await self.uow.commit()
                
                # при удалении публичной облачной колоды сбрасываем кеш публичных облачных колод
                # if cloud_deck.type == "PUBLIC":
                await self.cache.invalidate(key="public_decks_approved:all")
                
                await self.uow.cards.delete_orphan_deleted_cards()
                
                local_deck = deck.to_local()
                
                await self.uow.decks.update(deck=local_deck)
                await self.uow.commit()
                

                
                
                return DeleteCloudDeckOutput(result=True)
        except (DeckNotExistsError, UserIsNotAuthor):
            # Перебрасываем уже известные ошибки
            raise
        except Exception as e:
            self.logger.error("Ошибка при удалении облачной колоды", error=str(e), deck_id=input_dto.cloud_deck_id)
            raise
