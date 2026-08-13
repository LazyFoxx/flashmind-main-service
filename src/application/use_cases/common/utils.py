from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo


def get_study_cutoff(now: datetime, rollover_hour: int = 3) -> datetime:
    """
    Вычисляет cutoff — момент, разделяющий 'сегодня' и 'завтра'.
    
    Пример:
        Если сейчас 2024-01-15 14:00, cutoff = 2024-01-16 03:00
        Все карточки с next_due <= cutoff считаются 'на повтор сегодня'
    """
    study_day = now.date()
    return datetime.combine(
        study_day + timedelta(days=1),
        time(rollover_hour, 0),
        tzinfo=now.tzinfo,
    )


def get_current_datetime(timezone_str: str = "UTC") -> datetime:
    """Возвращает текущий момент в указанной таймзоне."""
    user_tz = ZoneInfo(timezone_str) if timezone_str else ZoneInfo("UTC")
    return datetime.now(user_tz)
