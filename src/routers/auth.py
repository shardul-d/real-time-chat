from fastapi import HTTPException, Response, APIRouter, Depends, status
from pydantic import BaseModel, Field

from dependencies import AuthenticatedUsername
from schema_models import User
from utils.auth_utils import (
    hash_password,
    match_passwords,
    set_auth_cookie,
)
from repository import Repository, get_repo

router = APIRouter(tags=["Authentication"])


# ✅ Pydantic request schema
class Credentials(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=5, max_length=100)

@router.get("/check_authentication_status", status_code=status.HTTP_200_OK)
async def check_authentication_status(username: AuthenticatedUsername):
    return {"status": "authenticated"}

# ✅ Login route (async)
@router.post("/login", status_code=status.HTTP_200_OK)
async def login(
    credentials: Credentials,
    response: Response,
    repo: Repository = Depends(get_repo),
):
    """Authenticate a user and set a secure cookie."""
    user: User | None = await repo.get_user(credentials.username)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    if not match_passwords(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Successful authentication → set auth cookie
    set_auth_cookie(credentials.username, response)

    return {"detail": "Login successful"}


# ✅ Registration route (async)
@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    credentials: Credentials,
    response: Response,
    repo: Repository = Depends(get_repo),
):
    """Register a new user and set an auth cookie."""
    hashed_password = hash_password(credentials.password)
    new_user = User(username=credentials.username, password_hash=hashed_password)

    user_created = await repo.create_user(new_user)
    if not user_created:
        raise HTTPException(status_code=400, detail="Username is already taken")

    set_auth_cookie(credentials.username, response)
    return {"detail": "Registration successful"}
