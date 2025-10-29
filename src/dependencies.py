from typing import Annotated
from fastapi import Depends
from sqlmodel import Session
from src.utils.auth_utils import validate_jwt

AuthenticatedUsername = Annotated[str, Depends(validate_jwt)]
db = Annotated[Session, Depends()]
