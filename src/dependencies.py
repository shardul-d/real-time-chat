from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_db_session
from utils.auth_utils import authenticate_request

AuthenticatedUsername = Annotated[str, Depends(authenticate_request)]
DBSessionDep = Annotated[AsyncSession, Depends(get_db_session)]
