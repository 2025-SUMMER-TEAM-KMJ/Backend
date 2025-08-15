# app/deps/auth.py
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from core.security import decode_token
from models.user_document import UserDocument

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")  # 클라이언트 문서화용

async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> str:
    """
    Authorization: Bearer <access_token> 에서 user_id(sub) 추출 및 검증.
    실제 유저 존재 여부도 확인.
    """
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="인증이 필요합니다.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        user_id: str | None = payload.get("sub")
        if not user_id:
            raise credentials_exc
    except Exception:
        raise credentials_exc

    user = await UserDocument.get(user_id)
    if not user:
        raise credentials_exc
    return user_id

async def get_optional_user_id(
    token: Optional[str] = Depends(oauth2_scheme)
) -> Optional[str]:
    """
    로그인하지 않은 경우 None 반환.
    로그인한 경우 user_id 반환.
    """
    if not token:
        return None

    try:
        payload = decode_token(token)
        user_id: str | None = payload.get("sub")
        if not user_id:
            return None
        user = await UserDocument.get(user_id)
        if not user:
            return None
        return user_id
    except Exception:
        return None
