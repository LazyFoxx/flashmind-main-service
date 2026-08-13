import structlog

from src.application.interfaces import (
    AbstractUnitOfWork, AbstractCacheService
)

from src.application.use_cases import GetUserProfileUseCase, GetProfileUserInput
from .dto import PublicDecksListOutput


class GetPublicDecksUseCase:
    def __init__(self, uow: AbstractUnitOfWork, cache: AbstractCacheService, get_profile_use_case: GetUserProfileUseCase):
        self.uow = uow
        self.logger = structlog.get_logger(__name__)
        self.cache = cache
        self.get_profile_use_case =get_profile_use_case
    
    async def execute(self, ) -> PublicDecksListOutput:
        try:
            
            data = await self.cache.load("public_decks_approved:all")
            if data:
                decks_list = PublicDecksListOutput.from_dict(data)
                return decks_list
            
            
            async with self.uow:
                
                                
                decks = await self.uow.cloud_decks.get_public_decks(is_approved=True)
                decks_with_authors = []
                authors_map = {}
                
                for deck in decks:
                    
                    total_cards = await self.uow.cloud_cards.get_total_cards_count(cloud_deck_id=deck.id)
                    deck = deck.set_total_cards(total_cards=total_cards)
                    
                    if deck.author_id not in authors_map:
                        # получаем автора если еще не встречался
                        try:
                            author = await self.get_profile_use_case.execute(GetProfileUserInput(user_id=deck.author_id))
                            decks_with_authors.append((deck, author))
                            authors_map[deck.author_id] = author
                        except:
                            self.logger.error("Ошибка при получении автора публичной колоды", user_id=deck.author_id)
                            pass
                    else:
                        author = authors_map[deck.author_id]
                        decks_with_authors.append((deck, author))
                
                
            decks_list = PublicDecksListOutput.from_decks_with_authors(decks_with_authors)
            json_data = decks_list.to_json()
            await self.cache.save("public_decks_approved:all", json_data, ttl=72000)
            self.logger.info("Кэш обновлен", count=len(decks_list.decks))
            return decks_list

        except Exception as e:
            self.logger.error("Ошибка при получении публичных колод", error=str(e))
            raise
