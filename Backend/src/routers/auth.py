from fastapi.routing import APIRouter
from fastapi import HTTPException
from pydantic import BaseModel, Field
from Backend.src.utils.auth_utils import hash_password, match_passwords
from src.db import engine
from src.models import User
from sqlmodel import Session, select

router: APIRouter = APIRouter()

class Credentials(BaseModel):
  username: str = Field(min_length=3)
  password: str = Field(min_length=5)
  
@router.post("/login")
async def login(credentials: Credentials):
  with Session(engine) as session:
    statement = select(User).where(User.username == credentials.username)
    existing_user = session.exec(statement).first()
    
    if not existing_user:
      raise HTTPException(status_code=401, detail="Username not registered.")
    
    hashed_password: str = existing_user.password_hash
    
    if not match_passwords(credentials.password, hashed_password):
      raise HTTPException(status_code=401, detail="Invalid password.")
    
    
@router.post("/register")
async def register(credentials: Credentials) -> dict[str, str]:
  with Session(engine) as session:
    statement = select(User).where(User.username == credentials.username)
    existing_user= session.exec(statement).first()

    if existing_user:
      raise HTTPException(status_code=400, detail="Username already taken.")

    hashed_password: str = hash_password(credentials.password)
    user: User = User(username=credentials.username, password_hash=hashed_password)
    session.add(user)
    session.commit()
    session.refresh(user)
    
    return {"message": "User registered successfully"}