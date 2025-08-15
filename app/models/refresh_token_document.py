# app/models/refresh_token_document.py
# 보안상 좋은 방식은 아니지만 mvp 단계에서는 db에 저장 후 추후 보완 예정
from beanie import Document, Indexed
from pydantic import Field
from datetime import datetime, timezone

class RefreshTokenDocument(Document):
    user_id: Indexed(str)                 # 조회 자주 하므로 인덱스 권장
    token: Indexed(str, unique=True)      # 토큰값 유니크
    expires_at: Indexed(datetime, expireAfterSeconds=0) = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    class Settings:
        name = "refresh_tokens"  # 컬렉션명
