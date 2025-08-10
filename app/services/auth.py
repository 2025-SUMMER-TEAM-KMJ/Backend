# app/services/auth.py
from fastapi import HTTPException, Response
from pymongo.collection import Collection
from app.schemas.auth import LoginRequest
from app.crud.user import get_user_by_email
from app.core.security import verify_password
from app.core.jwt_utils import create_access_token, create_refresh_token, REFRESH_TOKEN_EXPIRE_DAYS
from app.crud.token import save_refresh_token

def login(users_col: Collection, tokens_col: Collection, creds: LoginRequest, resp: Response) -> dict:
    user = get_user_by_email(users_col, creds.email)
    if not user or not verify_password(creds.password, user.get("hashed_password", "")):
        raise HTTPException(status_code=400, detail="이메일 또는 비밀번호가 올바르지 않습니다.")

    user_id = str(user["_id"])
    access_token = create_access_token(sub=user_id, extra_claims={"email": user["email"]})

    refresh_token = create_refresh_token()
    save_refresh_token(tokens_col, user_id, refresh_token, REFRESH_TOKEN_EXPIRE_DAYS)

    # HttpOnly 쿠키로 전달
    resp.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        path="/",
    )

    return {"access_token": access_token, "token_type": "bearer"}
