from fastapi import APIRouter, HTTPException, status

from ..schemas import LoginRequest, LoginResponse
from ..security import create_access_token, verify_admin_credentials

router = APIRouter(prefix="/api")


@router.post("/auth/login", response_model=LoginResponse)
def login(payload: LoginRequest):
    if not verify_admin_credentials(payload.phone, payload.pin):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid phone number or PIN")
    token, expires_at = create_access_token(payload.phone)
    return LoginResponse(access_token=token, expires_at=expires_at)
