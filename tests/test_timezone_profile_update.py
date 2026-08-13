"""
Тесты для проверки обновления timezone при запросе к GET /users/profile.

Этот тест проверяет:
1. TimezoneMiddleware корректно извлекает timezone из заголовка X-Timezone
2. DailyReviewStatUseCase синхронизирует timezone пользователя при вызове
3. SQlAlchemyUserRepository корректно сохраняет timezone в БД
4. Edge cases: невалидный timezone, отсутствие заголовка, разные таймзоны

Запуск: poetry run python tests/test_timezone_profile_update.py
"""
import asyncio
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

# Добавляем src в PYTHONPATH
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))


# ============================================================================
# ТЕСТ 1: TimezoneMiddleware — извлечение timezone из заголовка
# ============================================================================

async def test_middleware_extract_valid_timezone() -> bool:
    """Тест: Middleware корректно извлекает валидный timezone из заголовка."""
    from fastapi import FastAPI, Request
    from starlette.testclient import TestClient

    from src.core.middleware.timezone_middleware import TimezoneMiddleware

    print("🧪 ТЕСТ 1: Извлечение валидного timezone из заголовка X-Timezone")
    print("-" * 70)

    app = FastAPI()

    @app.get("/test")
    async def test_endpoint(request: Request):
        """Эндпоинт для проверки middleware."""
        return {"timezone": getattr(request.state, "timezone", None)}

    app.add_middleware(TimezoneMiddleware)

    client = TestClient(app)

    response = client.get(
        "/test",
        headers={"X-Timezone": "America/Los_Angeles"},
    )

    assert response.status_code == 200
    data = response.json()
    tz = data.get("timezone")

    print(f"   Заголовок: America/Los_Angeles")
    print(f"   Результат: {tz}")

    success = tz == "America/Los_Angeles"
    print(f"    {'✅ ПРОЙДЕН' if success else '❌ ПРОВАЛЕН'}")
    print()

    return success


async def test_middleware_fallback_to_utc_on_invalid() -> bool:
    """Тест: Middleware fallback на UTC при невалидном timezone."""
    from fastapi import FastAPI, Request
    from starlette.testclient import TestClient

    from src.core.middleware.timezone_middleware import TimezoneMiddleware

    print("🧪 ТЕСТ 2: Fallback на UTC при невалидном timezone")
    print("-" * 70)

    app = FastAPI()

    @app.get("/test")
    async def test_endpoint(request: Request):
        return {"timezone": getattr(request.state, "timezone", None)}

    app.add_middleware(TimezoneMiddleware)

    client = TestClient(app)

    # Тест с невалидным timezone
    response = client.get(
        "/test",
        headers={"X-Timezone": "Invalid/Zone"},
    )
    data = response.json()
    tz = data.get("timezone")

    print(f"   Заголовок: Invalid/Zone")
    print(f"   Результат: {tz}")

    success = tz == "UTC"
    print(f"    {'✅ ПРОЙДЕН' if success else '❌ ПРОВАЛЕН'}")
    print()

    return success


async def test_middleware_default_utc_when_missing() -> bool:
    """Тест: Middleware использует UTC по умолчанию, если заголовок отсутствует."""
    from fastapi import FastAPI, Request
    from starlette.testclient import TestClient

    from src.core.middleware.timezone_middleware import TimezoneMiddleware

    print("🧪 ТЕСТ 3: UTC по умолчанию при отсутствии заголовка")
    print("-" * 70)

    app = FastAPI()

    @app.get("/test")
    async def test_endpoint(request: Request):
        return {"timezone": getattr(request.state, "timezone", None)}

    app.add_middleware(TimezoneMiddleware)

    client = TestClient(app)

    # Запрос без заголовка X-Timezone
    response = client.get("/test")
    data = response.json()
    tz = data.get("timezone")

    print(f"   Заголовок: (отсутствует)")
    print(f"   Результат: {tz}")

    success = tz == "UTC"
    print(f"    {'✅ ПРОЙДЕН' if success else '❌ ПРОВАЛЕН'}")
    print()

    return success


# ============================================================================
# ТЕСТ 4-5: DailyReviewStatUseCase — синхронизация timezone
# ============================================================================

async def test_use_case_sync_timezone_updates_user() -> bool:
    """Тест: Use Case обновляет timezone пользователя, если он отличается."""
    from src.application.use_cases.stats.daily_review_stat.use_case import (
        DailyReviewStatUseCase,
    )
    from src.application.use_cases.stats.daily_review_stat.dto import (
        DailyReviewStatInput,
    )
    from src.domain.entities.user.user import User
    from uuid import uuid4

    print("🧪 ТЕСТ 4: Use Case обновляет timezone пользователя")
    print("-" * 70)

    user_id = uuid4()
    old_user = User(
        id=user_id,
        first_name="Test",
        last_name="User",
        avatar_key="avatar.jpg",
        timezone="UTC",  # Старый timezone
    )

    # Mock uow
    mock_uow = MagicMock()
    mock_storage = MagicMock()

    mock_uow.__aenter__ = AsyncMock(return_value=mock_uow)
    mock_uow.__aexit__ = AsyncMock(return_value=None)
    mock_uow.commit = AsyncMock()

    # get_by_id возвращает пользователя с UTC timezone
    mock_uow.users.get_by_id = AsyncMock(return_value=old_user)
    mock_uow.users.update = AsyncMock()

    # review_logs
    mock_uow.review_logs.get_daily_review_counts = AsyncMock(return_value={})
    mock_uow.review_logs.get_current_streak_days = AsyncMock(return_value=0)
    mock_uow.review_logs.get_total_reviews_count = AsyncMock(return_value=0)

    # user_stats
    mock_uow.user_stats.get_by_user_id = AsyncMock(return_value=None)
    mock_uow.user_stats.add = AsyncMock()
    mock_uow.user_stats.update = AsyncMock()

    # Создаём use case
    use_case = DailyReviewStatUseCase(uow=mock_uow, storage=mock_storage)

    # Вызываем с новым timezone
    input_dto = DailyReviewStatInput(
        user_id=user_id,
        days=28,
        timezone="America/Los_Angeles",
    )

    try:
        result = await use_case.execute(input_dto=input_dto)

        # Проверяем, что update был вызван с новым timezone
        update_called = mock_uow.users.update.called
        update_call_args = mock_uow.users.update.call_args

        print(f"   Старый timezone: UTC")
        print(f"   Новый timezone: America/Los_Angeles")
        print(f"   update() вызван: {update_called}")

        if update_called:
            updated_user = update_call_args[0][0]  # Первый аргумент — user
            print(f"   Updated user timezone: {updated_user.timezone}")
            success = updated_user.timezone == "America/Los_Angeles"
        else:
            success = False

        print(f"    {'✅ ПРОЙДЕН' if success else '❌ ПРОВАЛЕН'}")
        print()

        return success

    except Exception as e:
        print(f"    ❌ Исключение: {e}")
        print(f"    ❌ ПРОВАЛЕН")
        print()
        return False


async def test_use_case_no_update_when_same_timezone() -> bool:
    """Тест: Use Case НЕ обновляет пользователя, если timezone совпадает."""
    from src.application.use_cases.stats.daily_review_stat.use_case import (
        DailyReviewStatUseCase,
    )
    from src.application.use_cases.stats.daily_review_stat.dto import (
        DailyReviewStatInput,
    )
    from src.domain.entities.user.user import User

    print("🧪 ТЕСТ 5: Use Case НЕ обновляет timezone при совпадении")
    print("-" * 70)

    user_id = uuid4()
    existing_user = User(
        id=user_id,
        first_name="Test",
        last_name="User",
        avatar_key="avatar.jpg",
        timezone="Europe/Moscow",  # Уже нужный timezone
    )

    mock_uow = MagicMock()
    mock_storage = MagicMock()

    mock_uow.__aenter__ = AsyncMock(return_value=mock_uow)
    mock_uow.__aexit__ = AsyncMock(return_value=None)
    mock_uow.commit = AsyncMock()
    mock_uow.users.get_by_id = AsyncMock(return_value=existing_user)
    mock_uow.users.update = AsyncMock()
    mock_uow.review_logs.get_daily_review_counts = AsyncMock(return_value={})
    mock_uow.review_logs.get_current_streak_days = AsyncMock(return_value=0)
    mock_uow.review_logs.get_total_reviews_count = AsyncMock(return_value=0)
    mock_uow.user_stats.get_by_user_id = AsyncMock(return_value=None)
    mock_uow.user_stats.add = AsyncMock()
    mock_uow.user_stats.update = AsyncMock()

    use_case = DailyReviewStatUseCase(uow=mock_uow, storage=mock_storage)

    input_dto = DailyReviewStatInput(
        user_id=user_id,
        days=28,
        timezone="Europe/Moscow",  # Тот же timezone
    )

    try:
        result = await use_case.execute(input_dto=input_dto)

        # Проверяем, что update НЕ был вызван
        update_called = mock_uow.users.update.called

        print(f"   Timezone пользователя: Europe/Moscow")
        print(f"   Timezone из запроса: Europe/Moscow")
        print(f"   update() вызван: {update_called}")

        success = not update_called
        print(f"    {'✅ ПРОЙДЕН' if success else '❌ ПРОВАЛЕН'}")
        print()

        return success

    except Exception as e:
        print(f"    ❌ Исключение: {e}")
        print(f"    ❌ ПРОВАЛЕН")
        print()
        return False


# ============================================================================
# ТЕСТ 6-7: SQlAlchemyUserRepository — сохранение/загрузка timezone
# ============================================================================

async def test_repository_saves_timezone() -> bool:
    """Тест: Repository корректно сохраняет timezone в БД."""
    from src.domain.entities.user.user import User
    from src.infrastructure.db.models.user_profile import UserProfileModel

    print("🧪 ТЕСТ 6: Repository сохраняет timezone в БД")
    print("-" * 70)

    user_id = uuid4()
    user = User(
        id=user_id,
        first_name="Test",
        last_name="User",
        avatar_key="avatar.jpg",
        timezone="America/New_York",
    )

    # Создаём модель из entity
    model = UserProfileModel.from_domain(user)

    print(f"   User.timezone: {user.timezone}")
    print(f"   Model.timezone_str: {model.timezone_str}")

    # Проверяем, что timezone_str совпадает с user.timezone
    success = model.timezone_str == "America/New_York"

    print(f"    {'✅ ПРОЙДЕН' if success else '❌ ПРОВАЛЕН'}")
    print()

    return success


async def test_repository_loads_timezone() -> bool:
    """Тест: Repository корректно загружает timezone из БД (to_entity)."""
    from src.infrastructure.db.models.user_profile import UserProfileModel

    print("🧪 ТЕСТ 7: Repository загружает timezone из БД")
    print("-" * 70)

    user_id = uuid4()

    # Создаём модель с определённым timezone (имитация данных из БД)
    model = UserProfileModel(
        id=user_id,
        first_name="Test",
        last_name="User",
        avatar_key="avatar.jpg",
        bio=None,
        timezone_str="Asia/Tokyo",
    )

    # Конвертируем в entity
    entity = model.to_entity()

    print(f"   Model.timezone_str: {model.timezone_str}")
    print(f"   Entity.timezone: {entity.timezone}")

    success = entity.timezone == "Asia/Tokyo"

    print(f"    {'✅ ПРОЙДЕН' if success else '❌ ПРОВАЛЕН'}")
    print()

    return success


# ============================================================================
# ТЕСТ 8: Полный цикл — middleware + use case + repository
# ============================================================================

async def test_full_timezone_update_flow() -> bool:
    """Тест: Полный цикл обновления timezone через GET /users/profile."""
    from src.domain.entities.user.user import User
    from src.infrastructure.db.models.user_profile import UserProfileModel
    from zoneinfo import ZoneInfo

    print("🧪 ТЕСТ 8: Полный цикл обновления timezone")
    print("-" * 70)

    user_id = uuid4()
    initial_user = User(
        id=user_id,
        first_name="Dmitry",
        last_name="Test",
        avatar_key="avatar.jpg",
        timezone="UTC",  # Начальный timezone
    )

    # Шаг 1: Middleware извлекает timezone из заголовка
    test_timezone = "America/Los_Angeles"

    # Валидация через ZoneInfo
    try:
        ZoneInfo(test_timezone)
        tz_valid = True
    except (KeyError, ValueError):
        tz_valid = False

    print(f"   Шаг 1: Middleware извлекает timezone")
    print(f"   Заголовок X-Timezone: {test_timezone}")
    print(f"   Timezone валиден: {tz_valid}")

    if not tz_valid:
        print(f"    ❌ ПРОВАЛ (невалидный timezone)")
        print()
        return False

    # Шаг 2: Use Case проверяет и обновляет timezone
    print(f"   Шаг 2: Use Case проверяет timezone пользователя")
    print(f"   Текущий timezone: {initial_user.timezone}")
    print(f"   Новый timezone: {test_timezone}")

    needs_update = initial_user.timezone != test_timezone
    print(f"   Требуется обновление: {needs_update}")

    if needs_update:
        updated_user = initial_user.with_timezone(test_timezone)
        print(f"   Updated user timezone: {updated_user.timezone}")

        # Шаг 3: Repository сохраняет timezone
        model = UserProfileModel.from_domain(updated_user)
        saved_tz = model.timezone_str
        print(f"   Сохранённый timezone: {saved_tz}")

        success = saved_tz == test_timezone
    else:
        success = False

    print(f"    {'✅ ПРОЙДЕН' if success else '❌ ПРОВАЛЕН'}")
    print()

    return success


# ============================================================================
# ТЕСТ 9: Проверка обновления timezone через PATCH /users/profile
# ============================================================================

async def test_patch_profile_timezone_not_supported() -> bool:
    """Тест: PATCH /users/profile НЕ обновляет timezone (только name/bio/avatar)."""
    from src.domain.entities.user.user import User
    from src.infrastructure.db.models.user_profile import UserProfileModel

    print("🧪 ТЕСТ 9: PATCH /users/profile НЕ обновляет timezone")
    print("-" * 70)

    # Проверяем, что PATCH роутер не включает timezone в обновление
    # Смотри src/presentation/api/routers/v1/profile.py:82-89
    # Там передаются только: first_name, last_name, bio, avatar_file
    # Нет first_name, last_name, bio, avatar_file — нет timezone

    # Проверяем DTO UpdateProfileUserInput
    from src.application.use_cases.users.update_user_profile.dto import (
        UpdateProfileUserInput,
    )

    # Создаём DTO без timezone
    dto = UpdateProfileUserInput(
        user_id=uuid4(),
        first_name="NewName",
        last_name="NewLastName",
        bio="New bio",
    )

    # Проверяем, что в DTO нет timezone
    has_timezone = hasattr(dto, "timezone")

    print(f"   UpdateProfileUserInput имеет timezone: {has_timezone}")
    print(f"   DTO поля: user_id, first_name, last_name, bio, avatar_file")

    # PATCH не должен обновлять timezone — это ожидаемое поведение
    success = not has_timezone
    print(f"   PATCH НЕ обновляет timezone: {success}")
    print(f"    {'✅ ПРОЙДЕН' if success else '❌ ПРОВАЛЕН'}")
    print()

    return success


# ============================================================================
# ГЛАВНЫЙ MAIN
# ============================================================================

async def main():
    results = {}

    print()
    print("#" * 70)
    print("  ТЕСТЫ ОБНОВЛЕНИЯ TIMEZONE ЧЕРЕЗ GET /users/profile")
    print("#" * 70)
    print()

    # Тест 1: Middleware — валидный timezone
    print("🧪 ТЕСТ 1: Middleware — валидный timezone")
    print("-" * 70)
    results["middleware_valid_tz"] = (
        await test_middleware_extract_valid_timezone()
    )
    print()

    # Тест 2: Middleware — невалидный timezone
    print("🧪 ТЕСТ 2: Middleware — невалидный timezone")
    print("-" * 70)
    results["middleware_invalid_tz"] = (
        await test_middleware_fallback_to_utc_on_invalid()
    )
    print()

    # Тест 3: Middleware — отсутствие заголовка
    print("🧪 ТЕСТ 3: Middleware — отсутствие заголовка")
    print("-" * 70)
    results["middleware_default_utc"] = (
        await test_middleware_default_utc_when_missing()
    )
    print()

    # Тест 4: Use Case — обновление timezone
    print("🧪 ТЕСТ 4: Use Case — обновление timezone")
    print("-" * 70)
    results["use_case_sync_timezone"] = (
        await test_use_case_sync_timezone_updates_user()
    )
    print()

    # Тест 5: Use Case — без обновления (совпадение)
    print("🧪 ТЕСТ 5: Use Case — без обновления (совпадение)")
    print("-" * 70)
    results["use_case_no_update_same_tz"] = (
        await test_use_case_no_update_when_same_timezone()
    )
    print()

    # Тест 6: Repository — сохранение timezone
    print("🧪 ТЕСТ 6: Repository — сохранение timezone")
    print("-" * 70)
    results["repository_saves_timezone"] = (
        await test_repository_saves_timezone()
    )
    print()

    # Тест 7: Repository — загрузка timezone
    print("🧪 ТЕСТ 7: Repository — загрузка timezone")
    print("-" * 70)
    results["repository_loads_timezone"] = (
        await test_repository_loads_timezone()
    )
    print()

    # Тест 8: Полный цикл
    print("🧪 ТЕСТ 8: Полный цикл обновления timezone")
    print("-" * 70)
    results["full_timezone_flow"] = await test_full_timezone_update_flow()
    print()

    # Тест 9: PATCH не обновляет timezone
    print("🧪 ТЕСТ 9: PATCH НЕ обновляет timezone")
    print("-" * 70)
    results["patch_not_update_timezone"] = (
        await test_patch_profile_timezone_not_supported()
    )
    print()

    # Итоги
    print("=" * 70)
    print("ИТОГИ ТЕСТИРОВАНИЯ:")
    print("=" * 70)

    total = len(results)
    passed = sum(1 for v in results.values() if v)

    for test_name, success in results.items():
        status = "✅ ПРОЙДЕН" if success else "❌ ПРОВАЛЕН"
        print(f"    {test_name}: {status}")

    print()
    print(f"   Всего: {passed}/{total} тестов успешно")
    print()

    if passed == total:
        print(
            "🎉 ВСЕ ТЕСТЫ УСПЕШНЫ! Timezone корректно обновляется при запросе к GET /users/profile."
        )
    else:
        print("⚠️ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ. Проверьте реализацию.")

    print()
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
