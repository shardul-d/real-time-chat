from fastapi import Depends
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select
from db import get_session
from schema_models import Chat, ChatMembers, User


class Repository:
    def __init__(self, session: Session):
        self.session: Session = session

    def get_user(self, username: str) -> User | None:
        statement = select(User).where(User.username == username)
        return self.session.exec(statement).first()

    def create_user(self, user: User) -> bool:
        try:
            self.session.add(user)
            self.session.commit()
            self.session.refresh(user)
            return True
        except IntegrityError:
            return False

    def create_chat(self, user: User, chat_name: str):
        chat: Chat = Chat(name=chat_name, is_group=True)

        self.session.add(chat)
        self.session.refresh(chat)

        assert chat.id is int
        assert user.id is int

        chat_member: ChatMembers = ChatMembers(chat_id=chat.id, user_id=user.id)
        self.session.add(chat_member)
        self.session.commit()

    def get_chat(self, chat_id: int) -> Chat | None:
        statement = select(Chat).where(Chat.id == chat_id)
        return self.session.exec(statement).first()

    def join_chat(self, user: User, chat: Chat):
        assert chat.id is int
        assert user.id is int

        chat_member: ChatMembers = ChatMembers(chat_id=chat.id, user_id=user.id)

        self.session.add(chat_member)
        self.session.commit()


# Call this only as a dependency for a FastAPI route ie. Depends(get_repo)
def get_repo(session: Session = Depends(get_session)) -> Repository:  # pyright: ignore[reportCallInDefaultInitializer]
    return Repository(session)
