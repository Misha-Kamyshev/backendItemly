from pydantic import BaseModel


class HomeDataSchema(BaseModel):
    id: int
    image_url: str


class ItemSimilarDataSchema(BaseModel):
    username: str
    tags: list[str]
