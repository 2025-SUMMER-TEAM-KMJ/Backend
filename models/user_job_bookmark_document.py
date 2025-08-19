# app/models/user_job_bookmark_document.py
from datetime import datetime, timezone
from beanie import Document, Indexed
from pydantic import Field


class UserJobBookmarkDocument(Document):
    user_id: Indexed(str) = Field(...)   # UserDocument의 id (문자열)
    job_id: Indexed(str) = Field(...)  # JobPostingDocument의 id (문자열)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "user_job_bookmarks"
        indexes = [
            [("user_id", 1), ("job_id", 1)],  # 복합 키로 조회/유니크 관리 (유니크는 애플리케이션 레벨로 보완)
        ]
