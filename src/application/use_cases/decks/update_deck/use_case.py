from uuid import UUID, uuid4

import structlog

from src.application.exceptions import DeckAlreadyExistsError
from src.application.interfaces import (
    AbstractUnitOfWork,
)
from src.domain.entities import Deck

from .dto import UpdateDeckInput, UpdateDeckOutput


class UpdateDeckUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow
        self.logger = structlog.get_logger(__name__)

    async def execute(self, input_dto: UpdateDeckInput) -> UpdateDeckOutput:

        updated_deck = Deck(
            id=input_dto.deck_id,
            user_id=input_dto.user_id,
            name=input_dto.name,
            description=input_dto.description,
        )

        async with self.uow:
            try:

                await self.uow.decks.update(updated_deck)
                await self.uow.commit()
                self.logger.info(
                    "Колода успешно обновлена",
                    deck_name=updated_deck.name,
                    user_id=updated_deck.user_id,
                )
            except Exception as e:
                # возможные не отловленные ошибки
                self.logger.error("Ошибка при обновлении колоды", error=str(e))
                raise

        return UpdateDeckOutput(
            deck_id=str(updated_deck.id),
            name=updated_deck.name,
            description=updated_deck.description,
        )
