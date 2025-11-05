from pydantic import BaseModel, Field
from datetime import datetime
from .user import UserRead


class MessageBase(BaseModel):
    body: str = Field(..., min_length=1, max_length=5000)


class MessageCreate(MessageBase):
    chat_id: int
    sender_id: int


class MessageRead(MessageBase):
    id: int
    created_at: datetime
    sender: UserRead
    chat_id: int

    class Config:
        from_attributes = True  # pyright: ignore[reportUnannotatedClassAttribute]
