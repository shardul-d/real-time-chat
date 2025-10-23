import bcrypt
from fastapi import HTTPException, Request, Response, status
import jwt
from datetime import datetime, timezone, timedelta
from jwt.exceptions import InvalidTokenError
from sqlmodel import Session, select
from src.core.config import config
from src.models import User


def toUtf8(string: str) -> bytes:
    return string.encode("utf-8")


def match_passwords(challenge: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(toUtf8(challenge), toUtf8(hashed_password))


def hash_password(password: str) -> str:
    return bcrypt.hashpw(toUtf8(password), bcrypt.gensalt(12)).decode("utf-8")


def get_user_if_exists(db: Session, username: str) -> User | None:
    statement = select(User).where(User.username == username)
    return db.exec(statement).first()


def create_jwt(user_id: int) -> str:
    expiry: datetime = datetime.now(timezone.utc) + timedelta(
        hours=config.JWT_EXPIRY_IN_HOURS
    )
    payload: dict[str, int | datetime] = {"sub": user_id, "exp": expiry}
    return jwt.encode(payload, config.JWT_SECRET, config.JWT_ALGORITHM)  # pyright: ignore[reportUnknownMemberType]


def validate_jwt_and_get_user_id(req: Request) -> int:
    token: str | None = req.cookies.get("access_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated: Missing access token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = jwt.decode(token, config.JWT_SECRET, config.JWT_ALGORITHM)  # pyright: ignore[reportAny, reportUnknownMemberType]

        user_id = payload.get("sub")  # pyright: ignore[reportAny]

        if user_id is None:
            raise InvalidTokenError("Token payload is missing 'sub'.")

        return int(user_id)  # pyright: ignore[reportAny]

    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed.",
            headers={"WWW-Authenticate": "Bearer"},
        )


def set_auth_cookie(user_id: int, response: Response) -> None:
    access_token: str = create_jwt(user_id)
    response.set_cookie("access_token", access_token, httponly=True, samesite="lax")
