from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.user_repository import SQLAlchemyUserRepository
from app.services.auth_service import AuthService


def get_user_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SQLAlchemyUserRepository:
    return SQLAlchemyUserRepository(db)


def get_auth_service(
    user_repository: Annotated[SQLAlchemyUserRepository, Depends(get_user_repository)],
) -> AuthService:
    return AuthService(user_repository)
