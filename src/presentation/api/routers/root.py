from fastapi import APIRouter

from .v1 import card as card_v1
from .v1 import deck as deck_v1
from .v1 import profile as profile_v1

api_router = APIRouter(prefix="/api")

api_router.include_router(profile_v1.router, prefix="/v1")
api_router.include_router(deck_v1.router, prefix="/v1")
api_router.include_router(card_v1.router, prefix="/v1")
