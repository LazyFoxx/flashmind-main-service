from uuid import UUID, uuid4

import structlog

from src.application.interfaces import (
    AbstractUnitOfWork,
)
from src.domain.entities import Deck

from .dto import UpdateDeckSettingsInput, UpdateDeckSettingsOutput


class UpdateDeckSettingsUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow
        self.logger = structlog.get_logger(__name__)

    async def execute(self, input_dto: UpdateDeckSettingsInput) -> UpdateDeckSettingsOutput:

        async with self.uow:
            try:
                deck = await self.uow.decks.get_by_id(input_dto.deck_id)
                
                if input_dto.user_id != deck.user_id:
                    raise
                
                updated_deck = deck.with_updated_settings(
                    new_desired_retention=input_dto.desired_retention,
                    new_maximum_interval=input_dto.maximum_interval,
                    new_color=input_dto.color,
                )

                await self.uow.decks.update_settings(deck=updated_deck)
                await self.uow.commit()
                self.logger.info(
                    "Настройки колоды успешно обновлены",
                    deck_name=updated_deck.name,
                    user_id=updated_deck.user_id,
                )
            except Exception as e:
                # возможные не отловленные ошибки
                self.logger.error("Ошибка при обновлении колоды", error=str(e))
                raise

        return UpdateDeckSettingsOutput(
            deck_id=updated_deck.id,
            desired_retention=updated_deck.desired_retention,
            maximum_interval=updated_deck.maximum_interval,
            color=updated_deck.color,
        )
