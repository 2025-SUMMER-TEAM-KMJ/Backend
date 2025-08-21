# app/schemas/cover_letter.py
from datetime import datetime
from typing import Optional, Literal, List
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID, uuid4

class QnA(BaseModel):
    id: UUID = Field(default_factory=uuid4, description="문항에 대한 식별자")
    question: str = Field(..., description="자기소개서 문항")
    answer: str = Field(..., description="문항에 맞는 답변")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class CoverLetterCreate(BaseModel):
    """자기소개서 생성 요청"""
    title: str = Field(..., min_length=1, max_length=100, description="자기소개서 제목")
    type: Literal["profile", "job_posting"] = Field(..., description="자기소개서 타입")
    job_posting_id: Optional[str] = Field(None, description="공고 기반일 경우 해당 공고 id")
    qnas: Optional[List[QnA]] = Field(default=None, description="초기 문항 리스트")

class CoverLetterUpdate(BaseModel):
    """자기소개서 상위 메타 수정 요청 (부분 업데이트), 문항 수정은 별도 엔드포인트로 진행"""
    title: Optional[str] = Field(None, min_length=1, max_length=100)

class QnACreate(BaseModel):
    """자기소개서 개별 항목 생성 -> AI로 생성 진행"""
    question: str = Field(..., min_length=1, max_length=100, description="자기소개서 문항 질문")
    answer: Optional[str] = None

class QnAUpdate(BaseModel):
    """자기소개서 개별 항목 수정 -> 유저가 수정"""
    question: Optional[str]
    answer: Optional[str] = None

class CoverLetterResponse(BaseModel):
    """클라이언트 응답 모델"""
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    title: str
    type: Literal["profile", "job_posting"]
    job_posting_id: Optional[str] = None
    qnas: List[QnA]
    created_at: datetime
    updated_at: datetime
    strength: Optional[List[str]]
    weakness: Optional[List[str]]
    
    @classmethod
    def from_doc(cls, doc) -> "CoverLetterResponse":
        d = doc.dict() if hasattr(doc, "dict") else dict(doc)
        d["id"] = str(doc.id)
        d.pop("_id", None)
        return cls(**d)

class CoverLetterListResponse(BaseModel):
    total: int = Field(..., description="전체 개수")
    items: List[CoverLetterResponse] = Field(..., description="자기소개서 목록")
