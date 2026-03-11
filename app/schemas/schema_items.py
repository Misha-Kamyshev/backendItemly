from pydantic import BaseModel


class ItemData(BaseModel):
    id: int
    image_url: str


class ItemsDataResponse(BaseModel):
    items: list[ItemData]
    has_next: bool


class ItemInformationResponse(BaseModel):
    tags: list[str]
    icon_author: str | None
    author: str
    name: str
    count_like: int
    save_item: bool
    like_item: bool


class ItemSimilarRequest(BaseModel):
    tags: list[str]
    last_id: int | None = None


class SearchRequest(BaseModel):
    query: str
    last_id: int | None = None
