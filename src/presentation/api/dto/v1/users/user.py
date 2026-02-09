from typing import Optional

from fastapi import UploadFile
from pydantic import BaseModel, Field, HttpUrl


class UserProfileResponse(BaseModel):
    first_name: str
    last_name: str
    avatar_url: str
    bio: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "avatar_url": "https://example.com/avatar.png",
                    "first_name": "Иван",
                    "last_name": "Черноморов",
                }
            ]
        }
    }


class CreateUserProfileRequest(BaseModel):
    first_name: str = Field(
        ..., min_length=2, max_length=50, description="Имя"
    )
    last_name: str = Field(
        ..., min_length=2, max_length=50, description="Фамилия"
    )
    bio: Optional[str] = Field(None, max_length=500, description="Краткая информация о пользователе")

    avatar: Optional[UploadFile] = Field(default=None)

    model_config = {"extra": "forbid"}
