from typing import Any
import bcrypt
from fastapi import HTTPException, Request, Response, status
import jwt
from datetime import UTC, datetime, timedelta
from jwt.exceptions import InvalidTokenError
from core.config import config


def toUtf8(string: str) -> bytes:
    return string.encode("utf-8")


def match_passwords(challenge: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(toUtf8(challenge), toUtf8(hashed_password))


def hash_password(password: str) -> str:
    return bcrypt.hashpw(toUtf8(password), bcrypt.gensalt(12)).decode("utf-8")


def create_jwt(username: str) -> str:
    expiry: datetime = datetime.now(UTC) + timedelta(hours=config.JWT_EXPIRY_IN_HOURS)
    payload: dict[str, str | datetime] = {"sub": username, "exp": expiry}
    return jwt.encode(payload, config.JWT_SECRET, config.JWT_ALGORITHM)  # pyright: ignore[reportUnknownMemberType]


def authenticate_request(req: Request) -> str:
    token: str | None = req.cookies.get("access_token")
    print(f"Received token: {token}")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated: Missing access token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return validate_jwt(token)

def validate_jwt(token: str) -> str:
    try:
        payload = jwt.decode(token, config.JWT_SECRET, config.JWT_ALGORITHM)  # pyright: ignore[reportAny, reportUnknownMemberType]
        username = payload.get("sub")  # pyright: ignore[reportAny]

        if type(username) is not str:  # pyright: ignore[reportAny]
            raise InvalidTokenError("Token payload is missing 'sub'.")

        return username

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

def cookie_parser(environ: dict[str, Any]) -> dict[str, str]:
    headers = environ.get("asgi.scope", {}).get("headers", [])
    cookies: dict[str, str] = {}
    for k, v in headers:
        if k == b"cookie":
            cookie_str = v.decode()
            for part in cookie_str.split("; "):
                if "=" in part:
                    name, val = part.split("=", 1)
                    cookies[name] = val
                    
    return cookies

def set_auth_cookie(username: str, response: Response) -> None:
    access_token: str = create_jwt(username)
    response.set_cookie("access_token", access_token, httponly=False, samesite="lax")
