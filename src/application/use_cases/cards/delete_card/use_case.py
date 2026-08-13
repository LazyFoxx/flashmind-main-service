from uuid import UUID, uuid4

import structlog

from src.application.exceptions import DeckAlreadyExistsError
from src.application.interfaces import (
    AbstractUnitOfWork,
)
from src.domain.entities import Card

from .dto import DeleteCardInput


class DeleteCardUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow
        self.logger = structlog.get_logger(__name__)

    async def execute(self, input_dto: DeleteCardInput) -> None:

        async with self.uow:
            try:

                # проверяем существование карточки, обеспечиваем иденпотентность
                card = await self.uow.cards.get_by_id(card_id=input_dto.card_id)
                if not card:
                    self.logger.debug(
                        "Карточки не существует",
                        card_id=input_dto.card_id,
                    )
                    return None

                await self.uow.cards.delete(card_id=input_dto.card_id)

                await self.uow.commit()
                self.logger.info(
                    "Карточка успешно удалена",
                    card_id=input_dto.card_id,
                    user_id=input_dto.user_id,
                )
            except Exception as e:
                # возможные не отловленные ошибки
                self.logger.error("Ошибка при удалении карточки", error=str(e))
                raise

        return None
