from dishka import Provider, Scope, provide

from src.application.use_cases import (
    CreateDeckUseCase,
    CreateUserProfileUseCase,
    GetUserDecksUseCase,
    GetUserProfileUseCase,
    UpdateUserProfileUseCase,
)


class UseCaseProvider(Provider):
    get_user_profile = provide(GetUserProfileUseCase, scope=Scope.REQUEST)
    create_user_profile = provide(CreateUserProfileUseCase, scope=Scope.REQUEST)
    update_user_profile = provide(UpdateUserProfileUseCase, scope=Scope.REQUEST)

    create_deck = provide(CreateDeckUseCase, scope=Scope.REQUEST)
    get_user_decks = provide(GetUserDecksUseCase, scope=Scope.REQUEST)
