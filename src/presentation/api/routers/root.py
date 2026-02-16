from fastapi import APIRouter

from .v1 import profile as auth_v1

api_router = APIRouter(prefix="/api")

api_router.include_router(auth_v1.router, prefix="/v1")
