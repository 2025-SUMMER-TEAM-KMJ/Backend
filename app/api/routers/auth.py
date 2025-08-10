# app/api/routers/auth.py
from fastapi import APIRouter, Depends, Response, HTTPException, Cookie
from pymongo.collection import Collection
from app.database import get_collection
from app.schemas.auth import LoginRequest, TokenResponse
from app.services.auth import login
from app.core.jwt_utils import create_access_token, REFRESH_TOKEN_EXPIRE_DAYS
from app.crud.token import find_refresh_token, delete_refresh_token

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=TokenResponse)
def login_endpoint(
    creds: LoginRequest,
    resp: Response,
    users_col: Collection = Depends(get_collection("users")),
    tokens_col: Collection = Depends(get_collection("refresh_tokens")),
):
    return login(users_col, tokens_col, creds, resp)

@router.post("/refresh", response_model=TokenResponse)
def refresh_endpoint(
    resp: Response,
    refresh_token: str | None = Cookie(default=None, alias="refresh_token"),
    users_col: Collection = Depends(get_collection("users")),
    tokens_col: Collection = Depends(get_collection("refresh_tokens")),
):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="리프레시 토큰이 없습니다.")

    # 토큰 DB에서 조회
    entry = tokens_col.find_one({"token": refresh_token})
    if not entry:
        raise HTTPException(status_code=401, detail="유효하지 않은 리프레시 토큰입니다.")

    # 만료 체크 -> 추후 TTL 인덱스로 자동 삭제로 코드 변경 가능
    from datetime import datetime, timezone
    if entry.get("expires_at") and entry["expires_at"] < datetime.now(timezone.utc):
        delete_refresh_token(tokens_col, entry["user_id"], refresh_token)
        raise HTTPException(status_code=401, detail="리프레시 토큰이 만료되었습니다.")

    # 새 액세스 토큰 발급
    new_access = create_access_token(sub=entry["user_id"])

    # 회전: 기존 RT 폐기하고 새 RT 발급/세팅 -> 추후 진행이 필요할 경우 추가

    return {"access_token": new_access, "token_type": "bearer"}

@router.post("/logout")
def logout_endpoint(
    resp: Response,
    refresh_token: str | None = Cookie(default=None, alias="refresh_token"),
    tokens_col: Collection = Depends(get_collection("refresh_tokens")),
):
    # 보유한 리프레시 토큰 제거
    if refresh_token:
        tokens_col.delete_one({"token": refresh_token})
        resp.delete_cookie("refresh_token", path="/")
    return {"message": "로그아웃 되었습니다."}
