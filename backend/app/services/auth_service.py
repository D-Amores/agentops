from uuid import UUID

import redis.asyncio as redis
from jwt import InvalidTokenError

from app.core.exceptions import EmailAlreadyExistsError, InvalidCredentialsError
from app.core.security import (
    TokenType,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    is_token_revoked,
    revoke_token,
    verify_password,
)
from app.domain.user import User
from app.repositories.user_repository import UserRepositoryProtocol
from app.schemas.auth import (
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
)


class AuthService:
    def __init__(self, user_repository: UserRepositoryProtocol, redis_client: redis.Redis) -> None:
        self._user_repository = user_repository
        self._redis_client = redis_client

    async def register(self, data: RegisterRequest) -> TokenResponse:
        existing_user = await self._user_repository.get_by_email(data.email)

        if existing_user is not None:
            raise EmailAlreadyExistsError(data.email)

        user = User(email=data.email, hashed_password=hash_password(data.password))
        created_user = await self._user_repository.create(user)
        return self._build_token_response(created_user)

    async def login(self, data: LoginRequest) -> TokenResponse:
        user = await self._user_repository.get_by_email(data.email)

        if user is None or not verify_password(data.password, user.hashed_password):
            raise InvalidCredentialsError()

        return self._build_token_response(user)

    async def refresh(self, data: RefreshRequest) -> TokenResponse:
        try:
            payload = decode_token(data.refresh_token)
        except InvalidTokenError as exc:
            raise InvalidCredentialsError() from exc

        if payload.get("type") != TokenType.REFRESH:
            raise InvalidCredentialsError()

        jti = payload.get("jti")
        if jti and await is_token_revoked(jti, self._redis_client):
            raise InvalidCredentialsError()

        user = await self._user_repository.get_by_id(UUID(payload["sub"]))
        if user is None:
            raise InvalidCredentialsError()

        await revoke_token(payload, self._redis_client)  # rotation

        return self._build_token_response(user)

    async def logout(self, access_token: str, data: LogoutRequest) -> None:
        for token in filter(None, [access_token, data.refresh_token]):
            try:
                payload = decode_token(token)
            except InvalidTokenError:
                continue
            await revoke_token(payload, self._redis_client)

    @staticmethod
    def _build_token_response(user: User) -> TokenResponse:
        return TokenResponse(
            access_token=create_access_token(user.id),
            refresh_token=create_refresh_token(user.id),
        )
