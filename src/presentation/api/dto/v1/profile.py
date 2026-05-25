from pydantic import BaseModel
from typing import Dict


class UserProfileResponse(BaseModel):
    first_name: str
    last_name: str
    avatar_url: str
    bio: str
    total_reviews: int = 0
    review_series: int = 0
    daily_review_counts: Dict[str, int] = {}

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "avatar_url": "https://example.com/avatar.png",
                    "first_name": "Дмитрий",
                    "last_name": "Черноморов",
                    "bio": "Имею самую лучшую и любящую девушку на свете",
                    "total_reviews": 150,
                    "review_series": 7,
                    "daily_review_counts": {
                        "2024-01-01": 5,
                        "2024-01-02": 3,
                        "2024-01-03": 0,
                    },
                }
            ]
        }
    }
