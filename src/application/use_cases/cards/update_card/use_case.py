import dataclasses
from uuid import UUID, uuid4

import structlog

from src.application.exceptions import CardNotExistsError
from src.application.interfaces import (
    AbstractUnitOfWork,
)
from src.domain.entities import Card

from .dto import UpdateCardInput, UpdateCardOutput


class UpdateCardUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow
        self.logger = structlog.get_logger(__name__)

    async def execute(self, input_dto: UpdateCardInput) -> UpdateCardOutput:

        async with self.uow:
            try:
                # проверяем существование карточки
                existing_card = await self.uow.cards.get_by_id(
                    card_id=input_dto.card_id
                )
                if not existing_card:
                    raise CardNotExistsError(card_id=input_dto.card_id)

                updates = {}
                updates["front"] = input_dto.front
                updates["back"] = input_dto.back

                updated_card = dataclasses.replace(existing_card, **updates)  # type: ignore

                # добавляем новою карточку
                await self.uow.cards.update(updated_card)
                await self.uow.commit()
                self.logger.debug(
                    "Карточка обновлена",
                    front=updated_card.front,
                    user_id=input_dto.user_id,
                )
            except CardNotExistsError:
                raise
            except Exception as e:
                # возможные не отловленные ошибки
                self.logger.error("Ошибка при добавлении карточки в БД", error=str(e))
                raise

        return UpdateCardOutput(
            card_id=str(updated_card.id),
            deck_id=str(updated_card.deck_id),
            front=updated_card.front,
            back=updated_card.back,
        )
