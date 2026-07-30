import pytest

from app.core.exceptions import EmailAlreadyExistsError, InvalidCredentialsError
from app.schemas.auth import LoginRequest, RegisterRequest
from app.services.auth_service import AuthService
from tests.fakes import FakeUserRepository


@pytest.fixture
def auth_service() -> AuthService:
    return AuthService(FakeUserRepository())


async def test_register_creates_user_and_returns_tokens(auth_service: AuthService) -> None:
    data = RegisterRequest(email="alice@example.com", password="securepass123")

    result = await auth_service.register(data)

    assert result.access_token
    assert result.refresh_token
    assert result.token_type == "bearer"


async def test_register_with_duplicate_email_raises_error(auth_service: AuthService) -> None:
    data = RegisterRequest(email="bob@example.com", password="securepass123")
    await auth_service.register(data)

    with pytest.raises(EmailAlreadyExistsError):
        await auth_service.register(data)


async def test_login_with_correct_credentials_returns_tokens(auth_service: AuthService) -> None:
    register_data = RegisterRequest(email="carol@example.com", password="securepass123")
    await auth_service.register(register_data)

    login_data = LoginRequest(email="carol@example.com", password="securepass123")
    result = await auth_service.login(login_data)

    assert result.access_token
    assert result.refresh_token


async def test_login_with_wrong_password_raises_error(auth_service: AuthService) -> None:
    register_data = RegisterRequest(email="dave@example.com", password="securepass123")
    await auth_service.register(register_data)

    login_data = LoginRequest(email="dave@example.com", password="wrongpassword")

    with pytest.raises(InvalidCredentialsError):
        await auth_service.login(login_data)


async def test_login_with_nonexistent_email_raises_error(auth_service: AuthService) -> None:
    login_data = LoginRequest(email="nobody@example.com", password="whatever123")

    with pytest.raises(InvalidCredentialsError):
        await auth_service.login(login_data)
