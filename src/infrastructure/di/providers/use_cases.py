from dishka import Provider, Scope, provide

from src.application.use_cases import (
    CreateCardUseCase,
    CreateDeckUseCase,
    CreateUserProfileUseCase,
    DeleteDeckUseCase,
    GetCardUseCase,
    GetUserDecksUseCase,
    GetUserProfileUseCase,
    UpdateCardUseCase,
    UpdateDeckUseCase,
    UpdateUserProfileUseCase,
)


class UseCaseProvider(Provider):
    get_user_profile = provide(GetUserProfileUseCase, scope=Scope.REQUEST)
    create_user_profile = provide(CreateUserProfileUseCase, scope=Scope.REQUEST)
    update_user_profile = provide(UpdateUserProfileUseCase, scope=Scope.REQUEST)

    create_deck = provide(CreateDeckUseCase, scope=Scope.REQUEST)
    get_user_decks = provide(GetUserDecksUseCase, scope=Scope.REQUEST)
    update_deck = provide(UpdateDeckUseCase, scope=Scope.REQUEST)
    delete_deck = provide(DeleteDeckUseCase, scope=Scope.REQUEST)

    create_card = provide(CreateCardUseCase, scope=Scope.REQUEST)
    get_card = provide(GetCardUseCase, scope=Scope.REQUEST)
    update_card = provide(UpdateCardUseCase, scope=Scope.REQUEST)
