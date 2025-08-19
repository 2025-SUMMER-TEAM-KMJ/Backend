# app/models/cover_letter_document.py
from datetime import datetime, timezone
from typing import Optional, Literal, List
from beanie import Document, Indexed
from pydantic import Field, BaseModel
from uuid import UUID, uuid4

class QnA(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    question: str
    answer: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class CoverLetterDocument(Document):
    """
    사용자가 작성/생성한 자기소개서 문서
    - type: 'profile' | 'job_posting'
    - job_posting_id: 공고 기반일 때만 채움 (JobPostingDocument.id 문자열)
    """
    user_id: Indexed(str) = Field(...)  # UserDocument.id (str)
    title: str
    type: Literal["profile", "job_posting"]
    job_posting_id: Optional[str] = None
    strength: Optional[List[str]] = []
    weakness: Optional[List[str]] = []
    qnas: List[QnA] = Field(default_factory=list)

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "cover_letters"
        indexes = [
            [("user_id", 1), ("updated_at", -1)],
            [("user_id", 1), ("type", 1), ("updated_at", -1)],
        ]

