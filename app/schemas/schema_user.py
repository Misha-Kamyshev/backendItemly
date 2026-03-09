from pydantic import BaseModel


class CreateUserSchema(BaseModel):
    username: str
    email: str
    password: str


class LoginUserSchema(BaseModel):
    login: str
    password: str


class PushDataUserSchema(BaseModel):
    username: str
    email: str
    access_token: str
    refresh_token: str
    

class PushPreviewImageUserSchema(BaseModel):
    path_preview: str | None

