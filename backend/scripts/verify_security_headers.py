"""Verify required production security headers on an HTTP endpoint."""

import argparse
from collections.abc import Mapping, Sequence

import httpx

REQUIRED_HEADERS = (
    "X-Frame-Options",
    "X-Content-Type-Options",
    "Strict-Transport-Security",
    "Content-Security-Policy",
)


def check_required_headers(headers: Mapping[str, str]) -> list[str]:
    """Return required security headers missing from a case-insensitive mapping."""
    present = {name.lower() for name in headers}
    return [name for name in REQUIRED_HEADERS if name.lower() not in present]


def main(argv: Sequence[str] | None = None) -> int:
    """Run the security header verification CLI."""
    parser = argparse.ArgumentParser(description="Verify production security headers")
    parser.add_argument("--url", default="http://localhost:8000/health")
    args = parser.parse_args(argv)

    try:
        response = httpx.get(args.url, timeout=10.0)
        response.raise_for_status()
    except httpx.HTTPError as exc:
        print(f"FAIL request: {exc}")
        return 2

    missing = check_required_headers(response.headers)
    for header in REQUIRED_HEADERS:
        status = "FAIL" if header in missing else "PASS"
        print(f"{status} {header}")

    if missing:
        print("Missing required headers: " + ", ".join(missing))
        return 1

    print("All required security headers are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
