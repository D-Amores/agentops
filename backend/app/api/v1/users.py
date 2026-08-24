from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, require_role
from app.domain.user import User, UserRole
from app.schemas.auth import UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    return current_user


@router.get("/admin-only", response_model=UserResponse)
async def admin_only_endpoint(
    current_user: Annotated[User, Depends(require_role(UserRole.ADMIN))],
) -> User:
    return current_user
