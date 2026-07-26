from app.core.exceptions import EmailAlreadyExistsError, InvalidCredentialsError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.domain.user import User
from app.repositories.user_repository import UserRepositoryProtocol
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse


class AuthService:
    def __init__(self, user_repository: UserRepositoryProtocol) -> None:
        self._user_repository = user_repository

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

    @staticmethod
    def _build_token_response(user: User) -> TokenResponse:
        return TokenResponse(
            access_token=create_access_token(user.id),
            refresh_token=create_refresh_token(user.id),
        )
