"""Tests for security header verification script."""

from fastapi.testclient import TestClient
from pytest import MonkeyPatch

from app.core.config import get_settings
from app.main import create_app
from scripts.verify_security_headers import check_required_headers


def test_check_required_headers_all_present() -> None:
    headers = {
        "X-Frame-Options": "DENY",
        "X-Content-Type-Options": "nosniff",
        "Strict-Transport-Security": "max-age=31536000",
        "Content-Security-Policy": "default-src 'self'",
    }

    assert check_required_headers(headers) == []


def test_check_required_headers_missing() -> None:
    headers = {
        "X-Frame-Options": "DENY",
        "X-Content-Type-Options": "nosniff",
        "Strict-Transport-Security": "max-age=31536000",
    }

    assert check_required_headers(headers) == ["Content-Security-Policy"]


def test_check_required_headers_case_insensitive() -> None:
    headers = {
        "x-frame-options": "DENY",
        "x-content-type-options": "nosniff",
        "strict-transport-security": "max-age=31536000",
        "content-security-policy": "default-src 'self'",
    }

    assert check_required_headers(headers) == []


def test_real_app_emits_all_security_headers(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv("ENVIRONMENT", "production")
    get_settings.cache_clear()
    try:
        app = create_app()
        response = TestClient(app).get("/health")
    finally:
        get_settings.cache_clear()

    assert response.status_code == 200
    assert check_required_headers(response.headers) == []
