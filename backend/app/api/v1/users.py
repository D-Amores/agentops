from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.domain.user import User
from app.schemas.auth import UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    return current_user
