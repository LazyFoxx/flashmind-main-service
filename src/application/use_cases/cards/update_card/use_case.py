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
                if input_dto.title is not None:
                    updates["title"] = input_dto.title
                if input_dto.front is not None:
                    updates["front"] = input_dto.front
                if input_dto.back is not None:
                    updates["back"] = input_dto.back
                if input_dto.hint1 is not None:
                    updates["hint1"] = input_dto.hint1
                if input_dto.hint2 is not None:
                    updates["hint2"] = input_dto.hint2
                if input_dto.is_suspended is not None:
                    updates["is_suspended"] = input_dto.is_suspended

                updated_card = dataclasses.replace(existing_card, **updates)
                
                if updated_card.card_template_id:
                    updated_card = updated_card.set_is_updated_true()

                # добавляем новою карточку
                await self.uow.cards.update(updated_card)
                await self.uow.commit()

                updated_card = await self.uow.cards.get_by_id(input_dto.card_id)
                self.logger.debug(
                    "Карточка обновлена",
                    title=updated_card.title,
                    card_id=updated_card.id,
                    user_id=input_dto.user_id,
                )
            except CardNotExistsError:
                raise
            except Exception as e:
                # возможные не отловленные ошибки
                self.logger.error("Ошибка при добавлении карточки в БД", error=str(e))
                raise

        return UpdateCardOutput(
            card=updated_card
        )
