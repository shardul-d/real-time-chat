from typing import Annotated
from fastapi import Depends
from src.utils.auth_utils import validate_jwt_and_get_user_id

AuthenticatedUser = Annotated[int, Depends(validate_jwt_and_get_user_id)]
