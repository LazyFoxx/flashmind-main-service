import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)


class TimezoneMiddleware(BaseHTTPMiddleware):
    """
    Извлекает таймзону из заголовка X-Timezone
    и добавляет её в state запроса для использования в обработчиках.
    
    ВАЛИДАЦИЯ:
       - Используется zoneinfo.ZoneInfo() для автоматической проверки
       - При невалидной таймзоне логируется предупреждение
       - fallback на UTC
    """

    async def dispatch(self, request: Request, call_next):
        timezone_str = request.headers.get("X-Timezone", "UTC")
        
           # Автоматическая валидация через ZoneInfo
        try:
            ZoneInfo(timezone_str)
               # Валидная таймзона, продолжаем
        except (KeyError, ValueError):
               # Невалидная таймзона, логируем и используем UTC
            logger.warning(
                 "Невалидная таймзона, используется UTC",
                extra={"provided_timezone": timezone_str},
             )
            timezone_str = "UTC"
        
        request.state.timezone = timezone_str
        
        response = await call_next(request)
        return response
