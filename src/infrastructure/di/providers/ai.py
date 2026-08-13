from dishka import Provider, Scope, provide

from src.application.interfaces import AbstractAIService
from src.infrastructure.ai.deepseek_service import DeepSeekAIService
from src.core.settings import AISettings


class AIProvider(Provider):
    @provide(scope=Scope.APP)
    def deepseek_service(self, ai_settings: AISettings) -> AbstractAIService:
        return DeepSeekAIService(ai_settings)
