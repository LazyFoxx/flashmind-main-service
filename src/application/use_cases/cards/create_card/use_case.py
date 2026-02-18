from uuid import UUID, uuid4

import structlog

from src.application.exceptions import CardAlreadyExistsError, DeckNotExistsError
from src.application.interfaces import (
    AbstractUnitOfWork,
)
from src.domain.entities import Card

from .dto import CreateCardInput, CreateCardOutput


class CreateCardUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow
        self.logger = structlog.get_logger(__name__)

    async def execute(self, input_dto: CreateCardInput) -> CreateCardOutput:

        new_card = Card(
            id=uuid4(),
            deck_id=input_dto.deck_id,
            front=input_dto.front,
            back=input_dto.back,
            in_learning=False,
        )

        async with self.uow:
            try:
                # проверяем существование колоды у пользователя
                deck = await self.uow.decks.get_by_id(
                    deck_id=input_dto.deck_id, user_id=input_dto.user_id
                )
                if not deck:
                    raise DeckNotExistsError(
                        deck_id=input_dto.deck_id, user_id=input_dto.user_id
                    )

                # нельзя иметь две карты с одним и тем же front в одной колоде.
                existing_card = await self.uow.cards.get_by_front(
                    front=new_card.front, deck_id=new_card.deck_id
                )
                if existing_card:
                    raise CardAlreadyExistsError(
                        front=existing_card.front, deck_id=existing_card.deck_id
                    )

                # добавляем новою карточку
                await self.uow.cards.add(card=new_card, deck_id=input_dto.deck_id)
                await self.uow.commit()
                self.logger.info(
                    "Карточка создана и добавлена в БД",
                    front=new_card.front,
                    user_id=input_dto.user_id,
                )
            except CardAlreadyExistsError:
                raise
            except DeckNotExistsError:
                raise
            except Exception as e:
                # возможные не отловленные ошибки
                self.logger.error("Ошибка при добавлении карточки в БД", error=str(e))
                raise

        return CreateCardOutput(
            card_id=str(new_card.id),
            deck_id=str(new_card.deck_id),
            front=new_card.front,
            back=new_card.back,
        )
