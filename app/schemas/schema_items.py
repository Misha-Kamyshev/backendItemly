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


class HomeRequest(BaseModel):
    username: str
    last_id: int | None = None


class ItemRequest(BaseModel):
    id: int
    username: str


class ItemInformation(BaseModel):
    tags: list[str]
    icon_author: str | None
    author: str
    name: str
    count_like: int
    save_item: bool
    like_item: bool


class SearchRequest(BaseModel):
    query: str
    last_id: int | None = None
