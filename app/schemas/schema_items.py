from pydantic import BaseModel


class ItemDataSchema(BaseModel):
    id: int
    image_url: str


class HomeDataSchema(BaseModel):
    items: list[ItemDataSchema]
    has_next: bool


class ItemSimilarDataSchema(BaseModel):
    username: str
    tags: list[str]
    last_id: int | None = None
