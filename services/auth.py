# app/services/auth.py
from datetime import datetime, timezone
from typing import Optional
from fastapi import HTTPException, Response, status

from schemas.auth import LoginRequest, TokenResponse
from core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    REFRESH_TOKEN_EXPIRE_DAYS,
)
from repositories.user_repository import UserRepository
from repositories.refresh_token_repository import RefreshTokenRepository

class AuthService:
    """
    인증 서비스
    - 로그인: 이메일/비밀번호 확인 → AccessToken 발급 + RefreshToken 발급/저장 + 쿠키 세팅
    - 재발급: 쿠키의 RefreshToken 검증 → AccessToken 재발급 (+ RT 회전)
    - 로그아웃: 쿠키/DB의 RefreshToken 제거
    """
    def __init__(
        self,
        user_repo: Optional[UserRepository] = None,
        rt_repo: Optional[RefreshTokenRepository] = None,
    ):
        self.user_repo = user_repo or UserRepository()
        self.rt_repo = rt_repo or RefreshTokenRepository()

    async def login(self, creds: LoginRequest, resp: Response) -> TokenResponse:
        """
        로그인 → AccessToken + RefreshToken 발급
        - 응답 바디는 TokenResponse
        - 리프레시 토큰은 HttpOnly 쿠키로 세팅
        """
        user = await self.user_repo.get_by_email(str(creds.email))
        if not user or not verify_password(creds.password, user.password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="이메일 또는 비밀번호가 올바르지 않습니다.")

        user_id = str(user.id)

        # Access Token
        access_token = create_access_token(sub=user_id, extra_claims={"email": user.email})

        # Refresh Token (발급 + 저장)
        refresh_token = create_refresh_token()
        await self.rt_repo.save(user_id=user_id, token=refresh_token, days=REFRESH_TOKEN_EXPIRE_DAYS)

        # RT 쿠키 세팅
        resp.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,          # 운영 HTTPS 설정
            samesite="lax",
            max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
            path="/",
        )

        return TokenResponse(access_token=access_token)

    async def reissue(self, resp: Response, refresh_token: Optional[str]) -> TokenResponse:
        """
        AccessToken 재발급 + RefreshToken 회전
        - 응답 바디는 TokenResponse
        - 새 RT로 회전하여 쿠키 갱신
        """
        if not refresh_token:
            raise HTTPException(status_code=401, detail="리프레시 토큰이 없습니다.")

        entry = await self.rt_repo.find_by_token(refresh_token)
        if not entry:
            raise HTTPException(status_code=401, detail="유효하지 않은 리프레시 토큰입니다.")

        now = datetime.now(timezone.utc)
        if entry.expires_at and entry.expires_at < now:
            await self.rt_repo.delete_by_token(refresh_token)
            raise HTTPException(status_code=401, detail="리프레시 토큰이 만료되었습니다.")

        # 새 Access Token
        new_access_token = create_access_token(sub=entry.user_id)

        # RT 회전
        new_refresh_token = create_refresh_token()
        await self.rt_repo.replace_token(
            old_token=refresh_token,
            new_token=new_refresh_token,
            days=REFRESH_TOKEN_EXPIRE_DAYS,
        )

        # RT 쿠키 갱신
        resp.set_cookie(
            key="refresh_token",
            value=new_refresh_token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
            path="/",
        )

        return TokenResponse(access_token=new_access_token)

    async def logout(self, resp: Response, refresh_token: Optional[str]) -> dict:
        """현재 세션 로그아웃 (쿠키/DB의 해당 RT 제거)"""
        if refresh_token:
            await self.rt_repo.delete_by_token(refresh_token)
            resp.delete_cookie("refresh_token", path="/")
        return {"message": "로그아웃 되었습니다."}

    async def logout_all(self, resp: Response, user_id: str) -> dict:
        """모든 기기 로그아웃 (해당 유저의 모든 RT 제거)"""
        await self.rt_repo.delete_all_by_user(user_id)
        resp.delete_cookie("refresh_token", path="/")
        return {"message": "모든 세션이 로그아웃 처리되었습니다."}
