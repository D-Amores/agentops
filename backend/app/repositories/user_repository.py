from typing import Protocol
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.user import User
from app.models.user import UserModel


class UserRepositoryProtocol(Protocol):
    async def create(self, user: User) -> User: ...

    async def get_by_id(self, user_id: UUID) -> User | None: ...

    async def get_by_email(self, email: str) -> User | None: ...


class SQLAlchemyUserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, user: User) -> User:
        model = self._to_model(user)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def get_by_id(self, user_id: UUID) -> User | None:
        model = await self._session.get(UserModel, user_id)
        return self._to_domain(model) if model else None

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(UserModel).where(UserModel.email == email)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    @staticmethod
    def _to_domain(model: UserModel) -> User:
        return User(
            id=model.id,
            email=model.email,
            hashed_password=model.hashed_password,
            role=model.role,
            is_active=model.is_active,
            created_at=model.created_at,
        )

    @staticmethod
    def _to_model(user: User) -> UserModel:
        return UserModel(
            id=user.id,
            email=user.email,
            hashed_password=user.hashed_password,
            role=user.role,
            is_active=user.is_active,
        )
