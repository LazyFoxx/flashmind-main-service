from dishka import Provider, Scope, provide

from src.application.use_cases import (
    CreateCardUseCase,
    CreateDeckUseCase,
    CreateUserProfileUseCase,
    DeleteCardUseCase,
    DeleteDeckUseCase,
    GetCardsUseCase,
    GetCardUseCase,
    GetStudyCardsUseCase,
    GetUserDecksUseCase,
    GetUserProfileUseCase,
    NewToStudyUseCase,
    ReviewDueCardsUseCase,
    UpdateCardUseCase,
    UpdateDeckUseCase,
    UpdateUserProfileUseCase,
    DailyReviewStatUseCase,
    SyncCardsToCloudUseCase,
    EnableSharingUseCase,
    ImportDeckUseCase,
    GetCloudDeckUseCase,
    GetCloudCardsUseCase,
    GetCloudCardUseCase,
    GetPublicDecksUseCase,
    DeleteCloudDeckUseCase,
    CanTakeOwnershipUseCase,
    TakeOwnershipUseCase,
    # StudyStatUseCase,
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
    delete_card = provide(DeleteCardUseCase, scope=Scope.REQUEST)
    get_cards = provide(GetCardsUseCase, scope=Scope.REQUEST)

    new_to_study = provide(NewToStudyUseCase, scope=Scope.REQUEST)
    get_study_cards = provide(GetStudyCardsUseCase, scope=Scope.REQUEST)
    review_due_card = provide(ReviewDueCardsUseCase, scope=Scope.REQUEST)
    
    daily_rev_stats = provide(DailyReviewStatUseCase, scope=Scope.REQUEST)
    # study_stats = provide(StudyStatUseCase, scope=Scope.REQUEST)
    
    enable_sharing = provide(EnableSharingUseCase, scope=Scope.REQUEST)
    sync_cards_to_cloud = provide(SyncCardsToCloudUseCase, scope=Scope.REQUEST)
    import_deck = provide(ImportDeckUseCase, scope=Scope.REQUEST)
    get_cloud_deck = provide(GetCloudDeckUseCase, scope=Scope.REQUEST)
    get_cloud_cards = provide(GetCloudCardsUseCase, scope=Scope.REQUEST)
    get_cloud_card = provide(GetCloudCardUseCase, scope=Scope.REQUEST)
    get_public_decks = provide(GetPublicDecksUseCase, scope=Scope.REQUEST)
    delete_cloud_deck = provide(DeleteCloudDeckUseCase, scope=Scope.REQUEST)
    can_take_ownership = provide(CanTakeOwnershipUseCase, scope=Scope.REQUEST)
    take_ownership = provide(TakeOwnershipUseCase, scope=Scope.REQUEST)
    
