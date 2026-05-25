"""Tests for AuthService."""

from typing import Any

import pytest

from app.core.exceptions import ConflictException, UnauthorizedException, ValidationException
from app.core.security import decode_token
from app.services import auth_service as auth_module
from app.services.auth_service import AuthService

pytestmark = pytest.mark.asyncio

PASSWORD = "StrongPass123!"
NEW_PASSWORD = "NewStrongPass123!"


@pytest.fixture(autouse=True)
def fast_password_hashing(monkeypatch: pytest.MonkeyPatch) -> None:
    """Patch bcrypt helpers to keep service tests fast."""

    def fake_hash(password: str) -> str:
        return f"hashed:{password}"

    def fake_verify(password: str, hashed_password: str) -> bool:
        return hashed_password == f"hashed:{password}"

    monkeypatch.setattr(auth_module, "get_password_hash", fake_hash)
    monkeypatch.setattr(auth_module, "verify_password", fake_verify)


@pytest.fixture
def auth_service(fake_user_repository: Any, mock_redis: Any) -> AuthService:
    """Return an AuthService with fake dependencies."""
    return AuthService(fake_user_repository, mock_redis)


async def test_register_creates_user_with_hashed_password(auth_service: AuthService) -> None:
    user = await auth_service.register_user("A@Example.com", PASSWORD, "Nguyen Van A", "0901234567")

    assert user.hashed_password == f"hashed:{PASSWORD}"
    assert user.role == "customer"


async def test_register_lowercases_email(auth_service: AuthService) -> None:
    user = await auth_service.register_user("USER@Example.com", PASSWORD)

    assert user.email == "user@example.com"


async def test_register_raises_on_duplicate_email(auth_service: AuthService) -> None:
    await auth_service.register_user("user@example.com", PASSWORD)

    with pytest.raises(ConflictException):
        await auth_service.register_user("USER@example.com", PASSWORD)


async def test_login_returns_tokens_on_correct_credentials(auth_service: AuthService) -> None:
    user = await auth_service.register_user("user@example.com", PASSWORD)

    result = await auth_service.login_user("user@example.com", PASSWORD)

    assert result.user.id == user.id
    assert decode_token(result.access_token)["type"] == "access"
    assert decode_token(result.refresh_token)["type"] == "refresh"


async def test_login_raises_on_wrong_password(auth_service: AuthService) -> None:
    await auth_service.register_user("user@example.com", PASSWORD)

    with pytest.raises(UnauthorizedException):
        await auth_service.login_user("user@example.com", "wrong")


async def test_login_increments_failed_counter(auth_service: AuthService, mock_redis: Any) -> None:
    await auth_service.register_user("user@example.com", PASSWORD)

    with pytest.raises(UnauthorizedException):
        await auth_service.login_user("user@example.com", "wrong")

    assert await mock_redis.get("failed_login:user@example.com") == "1"


async def test_login_locks_account_after_5_fails(
    auth_service: AuthService,
    mock_redis: Any,
) -> None:
    await auth_service.register_user("user@example.com", PASSWORD)

    for _ in range(5):
        with pytest.raises(UnauthorizedException):
            await auth_service.login_user("user@example.com", "wrong")

    assert await mock_redis.get("lockout:user@example.com") == "1"


async def test_locked_account_cannot_login(auth_service: AuthService) -> None:
    await auth_service.register_user("user@example.com", PASSWORD)
    await auth_service.track_failed_login("user@example.com")
    await auth_service.track_failed_login("user@example.com")
    await auth_service.track_failed_login("user@example.com")
    await auth_service.track_failed_login("user@example.com")
    await auth_service.track_failed_login("user@example.com")

    with pytest.raises(UnauthorizedException) as exc_info:
        await auth_service.login_user("user@example.com", PASSWORD)

    assert exc_info.value.error_code == "account_locked"


async def test_login_clears_failed_counter_on_success(
    auth_service: AuthService,
    mock_redis: Any,
) -> None:
    await auth_service.register_user("user@example.com", PASSWORD)
    with pytest.raises(UnauthorizedException):
        await auth_service.login_user("user@example.com", "wrong")

    await auth_service.login_user("user@example.com", PASSWORD)

    assert await mock_redis.get("failed_login:user@example.com") is None


async def test_refresh_token_rotates_correctly(auth_service: AuthService, mock_redis: Any) -> None:
    await auth_service.register_user("user@example.com", PASSWORD)
    first = await auth_service.login_user("user@example.com", PASSWORD)

    second = await auth_service.refresh_access_token(first.refresh_token)

    assert second.refresh_token != first.refresh_token
    old_jti = decode_token(first.refresh_token)["jti"]
    assert await mock_redis.get(f"blacklist:{old_jti}") == "1"


async def test_logout_blacklists_token(auth_service: AuthService, mock_redis: Any) -> None:
    await auth_service.register_user("user@example.com", PASSWORD)
    result = await auth_service.login_user("user@example.com", PASSWORD)

    assert await auth_service.logout_user(result.access_token) is True

    jti = decode_token(result.access_token)["jti"]
    assert await mock_redis.get(f"blacklist:{jti}") == "1"


async def test_blacklisted_token_rejected(auth_service: AuthService) -> None:
    await auth_service.register_user("user@example.com", PASSWORD)
    result = await auth_service.login_user("user@example.com", PASSWORD)
    await auth_service.logout_user(result.access_token)

    with pytest.raises(UnauthorizedException):
        await auth_service.verify_token(result.access_token)


async def test_change_password_invalidates_old_tokens(auth_service: AuthService) -> None:
    user = await auth_service.register_user("user@example.com", PASSWORD)
    result = await auth_service.login_user("user@example.com", PASSWORD)

    assert await auth_service.change_password(user.id, PASSWORD, NEW_PASSWORD, result.access_token)

    with pytest.raises(UnauthorizedException):
        await auth_service.verify_token(result.access_token)
    with pytest.raises(UnauthorizedException):
        await auth_service.login_user("user@example.com", PASSWORD)
    assert await auth_service.login_user("user@example.com", NEW_PASSWORD)


async def test_password_reset_flow_end_to_end(
    auth_service: AuthService,
    mock_redis: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    user = await auth_service.register_user("user@example.com", PASSWORD)
    monkeypatch.setattr(auth_module, "generate_password_reset_token", lambda: "reset-token")

    assert await auth_service.request_password_reset("user@example.com") is True
    assert await mock_redis.get("password_reset:reset-token") == str(user.id)
    assert await auth_service.reset_password("reset-token", NEW_PASSWORD) is True
    assert await mock_redis.get("password_reset:reset-token") is None
    assert await auth_service.login_user("user@example.com", NEW_PASSWORD)


async def test_password_reset_unknown_email_returns_success(auth_service: AuthService) -> None:
    assert await auth_service.request_password_reset("missing@example.com") is True


async def test_reset_password_rejects_invalid_token(auth_service: AuthService) -> None:
    with pytest.raises(ValidationException):
        await auth_service.reset_password("missing-token", NEW_PASSWORD)
