from uuid import UUID, uuid4

import structlog

from src.application.exceptions import DeckNotExistsError, UserNotFoundError, UserIsNotAuthor, CloudDeckNotExistsError
from src.application.interfaces import AbstractUnitOfWork, AbstractCacheService
from src.domain.entities import Deck, CloudDeck

from .dto import EnableSharingInput, EnableSharingOutput
from src.application.use_cases.cloud_decks.sync_cards_to_cloud.use_case import SyncCardsToCloudUseCase, SyncCardsToCloudInput


class EnableSharingUseCase:
    def __init__(self, uow: AbstractUnitOfWork,
                 sync_cards_use_case: SyncCardsToCloudUseCase,
                 cache: AbstractCacheService,):
        self.uow = uow
        self.sync_cards_use_case = sync_cards_use_case
        self.logger = structlog.get_logger(__name__)
        self.cache = cache

    async def execute(self, input_dto: EnableSharingInput) -> EnableSharingOutput:
        try:
            async with self.uow:
                
                 # 1. Находим локальную колоду
                deck = await self.uow.decks.get_by_id(deck_id=input_dto.deck_id)
                
                if not deck:
                    self.logger.info("Колода не найдена", deck_id=input_dto.deck_id)
                    raise DeckNotExistsError(deck_id=input_dto.deck_id, user_id=input_dto.user_id)
                
                if deck.user_id != input_dto.user_id:
                    self.logger.warning("Колода не принадлежит данному пользователю",
                                         deck_id=input_dto.deck_id, user_id=input_dto.user_id)
                    raise UserNotFoundError(user_id=input_dto.user_id)
                
                 # 2. Логика создания или обновления
                if deck.is_cloud_deck and not input_dto.new_author:
                     # Уже в облаке
                    cloud_deck_id = deck.cloud_deck_id
                    cloud_deck = await self.uow.cloud_decks.get_by_id(deck_id=cloud_deck_id)
                    if not cloud_deck:
                        self.logger.warning("Облачная колода не найдена", deck_id=cloud_deck_id)
                        raise CloudDeckNotExistsError(message="Облачная колода не найдена")
                    
                     # Проверяем что это автор колоды
                    if cloud_deck.author_id != input_dto.user_id:
                        self.logger.warning("Пользователь облачной колоды не может share колоду")
                        raise UserIsNotAuthor(user_id=input_dto.user_id, message="Вы используете колоду другого автора")
                    
                    if cloud_deck.type != input_dto.type:
                        cloud_deck = cloud_deck.change_type(type=input_dto.type)
                else:
                     # Новое добавление облачной колоды
                    cloud_uuid = uuid4()
                    cloud_deck = CloudDeck(
                        name=deck.name,
                        description=deck.description,
                        id=cloud_uuid,
                        author_id=input_dto.user_id,
                        type=input_dto.type,
                         # is_approved=True if input_dto.type == "PRIVATE" else False,
                        is_approved=True,
                        approved_at=None,
                     )

                    await self.uow.cloud_decks.add(cloud_deck)
                    
                     # При добавлении новой публичной ОДОБРЕННОЙ колоды сбрасываем кеш
                    await self.cache.invalidate(key="public_decks_approved:all")

                     # Сбрасываем прошлую связь если есть
                    deck = deck.to_local()
                     # Обновляем локальную колоду: связываем её с облаком
                    deck = deck.to_cloud(cloud_deck_id=cloud_uuid,
                                         cloud_type=cloud_deck.type,
                                         is_approved=cloud_deck.is_approved,
                                         author_id=cloud_deck.author_id,
                                          )

                    await self.uow.decks.update(deck)

                 # 9. Фиксируем транзакцию
                await self.uow.commit()
                    
                 # Производим синхронизацию карточек
                input_sync = SyncCardsToCloudInput(
                        deck_id=input_dto.deck_id,
                        cloud_deck_id=deck.cloud_deck_id,
                        is_owner=True)
                sync_result = await self.sync_cards_use_case.execute(input_dto=input_sync)

            return EnableSharingOutput(
                cloud_uuid=cloud_deck.id,
                type=cloud_deck.type,
                is_approved=cloud_deck.is_approved,
                added=sync_result.added,
                updated=sync_result.updated,
                deleted=sync_result.deleted,
             )
        except (DeckNotExistsError, UserNotFoundError, UserIsNotAuthor, CloudDeckNotExistsError):
             # Перебрасываем уже известные ошибки
            raise
        except Exception as e:
            self.logger.error(
                 "Ошибка при включении шаринга",
                error=str(e),
                deck_id=input_dto.deck_id,
                user_id=input_dto.user_id,
             )
            raise
