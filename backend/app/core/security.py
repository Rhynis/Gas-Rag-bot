"""Security utilities: JWT tokens and password hashing."""

import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from jwt import InvalidTokenError
from passlib.context import CryptContext

from app.core.config import get_settings
from app.core.exceptions import UnauthorizedException

settings = get_settings()

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=settings.BCRYPT_ROUNDS,
)


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    subject: str,
    additional_claims: dict[str, Any] | None = None,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a JWT access token."""
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    issued_at = datetime.now(UTC)
    expire = issued_at + expires_delta
    to_encode = {
        "sub": str(subject),
        "exp": expire,
        "iat": issued_at,
        "type": "access",
        "jti": secrets.token_urlsafe(32),
        **(additional_claims or {}),
    }
    return str(jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM))


def create_refresh_token(subject: str) -> str:
    """Create a JWT refresh token with longer expiration."""
    issued_at = datetime.now(UTC)
    expire = issued_at + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {
        "sub": str(subject),
        "exp": expire,
        "iat": issued_at,
        "type": "refresh",
        "jti": secrets.token_urlsafe(32),
    }
    return str(jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM))


def decode_token(token: str) -> dict[str, Any]:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return dict(payload)
    except InvalidTokenError as exc:
        raise UnauthorizedException(f"Invalid token: {exc}", error_code="invalid_token") from exc


def generate_password_reset_token() -> str:
    """Generate a URL-safe random token for password reset."""
    return secrets.token_urlsafe(32)
