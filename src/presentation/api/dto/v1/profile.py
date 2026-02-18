from pydantic import BaseModel


class UserProfileResponse(BaseModel):
    first_name: str
    last_name: str
    avatar_url: str
    bio: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "avatar_url": "https://example.com/avatar.png",
                    "first_name": "Дмитрий",
                    "last_name": "Черноморов",
                    "bio": "Имею самую лучшую и любящую девушку на свете",
                }
            ]
        }
    }
