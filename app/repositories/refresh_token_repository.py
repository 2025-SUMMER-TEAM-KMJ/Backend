# app/repositories/refresh_token_repository.py
from datetime import datetime, timezone, timedelta
from typing import Optional
from app.models.refresh_token_document import RefreshTokenDocument

class RefreshTokenRepository:
    # 생성
    async def save(self, user_id: str, token: str, days: int) -> RefreshTokenDocument:
        """
        토큰을 생성합니다.
        - user_id와 토큰 문자열, 만료일(expires_at)을 함께 저장합니다.
        - 반환값: 방금 저장된 RefreshTokenDocument
        """
        exp = datetime.now(timezone.utc) + timedelta(days=days)
        doc = RefreshTokenDocument(user_id=user_id, token=token, expires_at=exp)
        await doc.insert()
        return doc

    # 조회 (토큰 값으로 단건 조회)
    async def find_by_token(self, token: str) -> Optional[RefreshTokenDocument]:
        """
        토큰 문자열로 리프레시 토큰 문서를 조회합니다.
        - 없으면 None 반환
        """
        return await RefreshTokenDocument.find_one(RefreshTokenDocument.token == token)

    # 삭제 (토큰 값 기준)
    async def delete_by_token(self, token: str) -> None:
        """
        토큰 문자열에 해당하는 리프레시 토큰을 삭제합니다.
        - 대상이 없으면 아무 동작도 하지 않습니다.
        """
        doc = await self.find_by_token(token)
        if doc:
            await doc.delete()

    # 사용자 기준 전체 삭제 (로그아웃 올클리어 등)
    async def delete_all_by_user(self, user_id: str) -> None:
        """
        특정 사용자(user_id)의 모든 리프레시 토큰을 삭제합니다.
        - 일괄 로그아웃(모든 세션 종료) 시 사용합니다.
        """
        await RefreshTokenDocument.find(RefreshTokenDocument.user_id == user_id).delete()

    # 토큰 회전
    async def replace_token(self, old_token: str, new_token: str, days: int) -> Optional[RefreshTokenDocument]:
        """
        액세스 토큰이 만료되었을 경우 액세스 토큰을 발급하며 리프레시 토큰을 회전합니다.
        - 리프레시 토큰을 새로운 리프레시 토큰으로 교체합니다.
        """
        doc = await self.find_by_token(old_token)
        if not doc:
            return None
        doc.token = new_token
        doc.expires_at = datetime.now(timezone.utc) + timedelta(days=days)
        await doc.save()
        return doc
