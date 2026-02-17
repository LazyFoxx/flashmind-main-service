from pydantic import BaseModel


class CreateDeckResponse(BaseModel):
    id: str
    name: str
    description: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "UUID",
                    "name": "Английский 3000",
                    "description": "Тут собраны 3000 самых популярных слов в английском языке",
                }
            ]
        }
    }


class CreateDeckRequest(BaseModel):
    name: str
    description: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Английский 3000",
                    "description": "Тут собраны 3000 самых популярных слов в английском языке",
                }
            ]
        }
    }


class ErrorMessageResponse(BaseModel):
    message: str
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "message": "Колода с таким названием уже существует",
                }
            ]
        }
    }
