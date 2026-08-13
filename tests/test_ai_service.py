"""
Тест для проверки работы DeepSeek AI сервиса через реальную реализацию.
Запуск: poetry run python tests/test_ai_service.py
"""
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Optional

# ЗАГРУЖАЕМ .env ДО ВСЕХ ИМПОРТОВ!
load_dotenv_path = Path(__file__).parent.parent / ".env"
if load_dotenv_path.exists():
    from dotenv import dotenv_values
    config = dotenv_values(str(load_dotenv_path))
    for key, value in config.items():
        if value is not None:
            os.environ.setdefault(key, value)

from pydantic import SecretStr
import httpx

# Добавляем src в PYTHONPATH
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

# --- Минимальная реализация AISettings без загрузки всего модуля settings ---
class AISettings:
    def __init__(self, api_key: str, model: str, base_url: str):
        self.api_key = SecretStr(api_key)
        self.model = model
        self.base_url = base_url


# --- Импорт реальной реализации ---
from src.infrastructure.ai.deepseek_service import DeepSeekAIService
from src.application.interfaces.ai_service import ModerationResult


def create_ai_service() -> DeepSeekAIService:
    """Создаём экземпляр DeepSeekAIService из переменных окружения."""
    settings = AISettings(
        api_key=os.getenv("AI_API_KEY", ""),
        model=os.getenv("AI_MODEL", "deepseek-chat"),
        base_url=os.getenv("AI_BASE_URL", "https://api.deepseek.com"),
    )
    return DeepSeekAIService(settings=settings)


async def test_http_direct() -> bool:
    """Тест: прямой HTTP запрос к API (без использования класса) для диагностики."""
    api_key = os.getenv("AI_API_KEY")
    base_url = os.getenv("AI_BASE_URL", "https://api.deepseek.com")
    model = os.getenv("AI_MODEL", "deepseek-chat")

    if not api_key:
        print("❌ AI_API_KEY не найден в .env")
        return False

    print(f"📡 Прямой HTTP запрос к {base_url}")
    print(f"   Model: {model}")
    print()

    try:
        async with httpx.AsyncClient(
            base_url=base_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
              },
            timeout=30.0,
        ) as client:
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Say OK if you can hear me."},
                 ],
                "max_tokens": 50,
                "temperature": 0.7,
              }

            response = await client.post("/chat/completions", json=payload)
            response.raise_for_status()
            
            
            data = response.json()

            content = data["choices"][0]["message"]["content"].strip()
            print(f"✅ HTTP ответ получен: {content}")
            return True

    except Exception as e:
        print(f"❌ HTTP ОШИБКА: {type(e).__name__}")
        print(f"   Детали: {e}")
        return False


async def test_deepseek_service_basic() -> bool:
    """Тест: базовый вызов moderate_public_deck с корректным контентом."""
    service = create_ai_service()

    print(f"📦 Создаём DeepSeekAIService:")
    print(f"   Model: {service.settings.model}")
    print(f"   Base URL: {service.settings.base_url}")
    print()

    try:
        result = await service.moderate_public_deck(
            deck_name="English Vocabulary Basics",
            deck_description="Basic English words for beginners",
            user_name="John Doe",
            user_bio="Language learner",
            sample_cards=[
                ("Apple", "A round fruit that is red or green"),
                ("Book", "Written or printed pages bound together"),
                ("Cat", "A small domesticated carnivorous mammal"),
            ],
          )

        print("✅ moderate_public_deck вернул результат:")
        print(f"   approved: {result.approved}")
        print(f"   reason: {result.reason}")
        print(f"   severity: {result.severity}")
        print()
        return result.approved is True

    except Exception as e:
        print(f"❌ ОШИБКА: {type(e).__name__}")
        print(f"   Детали: {e}")
        return False


async def test_deepseek_service_invalid_content() -> bool:
    """Тест: moderate_public_deck с некорректным контентом (должен отклонить)."""
    service = create_ai_service()

    print("📦 Тест с некорректным контентом (ожидаем отклонение):")
    print()

    try:
        result = await service.moderate_public_deck(
            deck_name="Bad Content Deck",
            deck_description="Some inappropriate stuff",
            user_name="Test User",
            user_bio=None,
            sample_cards=[
                ("Test", "Lorem ipsum dolor sit amet"),
                ("Card2", "Some meaningless gibberish xxx yyy zzz"),
             ],
          )

        print("✅ moderate_public_deck вернул результат:")
        print(f"   approved: {result.approved}")
        print(f"   reason: {result.reason}")
        print(f"   severity: {result.severity}")
        print()
        return True

    except Exception as e:
        print(f"❌ ОШИБКА: {type(e).__name__}")
        print(f"   Детали: {e}")
        return False


async def test_deepseek_service_russian() -> bool:
    """Тест: moderate_public_deck с русскоязычным контентом."""
    service = create_ai_service()

    print("📦 Тест с русскоязычным контентом:")
    print()

    try:
        result = await service.moderate_public_deck(
            deck_name="Английские слова для начинающих",
            deck_description="Базовые английские слова и выражения",
            user_name="Иван Иванов",
            user_bio="Изучаю иностранные языки",
            sample_cards=[
                ("Apple", "Круглый фрукт красного или зелёного цвета"),
                ("Book", "Книга - набор страниц с текстом"),
                ("Cat", "Кошка - домашнее животное"),
              ],
          )

        print("✅ moderate_public_deck вернул результат:")
        print(f"   approved: {result.approved}")
        print(f"   reason: {result.reason}")
        print(f"   severity: {result.severity}")
        print()
        return True

    except Exception as e:
        print(f"❌ ОШИБКА: {type(e).__name__}")
        print(f"   Детали: {e}")
        return False


async def test_deepseek_service_empty_cards() -> bool:
    """Тест: moderate_public_deck с пустым списком карточек."""
    service = create_ai_service()

    print("📦 Тест с пустым списком карточек:")
    print()

    try:
        result = await service.moderate_public_deck(
            deck_name="Test Deck",
            deck_description="Test description",
            user_name="Test User",
            user_bio=None,
            sample_cards=[],
          )

        print("✅ moderate_public_deck вернул результат:")
        print(f"   approved: {result.approved}")
        print(f"   reason: {result.reason}")
        print(f"   severity: {result.severity}")
        print()
        return True

    except Exception as e:
        print(f"❌ ОШИБКА: {type(e).__name__}")
        print(f"   Детали: {e}")
        return False


import json

async def test_deepseek_service_analyze_stats() -> bool:
    """Тест: базовый вызов analyze_study_stats с реальной структурой метрик."""
    service = create_ai_service()

    print(f"📦 Создаём DeepSeekAIService для анализа статистики:")
    print(f"   Model: {service.settings.model}")
    print(f"   Base URL: {service.settings.base_url}")
    print()

    # Формируем тестовые данные на основе вашего model_config
    mock_stats = {
     "one_time_metrics": {
         "total_study_seconds": 45630,
         "total_reviews": 1234,
         "в среднем времени на карточку при повторе": f"{45630 // 1234} секунд"
     },
    "forecast": {
        "points": [
            {"date": "2026-08-06", "count": 12},
            {"date": "2026-08-07", "count": 8},
            {"date": "2026-08-08", "count": 15},
            {"date": "2026-08-09", "count": 6},
            {"date": "2026-08-10", "count": 10},
            {"date": "2026-08-11", "count": 14},
            {"date": "2026-08-12", "count": 9},
            {"date": "2026-08-13", "count": 7},
            {"date": "2026-08-14", "count": 11},
            {"date": "2026-08-15", "count": 13},
            {"date": "2026-08-16", "count": 5},
            {"date": "2026-08-17", "count": 8},
            {"date": "2026-08-18", "count": 16},
            {"date": "2026-08-19", "count": 7},
            {"date": "2026-08-20", "count": 10},
            {"date": "2026-08-21", "count": 6},
            {"date": "2026-08-22", "count": 9},
            {"date": "2026-08-23", "count": 12},
            {"date": "2026-08-24", "count": 8},
            {"date": "2026-08-25", "count": 11},
            {"date": "2026-08-26", "count": 14},
            {"date": "2026-08-27", "count": 7},
            {"date": "2026-08-28", "count": 10},
            {"date": "2026-08-29", "count": 6},
            {"date": "2026-08-30", "count": 9},
            {"date": "2026-08-31", "count": 13},
            {"date": "2026-09-01", "count": 8},
            {"date": "2026-09-02", "count": 11},
            {"date": "2026-09-03", "count": 7},
            {"date": "2026-09-04", "count": 10}
        ]
    },
    "review_count": {
        "points": [
            {"date": "2026-07-07", "forgotten": 3, "hard": 2, "good": 8, "easy": 5},
            {"date": "2026-07-08", "forgotten": 1, "hard": 3, "good": 10, "easy": 7},
            {"date": "2026-07-09", "forgotten": 5, "hard": 4, "good": 6, "easy": 3},
            {"date": "2026-07-10", "forgotten": 2, "hard": 1, "good": 12, "easy": 8},
            {"date": "2026-07-11", "forgotten": 4, "hard": 3, "good": 7, "easy": 4},
            {"date": "2026-07-12", "forgotten": 0, "hard": 2, "good": 15, "easy": 10},
            {"date": "2026-07-13", "forgotten": 6, "hard": 5, "good": 4, "easy": 2},
            {"date": "2026-07-14", "forgotten": 2, "hard": 2, "good": 9, "easy": 6},
            {"date": "2026-07-15", "forgotten": 3, "hard": 1, "good": 11, "easy": 8},
            {"date": "2026-07-16", "forgotten": 1, "hard": 3, "good": 8, "easy": 5},
            {"date": "2026-07-17", "forgotten": 4, "hard": 2, "good": 10, "easy": 7},
            {"date": "2026-07-18", "forgotten": 2, "hard": 4, "good": 6, "easy": 3},
            {"date": "2026-07-19", "forgotten": 0, "hard": 1, "good": 14, "easy": 9},
            {"date": "2026-07-20", "forgotten": 5, "hard": 3, "good": 5, "easy": 2},
            {"date": "2026-07-21", "forgotten": 3, "hard": 2, "good": 9, "easy": 6},
            {"date": "2026-07-22", "forgotten": 1, "hard": 1, "good": 12, "easy": 8},
            {"date": "2026-07-23", "forgotten": 4, "hard": 4, "good": 6, "easy": 3},
            {"date": "2026-07-24", "forgotten": 2, "hard": 2, "good": 10, "easy": 7},
            {"date": "2026-07-25", "forgotten": 0, "hard": 3, "good": 13, "easy": 9},
            {"date": "2026-07-26", "forgotten": 3, "hard": 1, "good": 8, "easy": 5},
            {"date": "2026-07-27", "forgotten": 5, "hard": 3, "good": 5, "easy": 2},
            {"date": "2026-07-28", "forgotten": 1, "hard": 2, "good": 11, "easy": 7},
            {"date": "2026-07-29", "forgotten": 2, "hard": 4, "good": 7, "easy": 4},
            {"date": "2026-07-30", "forgotten": 4, "hard": 2, "good": 9, "easy": 6},
            {"date": "2026-07-31", "forgotten": 0, "hard": 1, "good": 14, "easy": 10},
            {"date": "2026-08-01", "forgotten": 3, "hard": 3, "good": 8, "easy": 5},
            {"date": "2026-08-02", "forgotten": 2, "hard": 1, "good": 10, "easy": 7},
            {"date": "2026-08-03", "forgotten": 5, "hard": 4, "good": 5, "easy": 3},
            {"date": "2026-08-04", "forgotten": 1, "hard": 2, "good": 12, "easy": 8},
            {"date": "2026-08-05", "forgotten": 3, "hard": 2, "good": 9, "easy": 6}
        ]
    },
    "review_time": {
        "points": [
            {"date": "2026-07-07", "seconds": 1200},
            {"date": "2026-07-08", "seconds": 1500},
            {"date": "2026-07-09", "seconds": 1800},
            {"date": "2026-07-10", "seconds": 900},
            {"date": "2026-07-11", "seconds": 1350},
            {"date": "2026-07-12", "seconds": 1680},
            {"date": "2026-07-13", "seconds": 2100},
            {"date": "2026-07-14", "seconds": 1100},
            {"date": "2026-07-15", "seconds": 1400},
            {"date": "2026-07-16", "seconds": 1250},
            {"date": "2026-07-17", "seconds": 1550},
            {"date": "2026-07-18", "seconds": 980},
            {"date": "2026-07-19", "seconds": 1300},
            {"date": "2026-07-20", "seconds": 1900},
            {"date": "2026-07-21", "seconds": 1150},
            {"date": "2026-07-22", "seconds": 1450},
            {"date": "2026-07-23", "seconds": 1700},
            {"date": "2026-07-24", "seconds": 1200},
            {"date": "2026-07-25", "seconds": 1600},
            {"date": "2026-07-26", "seconds": 1050},
            {"date": "2026-07-27", "seconds": 1850},
            {"date": "2026-07-28", "seconds": 1350},
            {"date": "2026-07-29", "seconds": 1100},
            {"date": "2026-07-30", "seconds": 1500},
            {"date": "2026-07-31", "seconds": 1750},
            {"date": "2026-08-01", "seconds": 1250},
            {"date": "2026-08-02", "seconds": 1400},
            {"date": "2026-08-03", "seconds": 1950},
            {"date": "2026-08-04", "seconds": 1150},
            {"date": "2026-08-05", "seconds": 1300}
        ]
    },
    "hourly_breakdown": {
        "points": [
            {"hour_range": "00:00-04:00", "percentage": 55.3},
            {"hour_range": "04:00-08:00", "percentage": 68.7},
            {"hour_range": "08:00-12:00", "percentage": 85.2},
            {"hour_range": "12:00-16:00", "percentage": 78.9},
            {"hour_range": "16:00-20:00", "percentage": 72.1},
            {"hour_range": "20:00-24:00", "percentage": 61.5}
        ]
    },
    "difficulty_distribution": {
        "points": [
            {"range_label": "1-2", "count": 5},
            {"range_label": "2-3", "count": 12},
            {"range_label": "3-4", "count": 25},
            {"range_label": "4-5", "count": 38},
            {"range_label": "5-6", "count": 42},
            {"range_label": "6-7", "count": 35},
            {"range_label": "7-8", "count": 22},
            {"range_label": "8-9", "count": 10},
            {"range_label": "9-10", "count": 3}
        ]
    },
    "stability_distribution": {
        "points": [
            {"range_label": "1-25 дней", "count": 15},
            {"range_label": "25-50 дней", "count": 30},
            {"range_label": "50-100 дней", "count": 45},
            {"range_label": ">100 дней", "count": 60}
        ]
    },
    "card_types": {
        "points": [
            {"card_type": "новые", "count": 500},
            {"card_type": "изучаемые", "count": 45},
            {"card_type": "изученные", "count": 50},
            {"card_type": "отложенные", "count": 5}
        ]
    }
}

    # Переводим словарь в JSON-строку для отправки в метод
    stats_json_string = json.dumps(mock_stats, ensure_ascii=False)

    try:
        # Вызываем ваш метод анализа
        analysis_result = await service.analyze_study_stats(stats_json=stats_json_string)

        print("✅ analyze_study_stats вернул результат:")
        print("-" * 50)
        print(analysis_result)
        print("-" * 50)
        print()
        
        # Проверяем, что метод вернул не пустую строку и в ней есть текст
        return bool(analysis_result and len(analysis_result) > 0)

    except Exception as e:
        print(f"❌ ОШИБКА: {type(e).__name__}")
        print(f"   Детали: {e}")
        return False



async def main():
    # print("=" * 70)
    # print("ТЕСТИРОВАНИЕ DEEPSEEK AI СЕРВИСА (реализация)")
    # print("=" * 70)
    # print()

    # # Проверка переменных окружения
    # api_key = os.getenv("AI_API_KEY")
    # model = os.getenv("AI_MODEL")
    # base_url = os.getenv("AI_BASE_URL")

    # print("📋 Конфигурация:")
    # print(f"   AI_API_KEY: {'***' + (api_key or '')[-4:] if api_key else 'НЕ УКАЗЕН'}")
    # print(f"   AI_MODEL: {model or 'НЕ УКАЗАН'}")
    # print(f"   AI_BASE_URL: {base_url or 'НЕ УКАЗАН'}")
    # print()
    # print("=" * 70)
    # print()

    results = {}

    # Тест 0: Прямой HTTP (диагностика сети/API)
    await test_deepseek_service_analyze_stats()
     # print("🧪 ТЕСТ 0: Прямой HTTP запрос к API (диагностика)")
        # print("-" * 70)
        # results["http_direct"] = await test_http_direct()
        # print()
        
    # print("🧪 ТЕСТ 0: Прямой HTTP запрос к API (диагностика)")
    # print("-" * 70)
    # results["http_direct"] = await test_http_direct()
    # print()

    # if not results["http_direct"]:
    #     print("⚠️ Прямой HTTP запрос не удался. Дальнейшие тесты могут быть бесполезны.")
    #     print("Проверьте сеть, API ключ и доступность DeepSeek API.")
    #     print()

    # # Тест 1: Базовый корректный контент
    # print("🧪 ТЕСТ 1: moderate_public_deck - корректный контент")
    # print("-" * 70)
    # results["basic"] = await test_deepseek_service_basic()
    # print()

    # # Тест 2: Некорректный контент
    # print("🧪 ТЕСТ 2: moderate_public_deck - некорректный контент")
    # print("-" * 70)
    # results["invalid_content"] = await test_deepseek_service_invalid_content()
    # print()

    # # Тест 3: Русскоязычный контент
    # print("🧪 ТЕСТ 3: moderate_public_deck - русскоязычный контент")
    # print("-" * 70)
    # results["russian"] = await test_deepseek_service_russian()
    # print()

    # # Тест 4: Пустые карточки
    # print("🧪 ТЕСТ 4: moderate_public_deck - пустой список карточек")
    # print("-" * 70)
    # results["empty_cards"] = await test_deepseek_service_empty_cards()
    # print()

    # # Итоги
    # print("=" * 70)
    # print("ИТОГИ ТЕСТИРОВАНИЯ:")
    # print("=" * 70)

    # total = len(results)
    # passed = sum(1 for v in results.values() if v)

    # for test_name, success in results.items():
    #     status = "✅ ПРОЙДЕН" if success else "❌ ПРОВАЛЕН"
    #     print(f"   {test_name}: {status}")

    # print()
    # print(f"  Всего: {passed}/{total} тестов успешно")
    # print()

    # if passed == total:
    #     print("🎉 ВСЕ ТЕСТЫ УСПЕШНЫ! DeepSeekAIService работает корректно.")
    # else:
    #     print("⚠️ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ. Проверьте конфигурацию и сеть.")

    # print()
    # return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
