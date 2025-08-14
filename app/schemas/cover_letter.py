# app/schemas/cover_letter.py
from datetime import datetime
from typing import Optional, Literal, List
from pydantic import BaseModel, Field, ConfigDict

class CoverLetterCreate(BaseModel):
    """자기소개서 생성 요청"""
    title: str = Field(..., min_length=1, max_length=100, description="자기소개서 제목")
    content: str = Field(..., min_length=1, description="자기소개서 내용 (AI로 생성된 결과를 넣어도 됨)")
    type: Literal["profile", "job_posting"] = Field(..., description="자기소개서 타입")
    job_posting_id: Optional[str] = Field(None, description="공고 기반일 경우 해당 공고 id")

class CoverLetterUpdate(BaseModel):
    """자기소개서 수정 요청 (부분 업데이트)"""
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    content: Optional[str] = Field(None, min_length=1)

class CoverLetterResponse(BaseModel):
    """클라이언트 응답 모델"""
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    title: str
    content: str
    type: Literal["profile", "job_posting"]
    job_posting_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_doc(cls, doc) -> "CoverLetterResponse":
        d = doc.dict() if hasattr(doc, "dict") else dict(doc)
        d["id"] = str(doc.id)
        d.pop("_id", None)
        return cls(**d)

class CoverLetterListResponse(BaseModel):
    total: int = Field(..., description="전체 개수")
    items: List[CoverLetterResponse] = Field(..., description="자기소개서 목록")