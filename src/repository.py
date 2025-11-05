from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from db import get_db_session
from schema_models import Chat, ChatMembers, Message, User
from schemas.message import MessageCreate


class Repository:
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    # ✅ Async query with select
    async def get_user(self, username: str) -> User | None:
        stmt = select(User).where(User.username == username)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    # ✅ Async add + commit + refresh
    async def create_user(self, user: User) -> bool:
        try:
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
            return True
        except IntegrityError:
            return False

    async def create_chat(self, user: User, chat_name: str) -> Chat:
        chat = Chat(name=chat_name, is_group=True)
        self.session.add(chat)
        await self.session.flush()  # ensures chat.id is available before commit

        chat_member = ChatMembers(chat_id=chat.id, user_id=user.id)
        self.session.add(chat_member)

        await self.session.commit()
        await self.session.refresh(chat)
        return chat

    async def get_chat(self, chat_id: int) -> Chat | None:
        stmt = select(Chat).where(Chat.id == chat_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def join_chat(self, user: User, chat: Chat) -> bool:
        chat_member = ChatMembers(chat_id=chat.id, user_id=user.id)
        self.session.add(chat_member)
        try:
            await self.session.commit()
            return True
        except IntegrityError:
            return False

    async def send_message(self, message: MessageCreate) -> Message:
        msg = Message(
            body=message.body, chat_id=message.chat_id, sender_id=message.sender_id
        )

        self.session.add(msg)
        await self.session.commit()
        await self.session.refresh(msg)
        return msg


# ✅ FastAPI dependency
async def get_repo(session: AsyncSession = Depends(get_db_session)) -> Repository:
    return Repository(session)
