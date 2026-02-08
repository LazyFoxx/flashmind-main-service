from dishka import Provider, Scope, provide

from src.application.use_cases import CreateUserProfileUseCase, GetUserProfileUseCase


class UseCaseProvider(Provider):
    get_user_profile = provide(GetUserProfileUseCase, scope=Scope.REQUEST)
    create_user_profile = provide(CreateUserProfileUseCase, scope=Scope.REQUEST)
