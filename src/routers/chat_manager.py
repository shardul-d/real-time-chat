from fastapi import APIRouter, Depends, HTTPException, status
from schema_models import User, Chat
from dependencies import AuthenticatedUsername
from repository import Repository, get_repo
from schemas.chat import ChatCreateResponse, ChatCreateRequest

router = APIRouter(tags=["Chat Management"])

@router.get("/chats", status_code=status.HTTP_200_OK)
async def chats(username: AuthenticatedUsername, repo: Repository = Depends(get_repo)):
    pass
@router.post(
    "/chats/create_chat",
    response_model=ChatCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_chat(
    username: AuthenticatedUsername,
    payload: ChatCreateRequest,
    repo: Repository = Depends(get_repo),
):
    """Create a new group chat and automatically add the creator as a member."""
    print(f"Hit create chat: {username}")
    user: User | None = await repo.get_user(username)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    chat: Chat = await repo.create_chat(user, payload.name)
    return chat  # ✅ FastAPI auto-serializes ORM → ChatRead


@router.post(
    "/chats/join_chat",
    status_code=status.HTTP_200_OK,
)
async def join_chat(
    username: AuthenticatedUsername,
    chat_id: int,
    repo: Repository = Depends(get_repo),
):
    """Join an existing chat."""
    user: User | None = await repo.get_user(username)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    chat: Chat | None = await repo.get_chat(chat_id)
    if chat is None:
        raise HTTPException(status_code=404, detail="Chat not found")

    could_join: bool = await repo.join_chat(user, chat)

    if not could_join:
        raise HTTPException(status_code=409, detail="User already in chat.")

    return {"detail": f"{username} joined chat {chat.name or chat.id}"}
