from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .config import get_settings

bearer = HTTPBearer(auto_error=False)


def _b64encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _b64decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def create_access_token(subject: str) -> tuple[str, int]:
    settings = get_settings()
    expires_at = int(time.time()) + (settings.token_ttl_minutes * 60)
    payload = _b64encode(json.dumps({"sub": subject, "exp": expires_at}, separators=(",", ":")).encode())
    signature = _b64encode(hmac.new(settings.jwt_secret.encode(), payload.encode(), hashlib.sha256).digest())
    return f"{payload}.{signature}", expires_at


def verify_access_token(token: str) -> str:
    settings = get_settings()
    try:
        payload_part, signature_part = token.split(".", 1)
        expected = _b64encode(hmac.new(settings.jwt_secret.encode(), payload_part.encode(), hashlib.sha256).digest())
        if not hmac.compare_digest(signature_part, expected):
            raise ValueError("bad signature")
        payload = json.loads(_b64decode(payload_part))
        if int(payload["exp"]) < int(time.time()):
            raise ValueError("expired")
        return str(payload["sub"])
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


def require_auth(credentials: HTTPAuthorizationCredentials | None = Depends(bearer)) -> str:
    settings = get_settings()
    if not settings.auth_required:
        return "development"
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return verify_access_token(credentials.credentials)


def verify_admin_credentials(phone: str, pin: str) -> bool:
    settings = get_settings()
    return hmac.compare_digest(phone.strip(), settings.admin_phone.strip()) and hmac.compare_digest(pin, settings.admin_pin)
