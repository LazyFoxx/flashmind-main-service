from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple, Union
from uuid import UUID
from zoneinfo import ZoneInfo
from sqlalchemy import delete, desc, func, select, update, case
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import AbstractCardRepository, Card
from src.infrastructure.db.models import CardModel, DeckModel, UserProfileModel


class SQlAlchemyCardRepository(AbstractCardRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, card_id: UUID) -> Optional[Card]:
        stmt = select(CardModel).where(
            CardModel.id == card_id,
            CardModel.is_deleted == False,
        )
        result = await self.session.execute(stmt)
        card_model = result.scalar_one_or_none()
        return card_model.to_entity() if card_model else None

    async def get_by_title(
        self, title: str, deck_id: Optional[UUID] = None
        ) -> Optional[Card]:
        stmt = select(CardModel).where(
            CardModel.title == title,
            CardModel.is_deleted == False,
         )

        if deck_id is not None:
            stmt = stmt.where(CardModel.deck_id == deck_id)

        result = await self.session.execute(stmt)
        card_model = result.scalar_one_or_none()
        return card_model.to_entity() if card_model else None

    async def add(self, card: Card) -> None:
        card_model = CardModel.from_domain(card)
        self.session.add(card_model)
        
        await self._update_deck_updated_at(card.deck_id)

    async def update(self, card: Card) -> None:
        if card._fsrs_card is None:
            stmt = (
                update(CardModel)
                  .where(CardModel.id == card.id)
                  .values(
                    title=card.title,
                    front=card.front,
                    back=card.back,
                    hint1=card.hint1,
                    hint2=card.hint2,
                    fsrs_state=None,
                    next_due=None,
                    difficulty=None,
                    stability=None,
                    card_template_id=card.card_template_id,
                    is_deleted=card.is_deleted,
                    is_updated=card.is_updated,
                    is_suspended=card.is_suspended,
                  )
              )
            await self._update_deck_updated_at(card.deck_id)
        else:
            stmt = (
            update(CardModel)
              .where(CardModel.id == card.id)
              .values(
                title=card.title,
                front=card.front,
                back=card.back,
                hint1=card.hint1,
                hint2=card.hint2,
                fsrs_state=card._fsrs_card.to_json(),
                next_due=card._fsrs_card.due,
                difficulty=card._fsrs_card.difficulty,
                stability=card._fsrs_card.stability,
                in_learning=card.in_learning,
                card_template_id=card.card_template_id,
                is_deleted=card.is_deleted,
                is_updated=card.is_updated,
                is_suspended=card.is_suspended,
              )
           )
        await self.session.execute(stmt)

    async def delete(self, card_id: UUID) -> None:
         # Получаем карточку без фильтра is_deleted, чтобы проверить существование
        card_stmt = select(CardModel).where(CardModel.id == card_id)
        card_result = await self.session.execute(card_stmt)
        card_model = card_result.scalar_one_or_none()

        if card_model is None:
            raise ValueError(f"Card with id {card_id} not found")

          # Если у карточки есть шаблон (card_template_id), делаем мягкое удаление
        if card_model.card_template_id:
             # Меняем is_deleted на True напрямую в БД без карточки домена
            stmt = (
                update(CardModel)
                .where(CardModel.id == card_id)
                .values(is_deleted=True)
            )
            await self.session.execute(stmt)
        else:
              # Иначе удаляем физически
            await self.session.execute(delete(CardModel).where(CardModel.id == card_id))
              # Обновляем updated_at у колоды
            await self._update_deck_updated_at(card_model.deck_id)

    # async def get_all_light_by_user_and_deck(
    #     self,
    #     user_id: UUID,
    #     desk: bool = True,
    #     deck_id: Optional[UUID] = None,
    #     offset: Optional[int] = None,  # None = все
    #     limit: Optional[int] = None,  # None = все
    #     created_at: Optional[bool] = None,
    #     difficulty: Optional[bool] = None,
    #     stability: Optional[bool] = None,
        

    # ) -> List[tuple[UUID, UUID, str, Optional[float], Optional[float]]]:

    #     query = select(
    #         CardModel.id,
    #         CardModel.deck_id,
    #         CardModel.front,
    #         CardModel.difficulty,
    #         CardModel.stability,
    #      )

    #     # Фильтруем только не удалённые карточки
    #     query = query.where(CardModel.is_deleted == False)

    #     # Если есть deck_id, фильтруем по нему
    #     if deck_id:
        #     query = query.where(CardModel.deck_id == deck_id)

        # # Если deck_id не передан, фильтруем по пользователю через колоды
        # else:
        #     query = (
        #         query.join(
        #             DeckModel
        #         )  # Присоединим DeckModel, чтобы фильтровать по колодам пользователя
        #         .join(
        #             UserProfileModel
        #         )  # Присоединим UserProfileModel, чтобы фильтровать по user_id
        #         .where(DeckModel.user_id == user_id)
        #     )
            
        
        # # сортировка
        # if created_at:
        #     if desk:
        #         query = query.order_by(desc(CardModel.created_at))
        #     else:
        #         query = query.order_by(CardModel.created_at)
        # elif difficulty:
        #     if desk:
        #         query = query.order_by(desc(CardModel.difficulty))
        #     else:
        #         query = query.order_by(CardModel.difficulty)
        # elif stability:
        #     if desk:
        #         query = query.order_by(desc(CardModel.stability))
        #     else:
        #         query = query.order_by(CardModel.stability)
        # else:
        #     query = query.order_by(desc(CardModel.created_at))
                

        # if limit is not None:
        #     query = query.offset(offset).limit(limit)

        # result = await self.session.execute(query)
        # rows = result.fetchall()

        # # Преобразуем результат в список кортежей
        # cards = [(row.id, row.deck_id, row.front, row.difficulty, row.stability) for row in rows]
        # return cards

    async def get_total_cards_by_deck_id(self, deck_id: UUID) -> int:
        query = select(func.count(CardModel.id)).where(
            CardModel.deck_id == deck_id,
            CardModel.is_deleted == False,
         )

        result = await self.session.execute(query)
        return result.scalar_one() or 0

    async def get_total_cards_by_deck_ids(
        self,
        deck_ids: List[UUID],
     ) -> List[Tuple[UUID, int]]:

         query = (
             select(
                 DeckModel.id.label("deck_id"),
                 func.count(CardModel.id).label("card_count"),
              )
              .outerjoin(CardModel, DeckModel.id == CardModel.deck_id)
              .group_by(DeckModel.id)
          )

         query = query.where(
             DeckModel.id.in_(deck_ids),
             CardModel.is_deleted == False,
          )
         result = await self.session.execute(query)
         rows = result.fetchall()
         return [(row.deck_id, row.card_count) for row in rows]

    async def get_by_deck_id(
        self,
        deck_id: UUID,
        in_learning: Optional[bool] = None,
        limit: Optional[int] = None,
        include_deleted: bool = False,
        include_suspended: bool = True, 
    ) -> List[Card]:

         # Базовый запрос, выбираем все карточки в колоде
        query = select(CardModel).where(
            CardModel.deck_id == deck_id,
         )
        
        if include_suspended:
            query = query.where(CardModel.is_suspended == False)
        
        if not include_deleted:
            query = query.where(CardModel.is_deleted == False)

        # Фильтрация по статусу обучения
        if in_learning is not None:
            query = query.where(CardModel.in_learning == in_learning)

        # сортировка по дате создания
        query = query.order_by(desc(CardModel.created_at))

        if limit is not None:
            query = query.limit(limit)

        result = await self.session.execute(query)
        card_models = result.scalars().all()

        return [card_model.to_entity() for card_model in card_models]

    async def get_due_cards(
        self,
        deck_id: UUID,
        due_before: datetime,
        limit: Optional[int] = None,
    ) -> list[Card]:
        query = (
            select(CardModel)
             .where(CardModel.deck_id == deck_id)
             .where(CardModel.next_due <= due_before)
             .where(CardModel.is_deleted == False)
             .where(CardModel.is_suspended == False)
             .order_by(CardModel.next_due.asc())
         )

        if limit is not None:
            query = query.limit(limit)

        result = await self.session.execute(query)
        card_models = result.scalars().all()

        return [card_model.to_entity() for card_model in card_models]
    

    # async def get_total_due_cards_by_deck_ids(
    #     self,
    #     deck_ids: List[UUID],
    #     due_before: datetime,
    # ) -> List[Tuple[UUID, int]]:
    #     """
    #     Возвращает список кортежей (deck_id, total_due_cards) для указанных колод.
    #     total_due_cards — это количество карт, у которых next_due <= due_before.
    #     """

    #     query = (
    #         select(
    #             CardModel.deck_id,
    #             func.count(
    #                 CardModel.id
    #               ).label("due_count"),
    #           )
    #           .where(CardModel.deck_id.in_(deck_ids))
    #           .where(CardModel.next_due.isnot(None))
    #           .where(CardModel.next_due <= due_before)
    #           .where(CardModel.is_deleted == False)
    #           .group_by(CardModel.deck_id)
    #       )

    #     result = await self.session.execute(query)
    #     rows = result.fetchall()
        
    #     return [(row.deck_id, row.due_count) for row in rows]
    
    async def _update_deck_updated_at(self, deck_id: UUID) -> None:
        """Обновляет updated_at у указанной колоды."""
        stmt = (
            update(DeckModel)
              .where(DeckModel.id == deck_id)
              .values(updated_at=func.now())
          )
        await self.session.execute(stmt)
        
    async def delete_orphan_deleted_cards(self) -> int:
        stmt = (
            delete(CardModel)
            .where(CardModel.is_deleted == True)
            .where(CardModel.card_template_id == None)
        )
        result = await self.session.execute(stmt)
        return result.rowcount

    async def get_difficulty_distribution(
        self,
        user_id: UUID,
        deck_id: Optional[UUID] = None,
    ) -> Dict[str, int]:
         # Создаем подзапрос для вычисления difficulty range
        base_conditions = [CardModel.is_deleted == False, CardModel.difficulty.isnot(None)]
        
        if deck_id is not None:
            base_conditions.append(CardModel.deck_id == deck_id)
        
        difficulty_subquery = (
            select(
                CardModel.id.label('card_id'),
                CardModel.deck_id,
                case(
                    (CardModel.difficulty >= 9, '9-10'),
                    (CardModel.difficulty >= 8, '8-9'),
                    (CardModel.difficulty >= 7, '7-8'),
                    (CardModel.difficulty >= 6, '6-7'),
                    (CardModel.difficulty >= 5, '5-6'),
                    (CardModel.difficulty >= 4, '4-5'),
                    (CardModel.difficulty >= 3, '3-4'),
                    (CardModel.difficulty >= 2, '2-3'),
                    (CardModel.difficulty >= 1, '1-2'),
                    else_='0-1',
                ).label('difficulty_range'),
            )
            .where(*base_conditions)
            .subquery()
        )
        
        # Основной запрос: агрегация по difficulty_range из подзапроса
        query = select(
            difficulty_subquery.c.difficulty_range,
            func.count(difficulty_subquery.c.card_id).label("count"),
        ).group_by(difficulty_subquery.c.difficulty_range)
        
        # Если deck_id не передан, фильтруем по пользователю через JOIN с decks
        if deck_id is None:
            query = query.join(
                DeckModel,
                DeckModel.id == difficulty_subquery.c.deck_id
            ).where(DeckModel.user_id == user_id)

        result = await self.session.execute(query)
        rows = result.fetchall()

        # Создаем словарь со всеми диапазонами и нулями
        all_ranges = ['1-2', '2-3', '3-4', '4-5', '5-6', '6-7', '7-8', '8-9', '9-10']
        distribution: Dict[str, int] = {range_label: 0 for range_label in all_ranges}

        # Заполняем реальными данными
        for row in rows:
            range_label = row.difficulty_range
            count = row.count
            if range_label in distribution:
                distribution[range_label] = count

        return distribution

    async def get_stability_distribution(
        self,
        user_id: UUID,
        deck_id: Optional[UUID] = None,
    ) -> Dict[str, int]:
         # Создаем подзапрос для вычисления stability range
        base_conditions = [CardModel.is_deleted == False, CardModel.stability.isnot(None)]
        
        if deck_id is not None:
            base_conditions.append(CardModel.deck_id == deck_id)
        
        stability_subquery = (
            select(
                CardModel.id.label('card_id'),
                CardModel.deck_id,
                case(
                    ((CardModel.stability >= 1) & (CardModel.stability < 25), '1-25 дней'),
                    ((CardModel.stability >= 25) & (CardModel.stability < 50), '25-50 дней'),
                    ((CardModel.stability >= 50) & (CardModel.stability < 100), '50-100 дней'),
                    else_='>100 дней',
                ).label('stability_range'),
            )
            .where(*base_conditions)
             .subquery()
         )
        
        # Основной запрос: агрегация по stability_range из подзапроса
        query = select(
            stability_subquery.c.stability_range,
            func.count(stability_subquery.c.card_id).label("count"),
         ).group_by(stability_subquery.c.stability_range)
        
        # Если deck_id не передан, фильтруем по пользователю через JOIN с decks
        if deck_id is None:
            query = query.join(
                DeckModel,
                DeckModel.id == stability_subquery.c.deck_id
             ).where(DeckModel.user_id == user_id)

        result = await self.session.execute(query)
        rows = result.fetchall()

        # Создаем словарь со всеми диапазонами и нулями
        all_ranges = ['1-25 дней', '25-50 дней', '50-100 дней', '>100 дней']
        distribution: Dict[str, int] = {range_label: 0 for range_label in all_ranges}

        # Заполняем реальными данными
        for row in rows:
            range_label = row.stability_range
            count = row.count
            if range_label in distribution:
                distribution[range_label] = count

        return distribution

    async def get_card_types_distribution(
        self,
        user_id: UUID,
        deck_id: Optional[UUID] = None,
    ) -> Dict[str, int]:

        from sqlalchemy import case, func

        # Базовый запрос
        query = select(
            CardModel.in_learning,
            CardModel.stability,
            CardModel.difficulty,
            func.count(CardModel.id).label("count"),
        )

        # Фильтруем только не удалённые карточки
        query = query.where(CardModel.is_deleted == False)

        # Если есть deck_id, фильтруем по нему
        if deck_id is not None:
            query = query.where(CardModel.deck_id == deck_id)
        else:
            # Если deck_id не передан, фильтруем по пользователю через колоды
            query = (
                query.join(
                    DeckModel
                )
                .where(DeckModel.user_id == user_id)
            )

        # Группируем по in_learning, stability, difficulty
        query = (
            query.group_by(
                CardModel.in_learning,
                CardModel.stability,
                CardModel.difficulty,
            )
        )

        result = await self.session.execute(query)
        rows = result.fetchall()

        # Создаем словарь со всеми типами и нулями
        distribution: Dict[str, int] = {
            'new': 0,
            'in_learning': 0,
            'learned': 0,
            'suspended': 0,
        }

        # Заполняем реальными данными
        for row in rows:
            in_learning = row.in_learning
            stability = row.stability
            difficulty = row.difficulty
            count = row.count
            
            if row.is_suspended:
                distribution['suspended'] += count
            elif not in_learning:
                # in_learning = False → новые
                distribution['new'] += count
            else:
                # in_learning = True
                # Проверяем условие для изученных
                if stability is not None and stability > 100:
                    if difficulty is not None and difficulty < 3:
                        # stability > 100 AND difficulty < 3 → изученные
                        distribution['learned'] += count
                    else:
                        # stability > 100 BUT difficulty >= 3 → изучаемые
                        distribution['in_learning'] += count
                else:
                    # stability <= 100 → изучаемые
                    distribution['in_learning'] += count

        return distribution

    async def get_forecast_due_cards(
        self,
        user_id: UUID,
        days: int = 30,
        deck_id: Optional[UUID] = None,
        timezone: str = "UTC",
     ) -> Dict[str, int]:

        user_tz = ZoneInfo(timezone) if timezone else ZoneInfo("UTC")
        now = datetime.now(user_tz)
        end_date = now + timedelta(days=days)
        today_str = now.strftime("%Y-%m-%d")

           # Базовый запрос
        query = select(
            func.date(CardModel.next_due).label("forecast_date"),
            func.count(CardModel.id).label("count"),
           )

           # Фильтруем только не удалённые карточки с next_due IS NOT NULL
        query = query.where(CardModel.is_deleted == False)
        query = query.where(CardModel.next_due.isnot(None))
          # Убираем >= now, чтобы включить все карточки с next_due <= end_date
          # Карточки с прошлой датой попадут в "сегодня" при заполнении словаря
        query = query.where(CardModel.next_due <= end_date)

           # Если есть deck_id, фильтруем по нему
        if deck_id is not None:
            query = query.where(CardModel.deck_id == deck_id)
        else:
              # Если deck_id не передан, фильтруем по пользователю через колоды
            query = (
                query.join(DeckModel)
                 .where(DeckModel.user_id == user_id)
            )

           # Группируем по дате
        query = query.group_by(func.date(CardModel.next_due))

        result = await self.session.execute(query)
        rows = result.fetchall()

           # Создаём словарь со всеми днями и нулями
        forecast: Dict[str, int] = {
              (now + timedelta(days=i)).strftime("%Y-%m-%d"): 0
             for i in range(days + 1)
          }

           # Заполняем реальными данными
           # Карточки с прошлой датой (просроченные) добавляем в "сегодня"
        for row in rows:
            date_str = row.forecast_date.strftime("%Y-%m-%d")
            if date_str in forecast:
                forecast[date_str] = row.count
            elif date_str < today_str:
                  # Просроченные карточки — добавляем в сегодняшний день
                if today_str in forecast:
                    forecast[today_str] += row.count

        return forecast
    
    async def get_hardest_cards(
        self,
        user_id: UUID,
        deck_id: Optional[UUID] = None,
        limit: int = 5,
    ) -> List[Card]:
        query = select(CardModel).where(
            CardModel.is_deleted == False,
            CardModel.stability.isnot(None),
            CardModel.difficulty.isnot(None),
        )
        
        if deck_id is not None:
            query = query.where(CardModel.deck_id == deck_id)
        else:
            query = (
                query.join(DeckModel)
                .where(DeckModel.user_id == user_id)
            )
        
        # Сортировка: сначала низкая стабильность, потом высокая сложность
        query = query.order_by(
            CardModel.stability.asc(),
            CardModel.difficulty.desc(),
        )
        
        query = query.limit(limit)
        
        result = await self.session.execute(query)
        card_models = result.scalars().all()
        
        return [card_model.to_entity() for card_model in card_models]


