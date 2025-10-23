import bcrypt
import jwt
from datetime import datetime, timezone, timedelta
from Backend.src.core.config import config

def toUtf8(string: str) -> bytes:
  return string.encode("utf-8")

def match_passwords(challenge: str, hashed_password: str) -> bool:
  return bcrypt.checkpw(toUtf8(challenge), toUtf8(hashed_password))
  
def hash_password(password: str) -> str:
  return bcrypt.hashpw(toUtf8(password), bcrypt.gensalt(12)).decode("utf-8")

def create_jwt(user_id: int) -> str:
  expiry: datetime = datetime.now(timezone.utc) + timedelta(hours=config.JWT_EXPIRY_IN_HOURS)
  payload: dict[str, int | datetime] = {"sub": user_id, "exp": expiry}
  return jwt.encode(payload, config.JWT_SECRET, config.JWT_ALGORITHM) #pyright: ignore[reportUnknownMemberType]

