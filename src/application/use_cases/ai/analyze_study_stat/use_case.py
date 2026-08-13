import json
import uuid
from uuid import UUID

import structlog
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from src.application.exceptions import InsufficientReviewsError, UserNotFoundError
from src.application.interfaces import (
    AbstractUnitOfWork,
    AbstractAIService,
    AnalyzeStatsInput,
    AnalyzeStudyStatsResult,
    AiAnalysisDto,
)
from src.application.interfaces.ai_service import AIStudyAnalysisResult

from src.application.use_cases.common.utils import get_current_datetime
from .dto import AIAnalyzeStudyStatInput, AIAnalyzeStudyStatOutput


class AIAnalyzeStudyStatUseCase:
    """
    Use Case: AIAnalyzeStudyStatUseCase
    
    Выполняет AI-анализ статистики обучения пользователя или конкретной колоды.
    
    Рабочий процесс:
        1. Проверяет существование пользователя
        2. Проверяет достаточно ли повторов (минимум 100) для AI-анализа
        3. Проверяет не выполнялся ли анализ за последние 7 дней
        4. Собирает статистику (по всем колодам или по конкретной)
        5. Отправляет данные в AI-сервис и возвращает анализ с рекомендациями
    
    Args:
        uow: Unit of Work для доступа к репозиториям
        ai: AI-сервис для выполнения анализа
    
    Returns:
        AIAnalyzeStudyStatOutput с результатом анализа или сообщением об ошибке
    """

    def __init__(self, uow: AbstractUnitOfWork, ai: AbstractAIService):
        self.uow = uow
        self.logger = structlog.get_logger(__name__)
        self.ai = ai
    
    async def _get_user_stats(self, user_id: UUID) -> dict[str, Any]:
        """
        Возвращает структурированный JSON со статистикой пользователя по ВСЕМ колодам для AI-анализа.
        
        Собирает все доступные метрики:
         - Общее время изучения и количество повторов (всё время)
         - Повторения по дням и рейтингам (7 дней)
         - Время ревью по дням (7 дней)
         - Продуктивность по часам (30 дней)
         - Распределение по сложности, стабильности, типам карточек (всё время)
         - Прогноз повторений на 7 дней вперёд
         - Среднее время и успешность по дням (7 дней)
        
        Args:
            user_id: ID пользователя для которого собирается статистика
            
        Returns:
            dict: Структурированный JSON со всеми метриками для отправки в AI
        """
        
        # 1. Общее время изучения ЗА ВСЁ ВРЕМЯ (по всем колодам)
        total_study_seconds = await self.uow.review_logs.get_total_study_seconds(
            user_id=user_id, deck_id=None  # None = все колоды
        )
        
        # 2. Общее количество повторов ЗА ВСЁ ВРЕМЯ (по всем колодам)
        total_reviews = await self.uow.review_logs.get_total_reviews_count(
            user_id=user_id, deck_id=None  # None = все колоды
        )
        
        user = await self.uow.users.get_by_id(user_id)
        user_tz = user.timezone if user else "UTC"
        
        # 3. Повторения по дням и рейтингам — ЗА 7 ДНЕЙ (по всем колодам)
        daily_review_by_rating_7d = await self.uow.review_logs.get_daily_review_by_rating(
            user_id=user_id, days=7, deck_id=None, timezone=user_tz
        )
        
        # 4. Время ревью по дням — ЗА 7 ДНЕЙ (по всем колодам)
        daily_review_time_7d = await self.uow.review_logs.get_daily_review_time(
            user_id=user_id, deck_id=None, days=7, timezone=user_tz
        )
        
        # 5. Продуктивность по часам — ЗА 30 ДНЕЙ (по всем колодам)
        hourly_breakdown_30d = await self.uow.review_logs.get_hourly_breakdown(
            user_id=user_id, deck_id=None, days=30, timezone=user_tz
        )
        
        # 6. Распределение по сложности — ЗА ВСЁ ВРЕМЯ (по всем колодам)
        difficulty_distribution = await self.uow.cards.get_difficulty_distribution(
            user_id=user_id, deck_id=None  # None = все колоды пользователя
        )
        
        # 7. Распределение по стабильности — ЗА ВСЁ ВРЕМЯ (по всем колодам)
        stability_distribution = await self.uow.cards.get_stability_distribution(
            user_id=user_id, deck_id=None
        )
        
        # 8. Распределение по типам карточек — ЗА ВСЁ ВРЕМЯ (по всем колодам)
        card_types_distribution = await self.uow.cards.get_card_types_distribution(
            user_id=user_id, deck_id=None
        )
        
        # 9. Прогноз на 7 дней вперёд (по всем колодам)
        forecast_7d = await self.uow.cards.get_forecast_due_cards(
            user_id=user_id, deck_id=None, days=7, timezone=user_tz
        )
        
        # ─── ВЫЧИСЛЕНИЕ СРЕДНИХ ЗА 7 ДНЕЙ ───
        
        # Среднее время одного повторения за 7 дней
        total_reviews_7d = sum(
            count
            for rating_counts in daily_review_by_rating_7d.values()
            for count in rating_counts.values()
        )
        total_time_7d = sum(daily_review_time_7d.values())
        avg_review_duration_7d = (
            round(total_time_7d / total_reviews_7d, 1) 
            if total_reviews_7d > 0 else 0
        )
        
        # Средняя успешность (процент правильных ответов) за 7 дней
        total_good_easy_7d = sum(
            rating_counts.get(3, 0) + rating_counts.get(4, 0)
            for rating_counts in daily_review_by_rating_7d.values()
        )
        avg_success_rate_7d = (
            round((total_good_easy_7d / total_reviews_7d) * 100, 1)
            if total_reviews_7d > 0 else 0
        )
        
        # ─── РАСЧЁТ СРЕДНЕГО ВРЕМЕНИ И УСПЕШНОСТИ ДЛЯ КАЖДОГО ДНЯ (7 ДНЕЙ) ───
        daily_stats_7d = {} 

        for date_str, rating_counts in daily_review_by_rating_7d.items():
            total_time_for_day = daily_review_time_7d.get(date_str, 0)
            total_reviews_for_day = sum(rating_counts.values())
            
            if total_reviews_for_day > 0:
                # Среднее время для этого дня
                avg_seconds = round(total_time_for_day / total_reviews_for_day, 1)
                
                # Успешность для этого дня (рейтинги 3 и 4 = правильный ответ)
                good_easy = rating_counts.get(3, 0) + rating_counts.get(4, 0)
                success_rate = round((good_easy / total_reviews_for_day) * 100, 1)
            else:
                avg_seconds = 0
                success_rate = 0
            
            daily_stats_7d[date_str] = {
                "avg_review_seconds": avg_seconds,
                "success_rate_percent": success_rate,
                "total_reviews": total_reviews_for_day
            }
        
        return {
            # ─── ОБЩАЯ СВОДКА (ЗА ВСЁ ВРЕМЯ) ───────────────────────────
            "summary_all_time": {
                "total_study_seconds": {
                    "value": total_study_seconds,
                    "description": "Общее время изучения ВСЕХ карточек пользователя за ВСЁ ВРЕМЯ в секундах."
                },
                "total_reviews": {
                    "value": total_reviews,
                    "description": "Общее количество повторений ВСЕХ карточек пользователя за ВСЁ ВРЕМЯ."
                }
            },
        
            # ─── СРЕДНИЕ ЗА 7 ДНЕЙ (УЖЕ РАССЧИТАННЫЕ ДЛЯ СРАВНЕНИЯ) ───
            "avg_7_days": {
                "avg_review_duration_seconds": {
                    "value": avg_review_duration_7d,
                    "description": "Среднее время одного повторения за последние 7 дней в секундах (по ВСЕМ колодам).",
                },
                "avg_success_rate_percent": {
                    "value": avg_success_rate_7d,
                    "description": "Средняя успешность (процент правильных ответов) за последние 7 дней в процентах (по ВСЕМ колодам).",
                }
            },
        
            # ─── ПОВТОРЫ ПО ДНЯМ И РЕЙТИНГАМ (ЗА 7 ДНЕЙ) ──────────────
            "daily_review_by_rating_7_days": {
                "value": daily_review_by_rating_7d,
                "description": "Количество повторений по дням с разбивкой по рейтингам ответа пользователя за последние 7 дней (по ВСЕМ колодам).",
            },
        
            # ─── ВРЕМЯ РЕВЮ ПО ДНЯМ (ЗА 7 ДНЕЙ) ────────────────────────
            "daily_review_time_7_days": {
                "value": daily_review_time_7d,
                "period": "Последние 7 дней",
                "description": "Суммарное время ревью в секундах по дням за последние 7 дней (по ВСЕМ колодам). Показывает сколько времени пользователь тратил на изучение в каждый день.",
            },
        
            # ─── СРЕДНЕЕ ВРЕМЯ И УСПЕШНОСТЬ ПО ДНЯМ (ЗА 7 ДНЕЙ) ────────
            "daily_stats_7_days": {
                "value": daily_stats_7d,
                "period": "Последние 7 дней",
                "description": "Среднее время и успешность для КАЖДОГО дня отдельно (по ВСЕМ колодам). Позволяет AI видеть динамику по дням.",
                "fields": {
                    "avg_review_seconds": {
                        "description": "Среднее время одного повторения в этом дне (в секундах)",
                    },
                    "success_rate_percent": {
                        "description": "Процент правильных ответов в этом дне (рейтинги 3 и 4)",
                    },
                    "total_reviews": {
                        "description": "Общее количество повторений в этот день"
                    }
                },
            },
        
            # ─── ПРОГНОЗ ПОВТОРЕНИЙ (НА 7 ДНЕЙ ВПЕРЁД) ─────────────────
            "forecast_next_7_days": {
                "value": forecast_7d,
                "period": "Следующие 7 дней",
                "description": "Прогноз количества карточек на повтор по дням на следующие 7 дней вперёд (по ВСЕМ колодам). Показывает нагрузку на пользователя.",
                "legend": {
                    "key": "Дата в формате 'YYYY-MM-DD' когда карточки будут на повторении",
                    "value": "Количество карточек которые нужно повторить в этот день без учета добавления новых."
                },
                "interpretation": "карточки на завтра показывают повторы завтра. Но на послезавтра уже не точно тк повторы с завтра часть карточек перейдет на следующий день. для кого то норма 30 карточек для кого то 200 в зависимости от средней нагрузки повторов предыдущие дни"
            },
        
            # ─── ПРОДУКТИВНОСТЬ ПО ЧАСАМ (ЗА 30 ДНЕЙ) ───────────────────
            "hourly_productivity_30_days": {
                "value": hourly_breakdown_30d,
                "description": "Процент правильных ответов (Good + Easy) по временным диапазонам суток за последние 30 дней (по ВСЕМ колодам). Показывает продуктивность пользователя в разные часы.",
            },
        
            # ─── РАСПРЕДЕЛЕНИЕ ПО СЛОЖНОСТИ (ЗА ВСЁ ВРЕМЯ) ─────────────
            "difficulty_distribution_all_time": {
                "value": difficulty_distribution,
                "period": "Всё время",
                "description": "Распределение карточек по ВСЕМ колодам пользователя по диапазонам сложности. Difficulty — FSRS параметр от 1 до 10.",
            },
        
            # ─── РАСПРЕДЕЛЕНИЕ ПО СТАБИЛЬНОСТИ (ЗА ВСЁ ВРЕМЯ) ──────────
            "stability_distribution_all_time": {
                "value": stability_distribution,
                "period": "Всё время",
                "description": "Распределение карточек по ВСЕМ колодам пользователя по диапазонам стабильности. Stability — через сколько дней пользователь вспомнит карточку с вероятностью 90% (FSRS параметр в днях).",
                "stability_ranges": {
                    "1-25 дней": "Карточки с стабильностью 1-25 дней — недавно выученные или слабые",
                    "25-50 дней": "Карточки с стабильностью 25-50 дней — средние по надёжности",
                    "50-100 дней": "Карточки с стабильностью 50-100 дней — хорошо выученные",
                    ">100 дней": "Карточки с стабильностью >100 дней — считаются условно изученными"
                },
            },
        
            # ─── РАСПРЕДЕЛЕНИЕ ПО ТИПАМ КАРТОЧЕК (ЗА ВСЁ ВРЕМЯ) ────────
            "card_types_distribution_all_time": {
                "value": card_types_distribution,
                "period": "Всё время",
                "description": "Распределение карточек по ВСЕМ колодам пользователя по типам на основе in_learning и stability.",
                "type_legend": {
                    "new": "Новые карточки — in_learning = False (ещё не начаты и просто лежат в колоде)",
                    "in_learning": "В процессе изучения — in_learning = True и stability <= 100 ИЛИ difficulty >= 3",
                    "learned": "Изученные — in_learning = True, stability > 100 И difficulty < 3",
                    "suspended": "Отложенные — карточки которые пользователь отложил из колоды чтобы не попадали в обучение"
                },
            }
        }

        
    async def _get_deck_stats(self, deck_id: UUID, user_id: UUID) -> dict[str, Any]:
        """
        Возвращает структурированный JSON со статистикой конкретной колоды для AI-анализа.
        
        Собирает все доступные метрики для колоды:
         - Общее время изучения и количество повторов (всё время)
         - Повторения по дням и рейтингам (7 дней)
         - Время ревью по дням (7 дней)
         - Продуктивность по часам (30 дней)
         - Распределение по сложности, стабильности, типам карточек (всё время)
         - Прогноз повторений на 7 дней вперёд
         - Среднее время и успешность по дням (7 дней)
        
        Args:
            deck_id: ID колоды для которой собирается статистика
            user_id: ID владельца колоды
            
        Returns:
            dict: Структурированный JSON со всеми метриками для отправки в AI
        """
        
        # 1. Общее время изучения ЗА ВСЁ ВРЕМЯ
        total_study_seconds = await self.uow.review_logs.get_total_study_seconds(
            user_id=user_id, deck_id=deck_id
        )
        
        # 2. Общее количество повторов ЗА ВСЁ ВРЕМЯ
        total_reviews = await self.uow.review_logs.get_total_reviews_count(
            user_id=user_id, deck_id=deck_id
        )
        
        user = await self.uow.users.get_by_id(user_id)
        user_tz = user.timezone if user else "UTC"
        
        # 3. Повторения по дням и рейтингам — ЗА 7 ДНЕЙ
        daily_review_by_rating_7d = await self.uow.review_logs.get_daily_review_by_rating(
            user_id=user_id, days=7, deck_id=deck_id, timezone=user_tz
        )
        
        # 4. Время ревью по дням — ЗА 7 ДНЕЙ
        daily_review_time_7d = await self.uow.review_logs.get_daily_review_time(
            user_id=user_id, deck_id=deck_id, days=7, timezone=user_tz
        )
        
        # 5. Продуктивность по часам — ЗА 30 ДНЕЙ
        hourly_breakdown_30d = await self.uow.review_logs.get_hourly_breakdown(
            user_id=user_id, deck_id=deck_id, days=30, timezone=user_tz
        )
        
        # 6. Распределение по сложности — ЗА ВСЁ ВРЕМЯ
        difficulty_distribution = await self.uow.cards.get_difficulty_distribution(
            user_id=user_id, deck_id=deck_id
        )
        
        # 7. Распределение по стабильности — ЗА ВСЁ ВРЕМЯ
        stability_distribution = await self.uow.cards.get_stability_distribution(
            user_id=user_id, deck_id=deck_id
        )
        
        # 8. Распределение по типам карточек — ЗА ВСЁ ВРЕМЯ
        card_types_distribution = await self.uow.cards.get_card_types_distribution(
            user_id=user_id, deck_id=deck_id
        )
        
        # 9. Прогноз на 7 дней вперёд
        forecast_7d = await self.uow.cards.get_forecast_due_cards(
            user_id=user_id, deck_id=deck_id, days=7, timezone=user_tz
        )
        
        # ─── ВЫЧИСЛЕНИЕ СРЕДНИХ ЗА 7 ДНЕЙ ───
        
        # Среднее время одного повторения за 7 дней
        total_reviews_7d = sum(
            count
            for rating_counts in daily_review_by_rating_7d.values()
            for count in rating_counts.values()
        )
        total_time_7d = sum(daily_review_time_7d.values())
        avg_review_duration_7d = (
            round(total_time_7d / total_reviews_7d, 1) 
            if total_reviews_7d > 0 else 0
        )
        
        # Средняя успешность (процент правильных ответов) за 7 дней
        # Рейтинг 3 (Good) и 4 (Easy) = правильный ответ
        total_good_easy_7d = sum(
            rating_counts.get(3, 0) + rating_counts.get(4, 0)
            for rating_counts in daily_review_by_rating_7d.values()
        )
        avg_success_rate_7d = (
            round((total_good_easy_7d / total_reviews_7d) * 100, 1)
            if total_reviews_7d > 0 else 0
        )
        
        # ─── РАСЧЁТ СРЕДНЕГО ВРЕМЕНИ И УСПЕШНОСТИ ДЛЯ КАЖДОГО ДНЯ (7 ДНЕЙ) ───
        daily_stats_7d = {} 

        for date_str, rating_counts in daily_review_by_rating_7d.items():
            total_time_for_day = daily_review_time_7d.get(date_str, 0)
            total_reviews_for_day = sum(rating_counts.values())
            
            if total_reviews_for_day > 0:
                # Среднее время для этого дня
                avg_seconds = round(total_time_for_day / total_reviews_for_day, 1)
                
                # Успешность для этого дня (рейтинги 3 и 4 = правильный ответ)
                good_easy = rating_counts.get(3, 0) + rating_counts.get(4, 0)
                success_rate = round((good_easy / total_reviews_for_day) * 100, 1)
            else:
                avg_seconds = 0
                success_rate = 0
            
            daily_stats_7d[date_str] = {
                "avg_review_seconds": avg_seconds,
                "success_rate_percent": success_rate,
                "total_reviews": total_reviews_for_day
            }

        
        return {    
            # ─── ОБЩАЯ СВОДКА (ЗА ВСЁ ВРЕМЯ) ───────────────────────────
            "summary_all_time": {
                "total_study_seconds": {
                    "value": total_study_seconds,
                    "description": "Общее время изучения карточек колоды за ВСЁ ВРЕМЯ в секундах."
                },
                "total_reviews": {
                    "value": total_reviews,
                    "description": "Общее количество повторений карточек колоды за ВСЁ ВРЕМЯ."
                }
            },
        
            # ─── СРЕДНИЕ ЗА 7 ДНЕЙ (УЖЕ РАССЧИТАННЫЕ ДЛЯ СРАВНЕНИЯ) ───
            "avg_7_days": {
                "avg_review_duration_seconds": {
                    "value": avg_review_duration_7d,
                    "description": "Среднее время одного повторения за последние 7 дней в секундах.",
                },
                "avg_success_rate_percent": {
                    "value": avg_success_rate_7d,
                    "description": "Средняя успешность (процент правильных ответов) за последние 7 дней в процентах.",
                }
            },
        
            # ─── ПОВТОРЫ ПО ДНЯМ И РЕЙТИНГАМ (ЗА 7 ДНЕЙ) ──────────────
            "daily_review_by_rating_7_days": {
                "value": daily_review_by_rating_7d,
                "description": "Количество повторений по дням с разбивкой по рейтингам ответа пользователя за последние 7 дней.",
            },
        
            # ─── ВРЕМЯ РЕВЮ ПО ДНЯМ (ЗА 7 ДНЕЙ) ────────────────────────
            "daily_review_time_7_days": {
                "value": daily_review_time_7d,
                "period": "Последние 7 дней",
                "description": "Суммарное время ревью в секундах по дням за последние 7 дней. Показывает сколько времени пользователь тратил на изучение в каждый день.",
            },
            
            # ─── СРЕДНЕЕ ВРЕМЯ И УСПЕШНОСТЬ ПО ДНЯМ (ЗА 7 ДНЕЙ) ────────────────
            "daily_stats_7_days": {
                "value": daily_stats_7d,
                "period": "Последние 7 дней",
                "description": "Среднее время и успешность для КАЖДОГО дня отдельно. Позволяет AI видеть динамику по дням.",
                "fields": {
                    "avg_review_seconds": {
                        "description": "Среднее время одного повторения в этом дне (в секундах)",
                    },
                    "success_rate_percent": {
                        "description": "Процент правильных ответов в этом дне (рейтинги 3 и 4)",
                    },
                    "total_reviews": {
                        "description": "Общее количество повторений в этот день"
                    }
                },

            },

            # ─── ПРОГНОЗ ПОВТОРЕНИЙ (НА 7 ДНЕЙ ВПЕРЁД) ─────────────────
            "forecast_next_7_days": {
                "value": forecast_7d,
                "period": "Следующие 7 дней",
                "description": "Прогноз количества карточек на повтор по дням на следующие 7 дней вперёд. Показывает нагрузку на пользователя. ( и по времени используя среднее время повтора * на количество в прогнозе)",
                "legend": {
                    "key": "Дата в формате 'YYYY-MM-DD' когда карточки будут на повторении",
                    "value": "Количество карточек которые нужно повторить в этот день без учета добавления новых."
                },
                "interpretation": "карточки на завтра показывают повторы завтра. Но на послезавтра уже не точно тк повторы с завтра часть карточек перейдет на следующий день. для кого то норма 30 карточек для кого то 200 в зависимости от средней нагрузки повторов предыдущие дни",
            },
        
            # ─── ПРОДУКТИВНОСТЬ ПО ЧАСАМ (ЗА 30 ДНЕЙ) ───────────────────
            "hourly_productivity_30_days": {
                "value": hourly_breakdown_30d,
                "description": "Процент правильных ответов (Good + Easy) по временным диапазонам суток за последние 30 дней. Показывает продуктивность пользователя в разные часы.",
            },
        
            # ─── РАСПРЕДЕЛЕНИЕ ПО СЛОЖНОСТИ (ЗА ВСЁ ВРЕМЯ) ─────────────
            "difficulty_distribution_all_time": {
                "value": difficulty_distribution,
                "period": "Всё время",
                "description": "Распределение карточек в колоде по диапазонам сложности. Difficulty — FSRS параметр от 1 до 10.",
            },
        
            # ─── РАСПРЕДЕЛЕНИЕ ПО СТАБИЛЬНОСТИ (ЗА ВСЁ ВРЕМЯ) ──────────
            "stability_distribution_all_time": {
                "value": stability_distribution,
                "period": "Всё время",
                "description": "Распределение карточек по диапазонам стабильности. Stability — через сколько дней пользователь вспомнит карточку с вероятностью 90% (FSRS параметр в днях).",
                "stability_ranges": {
                    "1-25 дней": "Карточки с стабильностью 1-25 дней — недавно выученные или слабые",
                    "25-50 дней": "Карточки с стабильностью 25-50 дней — средние по надёжности",
                    "50-100 дней": "Карточки с стабильностью 50-100 дней — хорошо выученные",
                    ">100 дней": "Карточки с стабильностью >100 дней — считаются условно изученными"
                },

            },
        
            # ─── РАСПРЕДЕЛЕНИЕ ПО ТИПАМ КАРТОЧЕК (ЗА ВСЁ ВРЕМЯ) ────────
            "card_types_distribution_all_time": {
                "value": card_types_distribution,
                "period": "Всё время",
                "description": "Распределение карточек по типам на основе in_learning и stability.",
                "type_legend": {
                    "new": "Новые карточки — in_learning = False (ещё не начаты и просто лежат в колоде)",
                    "in_learning": "В процессе изучения — in_learning = True и stability <= 100 ИЛИ difficulty >= 3",
                    "learned": "Изученные — in_learning = True, stability > 100 И difficulty < 3",
                    "suspended": "Отложенные — карточки которые пользователь отложил из колоды чтобы не попадали в обучение"
                },
                "example": {
                    "new": 30,
                    "in_learning": 120,
                    "learned": 200,
                    "suspended": 10
                }
            }
        }



    MIN_REVIEWS_FOR_AI_ANALYSIS = 100

    async def execute(self, input_dto: AIAnalyzeStudyStatInput) -> AIAnalyzeStudyStatOutput:
        """
        Выполняет AI-анализ статистики обучения.
        
        Рабочий процесс:
            1. Проверяет существование пользователя (бросает UserNotFoundError если не найден)
            2. Проверяет достаточно ли всего повторов (минимум 100) для AI-анализа
               - Если меньше 100 — возвращает сообщение с количеством необходимых повторов
            3. Проверяет не выполнялся ли анализ за последние 7 дней
               - Если анализ свежий — возвращает предыдущий результат
            4. Собирает статистику (по всем колодам или по конкретной)
            5. Отправляет данные в AI-сервис
            6. При успешном ответе — сохраняет анализ в БД
            7. Возвращает результат с датой следующего доступного анализа (через 7 дней)
        
        Args:
            input_dto: Входные данные с user_id и опциональным deck_id
            
        Returns:
            AIAnalyzeStudyStatOutput с:
                 - analysis_date: дата анализа
                 - analysis_next_date: дата когда можно получить следующий анализ
                 - analysis_success: флаг успешности анализа
                 - insights, problem_areas, recommendations, goals: структурированные данные
        
        Raises:
            UserNotFoundError: Если пользователь не найден
        """
        async with self.uow:
            # 1. Проверить существование пользователя
                user = await self.uow.users.get_by_id(input_dto.user_id)
                if user is None:
                    self.logger.warning(
                         "Пользователь не найден",
                        user_id=input_dto.user_id,
                     )
                    raise UserNotFoundError(user_id=str(input_dto.user_id))
                
                user_tz = user.timezone if user else "UTC"
                now = get_current_datetime(user_tz)
                user_name = user.first_name
                
                # 2. Проверка: достаточно ли всего повторов для AI-анализа
                if input_dto.deck_id:
                    total_reviews = await self.uow.review_logs.get_total_reviews_count(
                        user_id=input_dto.user_id, deck_id=input_dto.deck_id
                    )
                    last_analyze = await self.uow.ai_analysis.get_latest_by_deck(deck_id=input_dto.deck_id)
                else:
                    total_reviews = await self.uow.review_logs.get_total_reviews_count(
                        user_id=input_dto.user_id, deck_id=None
                    )
                    last_analyze = await self.uow.ai_analysis.get_latest_by_user(user_id=input_dto.user_id)
                
                if total_reviews < self.MIN_REVIEWS_FOR_AI_ANALYSIS:
                    remaining_reviews = self.MIN_REVIEWS_FOR_AI_ANALYSIS - total_reviews
                    self.logger.warning(
                          "Недостаточно повторов для AI-анализа",
                        total_reviews=total_reviews,
                        remaining_reviews=remaining_reviews,
                      )
                    raise InsufficientReviewsError(
                        total_reviews=total_reviews,
                        remaining_reviews=remaining_reviews,
                      )
                
                stats_json = None
                previous_stats_json = None
                previous_answer = None
                previous_date = None

                if last_analyze is not None:
                    elapsed = now - last_analyze.analysis_date
                    seven_days = timedelta(days=7)
                     # Проверка: прошло ли 7 суток с последнего анализа
                    if elapsed < seven_days:
                        remaining = seven_days - elapsed
                        # Парсим JSON из БД для возврата структурированного результата
                        parsed_result = None
                        if last_analyze.analysis_text:
                            try:
                                parsed_data = json.loads(last_analyze.analysis_text)
                                parsed_result = AIStudyAnalysisResult(**parsed_data)
                            except (json.JSONDecodeError, TypeError):
                                parsed_result = None
                        
                        return AIAnalyzeStudyStatOutput(
                            analysis_date=last_analyze.analysis_date,
                            analysis_next_date=now + remaining,
                            analysis_success=True,
                            insights=parsed_result.insights if parsed_result else [],
                            problem_areas=parsed_result.problem_areas if parsed_result else [],
                            recommendations=parsed_result.recommendations if parsed_result else [],
                            goals=parsed_result.goals if parsed_result else [],
                        )
                    else:
                         # прошло 7 суток
                        previous_stats_json = last_analyze.stats_json
                        previous_answer = last_analyze.analysis_text
                        previous_date = last_analyze.analysis_date

                if input_dto.deck_id:
                    stats_json = await self._get_deck_stats(deck_id=input_dto.deck_id, user_id=input_dto.user_id)
                    
                    
                else:
                    stats_json = await self._get_user_stats(user_id=input_dto.user_id)
                    
                # собираем данные делаем ai запрос и возвращаем ответ
                # в случае успеха обновляем бд
                ai_input_dto = AnalyzeStatsInput(stats_json=stats_json,
                                                 user_name=user_name,
                                                 previous_answer=previous_answer,
                                                 previous_stats_json=previous_stats_json,
                                                 previous_date=previous_date,)
                        
                result: AnalyzeStudyStatsResult = await self.ai.analyze_study_stats(input_data=ai_input_dto)
                
                if result.status and result.result:
                    # Сериализуем structured result в JSON str для БД
                    analysis_text_json = json.dumps(result.result.model_dump())
                    
                    # Сериализуем stats_json в JSON str для БД
                    stats_json_str = json.dumps(stats_json, ensure_ascii=False)
                    
                    dto = AiAnalysisDto(
                        id=uuid.uuid4(),
                        user_id=input_dto.user_id,
                        deck_id=input_dto.deck_id,
                        analysis_date=now,
                        stats_json=stats_json_str,
                        analysis_text=analysis_text_json,
                    )
                    
                    await self.uow.ai_analysis.upsert(dto=dto)
                    await self.uow.commit()
                    
                    return AIAnalyzeStudyStatOutput(
                        analysis_date=now,
                        analysis_next_date=now + timedelta(days=7),
                        analysis_success=True,
                        insights=result.result.insights,
                        problem_areas=result.result.problem_areas,
                        recommendations=result.result.recommendations,
                        goals=result.result.goals,
                    )
                else:
                    # Парсим JSON из БД для возврата структурированного результата
                    parsed_result = None
                    if last_analyze and last_analyze.analysis_text:
                        try:
                            parsed_data = json.loads(last_analyze.analysis_text)
                            parsed_result = AIStudyAnalysisResult(**parsed_data)
                        except (json.JSONDecodeError, TypeError):
                            parsed_result = None
                    
                    return AIAnalyzeStudyStatOutput(
                        analysis_date=last_analyze.analysis_date,
                        analysis_next_date=now + timedelta(minutes=5),
                        analysis_success=False,
                        insights=parsed_result.insights if parsed_result else [],
                        problem_areas=parsed_result.problem_areas if parsed_result else [],
                        recommendations=parsed_result.recommendations if parsed_result else [],
                        goals=parsed_result.goals if parsed_result else [],
                    )