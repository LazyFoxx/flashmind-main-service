from pydantic import BaseModel


class MessagePayload(BaseModel):
    user_id: str
