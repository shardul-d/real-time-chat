from schema_models import User, Chat
from src.dependencies import AuthenticatedUsername
from fastapi import APIRouter, Depends
from repositories import Repository, get_repo

router: APIRouter = APIRouter(tags=["Chat Management"])


@router.post(path="/chats/create_chat")
async def create_chat(
    username: AuthenticatedUsername,
    chat_name: str,
    repo: Repository = Depends(get_repo),
):
    user: User | None = repo.get_user(username)

    assert user is not None

    repo.create_chat(user, chat_name)


@router.post(path="/chats/join_chat")
async def join_chat(
    username: AuthenticatedUsername, chat_id: int, repo: Repository = Depends(get_repo)
):
    user: User | None = repo.get_user(username)
    chat: Chat | None = repo.get_chat(chat_id)

    assert user is not None
    assert chat is not None

    repo.join_chat(user, chat)
