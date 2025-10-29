from src.schema_models import User
from fastapi import HTTPException, Response, APIRouter, Depends
from pydantic import BaseModel, Field
from src.utils.auth_utils import (
    hash_password,
    match_passwords,
    set_auth_cookie,
)
from repositories import Repository, get_repo

router: APIRouter = APIRouter(tags=["Authentication"])


class Credentials(BaseModel):
    username: str = Field(min_length=3)
    password: str = Field(min_length=5)


@router.post("/login")
def login(
    credentials: Credentials,
    response: Response,
    repo: Repository = Depends(get_repo),  # pyright: ignore[reportCallInDefaultInitializer]
):
    user: User | None = repo.get_user(credentials.username)

    if not user:
        raise HTTPException(status_code=401, detail="Username not registered.")

    if not match_passwords(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid password.")

    set_auth_cookie(credentials.username, response)


@router.post("/register")
async def register(
    credentials: Credentials,
    response: Response,
    repo: Repository = Depends(get_repo),  # pyright: ignore[reportCallInDefaultInitializer]
) -> None:
    hashed_password: str = hash_password(credentials.password)
    user: User = User(username=credentials.username, password_hash=hashed_password)

    user_registered: bool = repo.create_user(user)

    if user_registered:
        set_auth_cookie(credentials.username, response)
    else:
        raise HTTPException(status_code=400, detail="Username is taken.")
