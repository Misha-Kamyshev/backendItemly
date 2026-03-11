from pydantic import BaseModel


class CreateUserRequest(BaseModel):
    username: str
    email: str
    password: str


class LoginUserRequest(BaseModel):
    login: str
    password: str


class DataUserResponse(BaseModel):
    username: str
    email: str
    access_token: str
    refresh_token: str


class PreviewImageUserResponse(BaseModel):
    path_preview: str | None
