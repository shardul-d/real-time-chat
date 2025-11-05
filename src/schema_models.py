from __future__ import annotations
from datetime import UTC, datetime
from uuid import uuid4
from sqlalchemy import String, Integer, JSON, DateTime, Boolean, ForeignKey, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.associationproxy import association_proxy, AssociationProxy


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__: str = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))

    messages: Mapped[list["Message"]] = relationship(back_populates="sender")

    chat_associations: Mapped[list["ChatMembers"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )
    chats: AssociationProxy[list["Chat"]] = association_proxy(
        target_collection="chat_associations", attr="chat"
    )


class Chat(Base):
    __tablename__: str = "chat"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str | None] = mapped_column(String(255))
    is_group: Mapped[bool] = mapped_column(default=False, nullable=False)

    messages: Mapped[list["Message"]] = relationship(
        back_populates="chat", cascade="all, delete-orphan", passive_deletes=True
    )
    user_associations: Mapped[list["ChatMembers"]] = relationship(
        back_populates="chat", cascade="all, delete-orphan", passive_deletes=True
    )
    members: AssociationProxy[list["User"]] = association_proxy(
        target_collection="user_associations", attr="user"
    )


class Message(Base):
    __tablename__: str = "message"

    id: Mapped[int] = mapped_column(primary_key=True)
    body: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    chat_id: Mapped[int] = mapped_column(ForeignKey("chat.id", ondelete="CASCADE"))
    sender_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))

    chat: Mapped["Chat"] = relationship(back_populates="messages")
    sender: Mapped["User"] = relationship(back_populates="messages")


class ChatMembers(Base):
    __tablename__: str = "chat_members"

    chat_id: Mapped[int] = mapped_column(
        ForeignKey("chat.id", ondelete="CASCADE"), primary_key=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"), primary_key=True
    )

    chat: Mapped["Chat"] = relationship(back_populates="user_associations")
    user: Mapped["User"] = relationship(back_populates="chat_associations")


class OutboxEvent(Base):
    __tablename__: str = "outbox_event"
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    # domain identification (helps routing/analytics)
    aggregate_type: Mapped[str] = mapped_column(String(64))  # e.g. "chat"
    aggregate_id: Mapped[int] = mapped_column(Integer)  # e.g. chat_id
    event_type: Mapped[str] = mapped_column(String(64))  # e.g. "MessageCreated"
    payload: Mapped[dict] = mapped_column(JSON)  # pyright: ignore[reportMissingTypeArgument]

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now(tz=UTC)
    )
    sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # delivery control
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    sent: Mapped[bool] = mapped_column(Boolean, default=False)
    lease_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
