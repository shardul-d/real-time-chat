import bcrypt
from fastapi import HTTPException, Request, Response, status
import jwt
from datetime import datetime, timezone, timedelta
from jwt.exceptions import InvalidTokenError
from src.core.config import config


def toUtf8(string: str) -> bytes:
    return string.encode("utf-8")


def match_passwords(challenge: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(toUtf8(challenge), toUtf8(hashed_password))


def hash_password(password: str) -> str:
    return bcrypt.hashpw(toUtf8(password), bcrypt.gensalt(12)).decode("utf-8")


def create_jwt(username: str) -> str:
    expiry: datetime = datetime.now(timezone.utc) + timedelta(
        hours=config.JWT_EXPIRY_IN_HOURS
    )
    payload: dict[str, str | datetime] = {"sub": username, "exp": expiry}
    return jwt.encode(payload, config.JWT_SECRET, config.JWT_ALGORITHM)  # pyright: ignore[reportUnknownMemberType]


def validate_jwt(req: Request) -> bool:
    token: str | None = req.cookies.get("access_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated: Missing access token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = jwt.decode(token, config.JWT_SECRET, config.JWT_ALGORITHM)  # pyright: ignore[reportAny, reportUnknownMemberType]
        username = payload.get("sub")  # pyright: ignore[reportAny]

        if username is None:
            raise InvalidTokenError("Token payload is missing 'sub'.")

        return True

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


def set_auth_cookie(username: str, response: Response) -> None:
    access_token: str = create_jwt(username)
    response.set_cookie("access_token", access_token, httponly=True, samesite="lax")
