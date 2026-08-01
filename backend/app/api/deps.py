from collections.abc import Callable, Coroutine
from typing import Annotated, Any
from uuid import UUID

import redis.asyncio as redis
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.redis import get_redis
from app.core.security import TokenType, decode_token, is_token_revoked
from app.domain.user import User, UserRole
from app.repositories.user_repository import SQLAlchemyUserRepository
from app.services.auth_service import AuthService


def get_user_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SQLAlchemyUserRepository:
    return SQLAlchemyUserRepository(db)


def get_auth_service(
    user_repository: Annotated[SQLAlchemyUserRepository, Depends(get_user_repository)],
    redis_client: Annotated[redis.Redis, Depends(get_redis)],
) -> AuthService:
    return AuthService(user_repository, redis_client)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_repository: Annotated[SQLAlchemyUserRepository, Depends(get_user_repository)],
    redis_client: Annotated[redis.Redis, Depends(get_redis)],
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(token)
    except InvalidTokenError as exc:
        raise credentials_exception from exc

    if payload.get("type") != TokenType.ACCESS:
        raise credentials_exception

    jti = payload.get("jti")
    if jti and await is_token_revoked(jti, redis_client):
        raise credentials_exception

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    user = await user_repository.get_by_id(UUID(user_id))
    if user is None:
        raise credentials_exception

    return user


def require_role(*allowed_roles: UserRole) -> Callable[..., Coroutine[Any, Any, User]]:
    async def role_checker(current_user: Annotated[User, Depends(get_current_user)]) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action",
            )
        return current_user

    return role_checker
