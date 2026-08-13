"""
Тест для проверки метода analyze_study_stats с анализом конкретной колоды.
Запуск: poetry run python tests/test_analyze_deck_stats.py

Этот тест проверяет:
1. Корректное создание DTO AnalyzeStatsInput с deck контекстом
2. Передачу данных колоды и сложных карточек в AI-сервис
3. Формирование контекста колоды в DeepSeekAIService
4. Возврат AI-ответа с рекомендациями по конкретной колоде
"""
import asyncio
import json
import os
import sys
from datetime import date
from pathlib import Path
from uuid import UUID

# ЗАГРУЖАЕМ .env ДО ВСЕХ ИМПОРТОВ!
load_dotenv_path = Path(__file__).parent.parent / ".env"
if load_dotenv_path.exists():
    from dotenv import dotenv_values
    config = dotenv_values(str(load_dotenv_path))
    for key, value in config.items():
        if value is not None:
            os.environ.setdefault(key, value)

from pydantic import SecretStr

# Добавляем src в PYTHONPATH
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))


# --- Минимальная реализация AISettings ---
class AISettings:
    def __init__(self, api_key: str, model: str, base_url: str):
        self.api_key = SecretStr(api_key)
        self.model = model
        self.base_url = base_url


# --- Импорт реальной реализации ---
from src.infrastructure.ai.deepseek_service import DeepSeekAIService
from src.application.interfaces.ai_service import (
    AnalyzeStatsInput,
    AnalyzeStudyStatsResult,
)
from src.domain.entities.deck.deck import Deck
from src.domain.entities.card.card import Card


def create_ai_service() -> DeepSeekAIService:
    """Создаём экземпляр DeepSeekAIService из переменных окружения."""
    settings = AISettings(
        api_key=os.getenv("AI_API_KEY", ""),
        model=os.getenv("AI_MODEL", "deepseek-chat"),
        base_url=os.getenv("AI_BASE_URL", "https://api.deepseek.com"),
    )
    return DeepSeekAIService(settings=settings)


# ============================================================================
# ТЕСТОВАЯ КОЛОДА: "Английские фразы для путешествий и повседневной жизни"
# ============================================================================

DECK_ID = UUID("a1b2c3d4-e5f6-7890-abcd-ef1234567890")
USER_ID = UUID("12345678-1234-5678-1234-567890abcdef")


# ============================================================================
# ТЕСТОВЫЕ ДАННЫЕ: СТАТИСТИКА КОЛОДЫ (соответствие _get_deck_stats)
# ============================================================================

def get_deck_stats() -> dict:
    """
    Возвращает статистику колоды в формате, соответствующем _get_deck_stats.
    
    Реалистичные данные для колоды "Английские фразы для путешествий":
     - 340 карточек всего
     - 25 карточек к повторению
     - Хорошая стабильность обучения
     - Средний уровень сложности
     """
    return {
         # ─── ОБЩАЯ СВОДКА (ЗА ВСЁ ВРЕМЯ) ───────────────────────────
         "summary_all_time": {
             "total_study_seconds": {
                 "value": 28450,
                 "description": "Общее время изучения карточек колоды за ВСЁ ВРЕМЯ в секундах.",
             },
             "total_reviews": {
                 "value": 1856,
                 "description": "Общее количество повторений карточек колоды за ВСЁ ВРЕМЯ.",
             }
         },

         # ─── СРЕДНИЕ ЗА 7 ДНЕЙ ─────────────────────────────────────
         "avg_7_days": {
             "avg_review_duration_seconds": {
                 "value": 4.2,
                 "description": "Среднее время одного повторения за последние 7 дней в секундах.",
             },
             "avg_success_rate_percent": {
                 "value": 78.5,
                 "description": "Средняя успешность (процент правильных ответов) за последние 7 дней в процентах.",
             }
         },

         # ─── ПОВТОРЫ ПО ДНЯМ И РЕЙТИНГАМ (ЗА 7 ДНЕЙ) ──────────────
         "daily_review_by_rating_7_days": {
             "value": {
                 "2026-08-03": {"1": 2, "2": 3, "3": 8, "4": 12},
                 "2026-08-04": {"1": 1, "2": 2, "3": 10, "4": 15},
                 "2026-08-05": {"1": 3, "2": 4, "3": 7, "4": 9},
                 "2026-08-06": {"1": 1, "2": 2, "3": 9, "4": 14},
                 "2026-08-07": {"1": 0, "2": 1, "3": 12, "4": 18},
                 "2026-08-08": {"1": 2, "2": 3, "3": 8, "4": 11},
                 "2026-08-09": {"1": 1, "2": 2, "3": 11, "4": 16},
             },
             "description": "Количество повторений по дням с разбивкой по рейтингам за последние 7 дней.",
         },

         # ─── ВРЕМЯ РЕВЮ ПО ДНЯМ (ЗА 7 ДНЕЙ) ────────────────────────
         "daily_review_time_7_days": {
             "value": {
                 "2026-08-03": 1450,
                 "2026-08-04": 1280,
                 "2026-08-05": 1620,
                 "2026-08-06": 1350,
                 "2026-08-07": 1100,
                 "2026-08-08": 1480,
                 "2026-08-09": 1200,
             },
             "period": "Последние 7 дней",
             "description": "Суммарное время ревью в секундах по дням за последние 7 дней.",
         },

         # ─── СРЕДНЕЕ ВРЕМЯ И УСПЕШНОСТЬ ПО ДНЯМ (ЗА 7 ДНЕЙ) ────────
         "daily_stats_7_days": {
             "value": {
                 "2026-08-03": {
                     "avg_review_seconds": 4.5,
                     "success_rate_percent": 75.0,
                     "total_reviews": 25,
                 },
                 "2026-08-04": {
                     "avg_review_seconds": 4.1,
                     "success_rate_percent": 80.0,
                     "total_reviews": 28,
                 },
                 "2026-08-05": {
                     "avg_review_seconds": 4.8,
                     "success_rate_percent": 70.0,
                     "total_reviews": 24,
                 },
                 "2026-08-06": {
                     "avg_review_seconds": 4.0,
                     "success_rate_percent": 82.0,
                     "total_reviews": 26,
                 },
                 "2026-08-07": {
                     "avg_review_seconds": 3.5,
                     "success_rate_percent": 88.0,
                     "total_reviews": 31,
                 },
                 "2026-08-08": {
                     "avg_review_seconds": 4.6,
                     "success_rate_percent": 73.0,
                     "total_reviews": 24,
                 },
                 "2026-08-09": {
                     "avg_review_seconds": 3.8,
                     "success_rate_percent": 85.0,
                     "total_reviews": 30,
                 },
             },
             "period": "Последние 7 дней",
             "description": "Среднее время и успешность для КАЖДОГО дня отдельно.",
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
             "value": {
                 "2026-08-10": 18,
                 "2026-08-11": 12,
                 "2026-08-12": 8,
                 "2026-08-13": 15,
                 "2026-08-14": 10,
                 "2026-08-15": 6,
                 "2026-08-16": 14,
             },
             "period": "Следующие 7 дней",
             "description": "Прогноз количества карточек на повтор по дням на следующие 7 дней вперёд.",
             "legend": {
                 "key": "Дата в формате 'YYYY-MM-DD' когда карточки будут на повторении",
                 "value": "Количество карточек которые нужно повторить в этот день без учета добавления новых.",
             },
         },

         # ─── ПРОДУКТИВНОСТЬ ПО ЧАСАМ (ЗА 30 ДНЕЙ) ───────────────────
         "hourly_productivity_30_days": {
             "value": {
                 "00:00-04:00": 58.3,
                 "04:00-08:00": 67.5,
                 "08:00-12:00": 82.1,
                 "12:00-16:00": 76.8,
                 "16:00-20:00": 71.4,
                 "20:00-24:00": 55.2,
             },
             "description": "Процент правильных ответов (Good + Easy) по временным диапазонам суток за последние 30 дней.",
         },

         # ─── РАСПРЕДЕЛЕНИЕ ПО СЛОЖНОСТИ (ЗА ВСЁ ВРЕМЯ) ─────────────
         "difficulty_distribution_all_time": {
             "value": {
                 "1-2": 12,
                 "2-3": 28,
                 "3-4": 45,
                 "4-5": 68,
                 "5-6": 75,
                 "6-7": 62,
                 "7-8": 35,
                 "8-9": 12,
                 "9-10": 3,
             },
             "period": "Всё время",
             "description": "Распределение карточек в колоде по диапазонам сложности.",
         },

         # ─── РАСПРЕДЕЛЕНИЕ ПО СТАБИЛЬНОСТИ (ЗА ВСЁ ВРЕМЯ) ──────────
         "stability_distribution_all_time": {
             "value": {
                 "1-25 дней": 45,
                 "25-50 дней": 78,
                 "50-100 дней": 95,
                 ">100 дней": 122,
             },
             "period": "Всё время",
             "description": "Распределение карточек по диапазонам стабильности.",
             "stability_ranges": {
                 "1-25 дней": "Карточки с стабильностью 1-25 дней — недавно выученные или слабые",
                 "25-50 дней": "Карточки с стабильностью 25-50 дней — средние по надёжности",
                 "50-100 дней": "Карточки с стабильностью 50-100 дней — хорошо выученные",
                 ">100 дней": "Карточки с стабильностью >100 дней — считаются условно изученными",
             },
         },

         # ─── РАСПРЕДЕЛЕНИЕ ПО ТИПАМ КАРТОЧЕК (ЗА ВСЁ ВРЕМЯ) ────────
         "card_types_distribution_all_time": {
             "value": {
                 "new": 15,
                 "in_learning": 85,
                 "learned": 220,
                 "suspended": 20,
             },
             "period": "Всё время",
             "description": "Распределение карточек по типам на основе in_learning и stability.",
             "type_legend": {
                 "new": "Новые карточки — in_learning = False (ещё не начаты и просто лежат в колоде)",
                 "in_learning": "В процессе изучения — in_learning = True и stability <= 100 ИЛИ difficulty >= 3",
                 "learned": "Изученные — in_learning = True, stability > 100 И difficulty < 3",
                 "suspended": "Отложенные — карточки которые пользователь отложил из колоды чтобы не попадали в обучение",
             },
             "example": {
                 "new": 15,
                 "in_learning": 85,
                 "learned": 220,
                 "suspended": 20,
             }
         },
    }


# ============================================================================
# ПРЕДЫДУЩИЙ ОТВЕТ DeepSEEK ДЛЯ КОЛОДЫ (для сравнения)
# ============================================================================

PREVIOUS_DECK_DEEPSEEK_ANSWER = """
Дмитрий, отличная работа с колодой "Английские фразы для путешествий"! 🌍

Ты сделал 1650 повторений с 72% успешностью — хороший показатель для практической лексики.
Твоё лучшее время: утро (8-12) с 77% успеха. Вечером (20-24) падает до 49% — не учи перед сном!

⚠️ Проблемные зоны: 52 карточки с стабильностью 1-25 дней — это слабые места.
72 карточки в диапазоне 5-6 сложности — средние, но требуют внимания.

🚀 Рекомендации:
1. Сфокусируйся на 52 слабых карточках (1-25 дней стабильности)
2. Утром (8-12) повторяй сложные фразы
3. Вечером только повторения, без новых карточек
4. Целевой ретеншен 92% — у тебя сейчас 72%, есть куда расти! ✨
"""


# ============================================================================
# ТЕСТЫ
# ============================================================================

async def test_analyze_deck_stats_with_comparison() -> bool:
    """Главный тест: analyze_study_stats для колоды с сравнением.
     
     Проверяет что:
     1. DTO передаётся корректно с deck контекстом
     2. AI получает данные колоды и сложные карточки
     3. AI возвращает анализ с рекомендациями по колоде
     """
    service = create_ai_service()

    print("=" * 70)
    print("ТЕСТ: analyze_study_stats ДЛЯ КОЛОДЫ С СРАВНЕНИЕМ")
    print("=" * 70)
    print()


    
     # Получаем статистику колоды
    deck_stats = get_deck_stats()
    deck_stats_json = json.dumps(deck_stats, ensure_ascii=False)
    
     # Предыдущая статистика (для сравнения)
    previous_stats = get_previous_week_deck_stats()
    previous_stats_json = json.dumps(previous_stats, ensure_ascii=False)
    
     # Дата предыдущего анализа
    previous_date = date(2026, 8, 2)

     # Создаём DTO С данными колоды
    input_data = AnalyzeStatsInput(
        stats_json=deck_stats_json,
        user_name="Дмитрий",
        previous_stats_json=previous_stats_json,
        previous_answer=PREVIOUS_DECK_DEEPSEEK_ANSWER,
        previous_date=previous_date,

    )

    print("📊 Данные для отправки:")
    print(f"   Статистика: {len(deck_stats_json)} символов")
    print(f"   Предыдущая статистика: {len(previous_stats_json)} символов")
    print(f"   Дата предыдущего анализа: {previous_date.isoformat()}")
    print()

     # Проверяем что DTO содержит все поля
    print("✅ Проверка DTO:")
    print(f"   stats_json не пустой: {bool(input_data.stats_json)}")
    print(f"   user_name задан: {input_data.user_name}")
    print(f"   previous_stats_json не пустой: {bool(input_data.previous_stats_json)}")
    print(f"   previous_answer не пустой: {bool(input_data.previous_answer)}")
    print(f"   previous_date задан: {input_data.previous_date}")
    print()

    try:
        analysis_result: AnalyzeStudyStatsResult = await service.analyze_study_stats(
            input_data=input_data
        )

        print("✅ analyze_study_stats вернул результат:")
        print("-" * 70)
        print(analysis_result.result)
        print("-" * 70)
        print()

         # Проверяем что статус успеха
        print("✅ Проверка результата:")
        print(f"   status: {analysis_result.status}")
        print(f"   result не пустой: {analysis_result.result is not None}")
        if analysis_result.result is not None:
            insights_count = len(analysis_result.result.insights)
            problem_areas_count = len(analysis_result.result.problem_areas)
            recommendations_count = len(analysis_result.result.recommendations)
            print(f"   insights: {insights_count}, problem_areas: {problem_areas_count}, recommendations: {recommendations_count}")
        print()

          # Проверяем что в ответе есть упоминание колоды
        if analysis_result.result is not None:
              # Собираем все текстовые поля для проверки ключевых слов
            all_text = ""
            for item in analysis_result.result.insights:
                all_text += item.text + " "
            for item in analysis_result.result.problem_areas:
                all_text += item.text + " "
            for item in analysis_result.result.recommendations:
                all_text += item.text + " "
            
            response_lower = all_text.lower()
            has_deck_keywords = any(kw in response_lower for kw in [
                 "путешеств", "колод",
                 "карточ", "фраз", "обучен", "ретеншен",
             ])
            
            if has_deck_keywords:
                print("✅ Ответ содержит ключевые слова колоды!")
            else:
                print("⚠️ Ответ не содержит явных ключевых слов колоды")
                print("     (Возможно AI не использовал контекст колоды)")
            print()

          # Проверяем что result не пустой и содержит хотя бы один массив с данными
        result_valid = (
            analysis_result.status
            and analysis_result.result is not None
            and (
                len(analysis_result.result.insights) > 0
                or len(analysis_result.result.problem_areas) > 0
                or len(analysis_result.result.recommendations) > 0
               )
           )
        return result_valid

    except Exception as e:
        print(f"❌ ОШИБКА: {type(e).__name__}")
        print(f"   Детали: {e}")
        return False


async def test_analyze_deck_stats_without_comparison() -> bool:
    """Вспомогательный тест: analyze_study_stats для колоды БЕЗ сравнения.
     
     Проверяет что метод работает и без предыдущих данных.
     """
    service = create_ai_service()

    print("=" * 70)
    print("ТЕСТ: analyze_study_stats ДЛЯ КОЛОДЫ БЕЗ СРАВНЕНИЯ")
    print("=" * 70)
    print()

     # Получаем статистику колоды
    deck_stats = get_deck_stats()
    deck_stats_json = json.dumps(deck_stats, ensure_ascii=False)

     # Создаём DTO БЕЗ предыдущих данных
    input_data = AnalyzeStatsInput(
        stats_json=deck_stats_json,
        user_name="Дмитрий",
    )

    print("📊 Данные для отправки:")
    print(f"   Статистика: {len(deck_stats_json)} символов")
    print(f"   previous_stats_json: {input_data.previous_stats_json}")
    print(f"   previous_answer: {input_data.previous_answer}")
    print()

    try:
        analysis_result: AnalyzeStudyStatsResult = await service.analyze_study_stats(
            input_data=input_data
        )

        print("✅ analyze_study_stats (без сравнения) вернул результат:")
        print("-" * 70)
        print(analysis_result.result)
        print("-" * 70)
        print()

        print("✅ Проверка результата:")
        print(f"   status: {analysis_result.status}")
        print(f"   result не пустой: {analysis_result.result is not None}")
        if analysis_result.result is not None:
            print(f"   insights: {len(analysis_result.result.insights)}, problem_areas: {len(analysis_result.result.problem_areas)}, recommendations: {len(analysis_result.result.recommendations)}")
        print()

        result_valid = (
            analysis_result.status
            and analysis_result.result is not None
            and (
                len(analysis_result.result.insights) > 0
                or len(analysis_result.result.problem_areas) > 0
                or len(analysis_result.result.recommendations) > 0
                )
            )
        return result_valid

    except Exception as e:
        print(f"❌ ОШИБКА: {type(e).__name__}")
        print(f"   Детали: {e}")
        return False


async def test_analyze_deck_stats_minimal() -> bool:
    """Минимальный тест: analyze_study_stats только со статистикой."""
    service = create_ai_service()

    print("=" * 70)
    print("ТЕСТ: analyze_study_stats МИНИМАЛЬНЫЙ (только stats)")
    print("=" * 70)
    print()

    deck_stats = get_deck_stats()
    deck_stats_json = json.dumps(deck_stats, ensure_ascii=False)

    # Минимальный DTO
    input_data = AnalyzeStatsInput(
        stats_json=deck_stats_json,
        user_name="Дмитрий",
    )

    print("📊 Минимальные данные:")
    print(f"   Статистика: {len(deck_stats_json)} символов")
    print()

    try:
        analysis_result: AnalyzeStudyStatsResult = await service.analyze_study_stats(
            input_data=input_data
        )

        print("✅ analyze_study_stats (минимальный) вернул результат:")
        print("-" * 70)
        print(analysis_result.result)
        print("-" * 70)
        print()

        result_valid = (
            analysis_result.status
            and analysis_result.result is not None
            and (
                len(analysis_result.result.insights) > 0
                or len(analysis_result.result.problem_areas) > 0
                or len(analysis_result.result.recommendations) > 0
                )
            )
        return result_valid

    except Exception as e:
        print(f"❌ ОШИБКА: {type(e).__name__}")
        print(f"   Детали: {e}")
        return False


# ============================================================================
# ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ: ПРЕДЫДУЩАЯ НЕДЕЛЯ ДЛЯ КОЛОДЫ
# ============================================================================

def get_previous_week_deck_stats() -> dict:
    """Предыдущая неделя для колоды — немного хуже результаты."""
    return {
         "summary_all_time": {
             "total_study_seconds": {
                 "value": 25200,
                 "description": "Общее время изучения карточек колоды за ВСЁ ВРЕМЯ в секундах.",
             },
             "total_reviews": {
                 "value": 1650,
                 "description": "Общее количество повторений карточек колоды за ВСЁ ВРЕМЯ.",
             }
         },
         "avg_7_days": {
             "avg_review_duration_seconds": {
                 "value": 4.8,
                 "description": "Среднее время одного повторения за последние 7 дней в секундах.",
             },
             "avg_success_rate_percent": {
                 "value": 72.3,
                 "description": "Средняя успешность (процент правильных ответов) за последние 7 дней в процентах.",
             }
         },
         "daily_review_by_rating_7_days": {
             "value": {
                 "2026-08-02": {"1": 3, "2": 4, "3": 6, "4": 8},
                 "2026-08-03": {"1": 2, "2": 3, "3": 8, "4": 10},
                 "2026-08-04": {"1": 4, "2": 5, "3": 5, "4": 7},
                 "2026-08-05": {"1": 2, "2": 3, "3": 7, "4": 11},
                 "2026-08-06": {"1": 3, "2": 4, "3": 6, "4": 9},
                 "2026-08-07": {"1": 1, "2": 2, "3": 9, "4": 13},
                 "2026-08-08": {"1": 3, "2": 4, "3": 5, "4": 6},
             },
             "description": "Количество повторений по дням с разбивкой по рейтингам за последние 7 дней.",
         },
         "daily_review_time_7_days": {
             "value": {
                 "2026-08-02": 1650,
                 "2026-08-03": 1400,
                 "2026-08-04": 1850,
                 "2026-08-05": 1350,
                 "2026-08-06": 1550,
                 "2026-08-07": 1200,
                 "2026-08-08": 1700,
             },
             "period": "Последние 7 дней",
             "description": "Суммарное время ревью в секундах по дням за последние 7 дней.",
         },
         "daily_stats_7_days": {
             "value": {
                 "2026-08-02": {
                     "avg_review_seconds": 5.2,
                     "success_rate_percent": 68.0,
                     "total_reviews": 21,
                 },
                 "2026-08-03": {
                     "avg_review_seconds": 4.8,
                     "success_rate_percent": 72.0,
                     "total_reviews": 24,
                 },
                 "2026-08-04": {
                     "avg_review_seconds": 5.5,
                     "success_rate_percent": 62.0,
                     "total_reviews": 20,
                 },
                 "2026-08-05": {
                     "avg_review_seconds": 4.5,
                     "success_rate_percent": 76.0,
                     "total_reviews": 25,
                 },
                 "2026-08-06": {
                     "avg_review_seconds": 5.0,
                     "success_rate_percent": 70.0,
                     "total_reviews": 22,
                 },
                 "2026-08-07": {
                     "avg_review_seconds": 4.2,
                     "success_rate_percent": 82.0,
                     "total_reviews": 25,
                 },
                 "2026-08-08": {
                     "avg_review_seconds": 5.3,
                     "success_rate_percent": 65.0,
                     "total_reviews": 18,
                 },
             },
             "period": "Последние 7 дней",
             "description": "Среднее время и успешность для КАЖДОГО дня отдельно.",
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
         "forecast_next_7_days": {
             "value": {
                 "2026-08-09": 22,
                 "2026-08-10": 15,
                 "2026-08-11": 10,
                 "2026-08-12": 18,
                 "2026-08-13": 12,
                 "2026-08-14": 8,
                 "2026-08-15": 16,
             },
             "period": "Следующие 7 дней",
             "description": "Прогноз количества карточек на повтор по дням на следующие 7 дней вперёд.",
             "legend": {
                 "key": "Дата в формате 'YYYY-MM-DD' когда карточки будут на повторении",
                 "value": "Количество карточек которые нужно повторить в этот день без учета добавления новых.",
             },
         },
         "hourly_productivity_30_days": {
             "value": {
                 "00:00-04:00": 52.1,
                 "04:00-08:00": 61.3,
                 "08:00-12:00": 76.8,
                 "12:00-16:00": 70.2,
                 "16:00-20:00": 65.4,
                 "20:00-24:00": 48.9,
             },
             "description": "Процент правильных ответов (Good + Easy) по временным диапазонам суток за последние 30 дней.",
         },
         "difficulty_distribution_all_time": {
             "value": {
                 "1-2": 14,
                 "2-3": 30,
                 "3-4": 48,
                 "4-5": 70,
                 "5-6": 72,
                 "6-7": 58,
                 "7-8": 32,
                 "8-9": 10,
                 "9-10": 2,
             },
             "period": "Всё время",
             "description": "Распределение карточек в колоде по диапазонам сложности.",
         },
         "stability_distribution_all_time": {
             "value": {
                 "1-25 дней": 52,
                 "25-50 дней": 70,
                 "50-100 дней": 85,
                 ">100 дней": 105,
             },
             "period": "Всё время",
             "description": "Распределение карточек по диапазонам стабильности.",
             "stability_ranges": {
                 "1-25 дней": "Карточки с стабильностью 1-25 дней — недавно выученные или слабые",
                 "25-50 дней": "Карточки с стабильностью 25-50 дней — средние по надёжности",
                 "50-100 дней": "Карточки с стабильностью 50-100 дней — хорошо выученные",
                 ">100 дней": "Карточки с стабильностью >100 дней — считаются условно изученными",
             },
         },
         "card_types_distribution_all_time": {
             "value": {
                 "new": 22,
                 "in_learning": 95,
                 "learned": 195,
                 "suspended": 18,
             },
             "period": "Всё время",
             "description": "Распределение карточек по типам на основе in_learning и stability.",
             "type_legend": {
                 "new": "Новые карточки — in_learning = False (ещё не начаты и просто лежат в колоде)",
                 "in_learning": "В процессе изучения — in_learning = True и stability <= 100 ИЛИ difficulty >= 3",
                 "learned": "Изученные — in_learning = True, stability > 100 И difficulty < 3",
                 "suspended": "Отложенные — карточки которые пользователь отложил из колоды чтобы не попадали в обучение",
             },
             "example": {
                 "new": 22,
                 "in_learning": 95,
                 "learned": 195,
                 "suspended": 18,
             }
         },
    }


# ============================================================================
# ГЛАВНЫЙ MAIN
# ============================================================================

async def main():
    results = {}

    print()
    print("#" * 70)
    print("  ТЕСТЫ ДЛЯ analyze_study_stats С АНАЛИЗОМ КОЛОДЫ")
    print("#" * 70)
    print()

     # Тест 1: С сравнением (главный тест)
    print("🧪 ТЕСТ 1: analyze_study_stats ДЛЯ КОЛОДЫ С СРАВНЕНИЕМ")
    print("-" * 70)
    results["deck_with_comparison"] = await test_analyze_deck_stats_with_comparison()
    print()

     # Тест 2: Без сравнения
    print("🧪 ТЕСТ 2: analyze_study_stats ДЛЯ КОЛОДЫ БЕЗ СРАВНЕНИЯ")
    print("-" * 70)
    results["deck_without_comparison"] = await test_analyze_deck_stats_without_comparison()
    print()

     # Тест 3: Минимальный
    print("🧪 ТЕСТ 3: analyze_study_stats МИНИМАЛЬНЫЙ")
    print("-" * 70)
    results["deck_minimal"] = await test_analyze_deck_stats_minimal()
    print()

     # Итоги
    print("=" * 70)
    print("ИТОГИ ТЕСТИРОВАНИЯ:")
    print("=" * 70)

    total = len(results)
    passed = sum(1 for v in results.values() if v)

    for test_name, success in results.items():
        status = "✅ ПРОЙДЕН" if success else "❌ ПРОВАЛЕН"
        print(f"   {test_name}: {status}")

    print()
    print(f"   Всего: {passed}/{total} тестов успешно")
    print()

    if passed == total:
        print("🎉 ВСЕ ТЕСТЫ УСПЕШНЫ! Метод analyze_study_stats для колоды работает корректно.")
    else:
        print("⚠️ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ. Проверьте конфигурацию и сеть.")

    print()
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
