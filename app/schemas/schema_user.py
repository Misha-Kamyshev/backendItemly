from typing import Optional

from pydantic import BaseModel


class CreateUserSchema(BaseModel):
    username: str
    email: str
    password: str


class LoginUserSchema(BaseModel):
    email: Optional[str]
    username: Optional[str]
    password: str


class PushDataUserSchema(BaseModel):
    username: str
    access_token: str
    refresh_token: str
