
from pydantic import BaseModel, Field
from typing import Literal


class AuthUser(BaseModel):
    username: str = Field(min_length = 4, max_length = 32)
    password: str = Field(min_length = 8, max_length = 32)


class AuthStatus(BaseModel):
    status: Literal["ok", "error"]

    token: str | None
    error: str | None
