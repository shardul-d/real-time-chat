from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Relationship  # pyright: ignore[reportUnknownVariableType]


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True, nullable=False)
    password_hash: str = Field(nullable=False)

    messages: list["Message"] = Relationship(back_populates="sender")  # pyright: ignore[reportAny]
    chats: list["Chat"] = Relationship(  # pyright: ignore[reportAny]
        back_populates="members", link_model=lambda: ChatMembers
    )


class Chat(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(default=None, nullable=True)
    is_group: bool = Field(default=False, nullable=False)

    messages: list["Message"] = Relationship(back_populates="chat")  # pyright: ignore[reportAny]
    members: list["User"] = Relationship(  # pyright: ignore[reportAny]
        back_populates="chats", link_model=lambda: ChatMembers
    )


class ChatMembers(SQLModel, table=True):
    chat_id: int = Field(foreign_key="chat.id", primary_key=True)
    user_id: int = Field(foreign_key="user.id", primary_key=True)


class Message(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    chat_id: int = Field(foreign_key="chat.id", nullable=False)
    sender_id: int = Field(foreign_key="user.id", nullable=False)
    body: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    chat: Chat = Relationship(back_populates="messages")  # pyright: ignore[reportAny]
    sender: User = Relationship(back_populates="messages")  # pyright: ignore[reportAny]
