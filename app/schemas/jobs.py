# app/schemas/jobs.py
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Literal, Optional

class JobSearchRequest(BaseModel):
    q: str = Field(..., description="자연어 검색 질의")
    offset: int = 0
    limit: int = 20

class JobDocument(BaseModel):
    # _id는 id(str)로 치환
    id: str
    # 스키마에 맞춘 주요 루트 필드들
    metadata: Dict[str, Any]
    status: Literal["active", "closed"]
    detail: Dict[str, Any]
    company: Dict[str, Any]
    externalUrl: Optional[str] = None
    due_time: Optional[str] = None
    skill_tags: Optional[List[str]] = None
    title_images: Optional[List[str]] = None

class JobSearchResponse(BaseModel):
    total: int
    offset: int
    limit: int
    items: List[JobDocument]
