from pydantic import BaseModel, Field


class ChatBase(BaseModel):
    name: str = Field(..., max_length=255)


class ChatCreateRequest(ChatBase):
    pass


class ChatCreateResponse(ChatBase):
    id: int

    class Config:
        from_attributes = True  # pyright: ignore[reportUnannotatedClassAttribute]
