from uuid import UUID
from datetime import datetime, time, timedelta, timezone

import structlog

from src.application.interfaces import (
    AbstractUnitOfWork,
)

from src.application.exceptions import DeckNotExistsError, CloudDeckNotExistsError
from .dto import GetCloudDeckOutput, GetCloudDeckInput


class GetCloudDeckUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow
        self.logger = structlog.get_logger(__name__)
    
    async def execute(self, input_dto: GetCloudDeckInput) -> GetCloudDeckOutput:
        try:
            async with self.uow:
                deck = await self.uow.cloud_decks.get_by_id(deck_id=input_dto.deck_id)

                if not deck:
                    self.logger.debug("Облачная колода не найдена", deck_id=input_dto.deck_id)
                    raise CloudDeckNotExistsError(message="Облачная колода не найдена")

                return GetCloudDeckOutput(deck=deck)
        except CloudDeckNotExistsError:
            # Перебрасываем уже известные ошибки
            raise
        except Exception as e:
            self.logger.error("Ошибка при получении облачной колоды", error=str(e), deck_id=input_dto.deck_id)
            raise
