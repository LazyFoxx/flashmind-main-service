from uuid import UUID, uuid4

import structlog

from src.application.exceptions import DeckAlreadyExistsError, UserNotFoundError
from src.application.interfaces import (
    AbstractUnitOfWork,
)
from src.domain.entities import Deck

from .dto import CreateDeckInput, CreateDeckOutput


class CreateDeckUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow
        self.logger = structlog.get_logger(__name__)

    async def execute(self, input_dto: CreateDeckInput) -> CreateDeckOutput:

        new_deck = Deck(
            id=uuid4(),
            user_id=input_dto.user_id,
            name=input_dto.name,
            description=input_dto.description,
        )

        async with self.uow:
            try:

                user = await self.uow.users.get_by_id(user_id=input_dto.user_id)

                if user is None:
                    raise UserNotFoundError(user_id=str(input_dto.user_id))

                # нельзя иметь две колоды с одним и тем же названием у одного пользователя.
                existing_deck = await self.uow.decks.get_by_name(
                    new_deck.name, user_id=input_dto.user_id
                )
                if existing_deck:
                    raise DeckAlreadyExistsError(
                        name=existing_deck.name, user_id=input_dto.user_id
                    )

                # добавляем новою колоду
                await self.uow.decks.add(deck=new_deck)
                await self.uow.commit()
                self.logger.info(
                    "Колода создана и добавлена в БД",
                    deck_name=new_deck.name,
                    user_id=input_dto.user_id,
                )
            except DeckAlreadyExistsError:
                raise
            except UserNotFoundError:
                raise
            except Exception as e:
                # возможные не отловленные ошибки
                self.logger.error("Ошибка при добавлении колоды в БД", error=str(e))
                raise

        return CreateDeckOutput(
            deck_id=str(new_deck.id),
            name=new_deck.name,
            description=new_deck.description,
        )
