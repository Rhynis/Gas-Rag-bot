"""Tests for security utilities."""

from datetime import timedelta

import pytest

from app.core.exceptions import UnauthorizedException
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)


def test_password_hash_returns_different_hash_each_time() -> None:
    """Hashing the same password twice should produce different hashes."""
    first = get_password_hash("CorrectHorseBatteryStaple!")
    second = get_password_hash("CorrectHorseBatteryStaple!")
    assert first != second


def test_verify_password_returns_true_for_correct_password() -> None:
    """Password verification should pass for the correct password."""
    hashed = get_password_hash("CorrectHorseBatteryStaple!")
    assert verify_password("CorrectHorseBatteryStaple!", hashed) is True


def test_verify_password_returns_false_for_wrong_password() -> None:
    """Password verification should fail for a wrong password."""
    hashed = get_password_hash("CorrectHorseBatteryStaple!")
    assert verify_password("WrongPassword!", hashed) is False


def test_create_access_token_returns_valid_jwt() -> None:
    """Access token should decode into the expected payload."""
    token = create_access_token("user-123", {"role": "admin"})
    payload = decode_token(token)
    assert payload["sub"] == "user-123"
    assert payload["role"] == "admin"
    assert payload["type"] == "access"


def test_decode_token_returns_payload_for_valid_token() -> None:
    """Valid tokens should decode successfully."""
    token = create_access_token("user-123")
    payload = decode_token(token)
    assert payload["sub"] == "user-123"


def test_decode_token_raises_for_expired_token() -> None:
    """Expired tokens should raise UnauthorizedException."""
    token = create_access_token("user-123", expires_delta=timedelta(seconds=-1))
    with pytest.raises(UnauthorizedException):
        decode_token(token)


def test_decode_token_raises_for_invalid_signature() -> None:
    """Malformed tokens should raise UnauthorizedException."""
    with pytest.raises(UnauthorizedException):
        decode_token("not.a.valid.jwt")


def test_refresh_token_has_jti_claim() -> None:
    """Refresh tokens should include a JTI claim."""
    token = create_refresh_token("user-123")
    payload = decode_token(token)
    assert payload["type"] == "refresh"
    assert payload["jti"]
