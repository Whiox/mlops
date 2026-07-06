
from pydantic import BaseModel, Field, ConfigDict


class MessageSc(BaseModel):
    text: str
    is_user: bool
    is_assistant: bool

    model_config = ConfigDict(from_attributes=True)


class ChatCreateSc(BaseModel):
    title: str = Field(min_length=1, max_length=32)


class ChatPrevSc(BaseModel):
    id: int
    title: str
    user_id: int

    model_config = ConfigDict(from_attributes=True)
