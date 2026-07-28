from fastapi import APIRouter
from .v1.card import router as card_v1
from .v1.deck import router as deck_v1
from .v1.profile import router as profile_v1
from .v1.study import router as study_v1
from .v1.cloud_deck import router as cloud_deck_v1
from .v1.stats import router as stats_v1

api_router_v1 = APIRouter(prefix="/api/v1/flashmind")

api_router_v1.include_router(deck_v1)
api_router_v1.include_router(card_v1)
api_router_v1.include_router(profile_v1)
api_router_v1.include_router(study_v1)
api_router_v1.include_router(cloud_deck_v1)
api_router_v1.include_router(stats_v1)
