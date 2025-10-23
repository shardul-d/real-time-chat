from fastapi import HTTPException, Response, APIRouter
from pydantic import BaseModel, Field
from src.utils.auth_utils import (
    get_user_if_exists,
    hash_password,
    match_passwords,
    set_auth_cookie,
)
from src.db import engine
from src.models import User
from sqlmodel import Session, select

router: APIRouter = APIRouter()


class Credentials(BaseModel):
    username: str = Field(min_length=3)
    password: str = Field(min_length=5)


@router.post("/login")
async def login(credentials: Credentials, response: Response):
    with Session(engine) as session:
        user: User | None = get_user_if_exists(session, credentials.username)

        if not user:
            raise HTTPException(status_code=401, detail="Username not registered.")

        if not match_passwords(credentials.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid password.")

        set_auth_cookie(user.id, response)  # pyright: ignore[reportArgumentType]


@router.post("/register")
async def register(credentials: Credentials, response: Response) -> None:
    with Session(engine) as session:
        statement = select(User).where(User.username == credentials.username)
        existing_user = session.exec(statement).first()

        if existing_user:
            raise HTTPException(status_code=400, detail="Username already taken.")

        hashed_password: str = hash_password(credentials.password)
        user: User = User(username=credentials.username, password_hash=hashed_password)
        session.add(user)
        session.commit()
        session.refresh(user)

        set_auth_cookie(user.id, response)  # pyright: ignore[reportArgumentType]
