# app/api/routers/cover_letter.py
from http import HTTPStatus
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, HTTPException, status
from deps.auth import get_current_user_id
from schemas.cover_letter import (
    CoverLetterCreate, CoverLetterUpdate,
    CoverLetterResponse, CoverLetterListResponse, QnACreate, QnAUpdate
)
from services.cover_letter import CoverLetterService

router = APIRouter(prefix="/cover-letters", tags=["cover-letters"])
svc = CoverLetterService()

@router.post("", response_model=CoverLetterResponse, status_code=status.HTTP_201_CREATED)
async def create_cover_letter(
    body: CoverLetterCreate,
    user_id: str = Depends(get_current_user_id),
):
    return await svc.create(user_id, body)

@router.get("", response_model=CoverLetterListResponse)
async def get_list_cover_letters(
    type: Optional[str] = Query(None, description="profile | job_posting"),
    job_posting_id: Optional[str] = Query(None, description="공고 기반 필터용"),
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    user_id: str = Depends(get_current_user_id),
):
    return await svc.list(user_id, offset, limit, type_filter=type, job_posting_id=job_posting_id)

@router.get("/{cl_id}", response_model=CoverLetterResponse)
async def get_cover_letter(
    cl_id: str,
    user_id: str = Depends(get_current_user_id),
):
    return await svc.get(user_id, cl_id)

@router.patch("/{cl_id}", response_model=CoverLetterResponse)
async def update_cover_letter(
    cl_id: str,
    body: CoverLetterUpdate,
    user_id: str = Depends(get_current_user_id),
):
    return await svc.update(user_id, cl_id, body)

@router.delete("/{cl_id}", status_code=status.HTTP_200_OK)
async def delete_cover_letter(
    cl_id: str,
    user_id: str = Depends(get_current_user_id),
):
    return await svc.delete(user_id, cl_id)

# === 자기소개서 항목 관련 로직===
@router.post("/{cl_id}/qnas", response_model=CoverLetterResponse, status_code=HTTPStatus.CREATED, summary="자기소개서 항목 생성")
async def create_qna(
    cl_id: str,
    body: QnACreate,
    user_id: str = Depends(get_current_user_id)
):
    return await svc.create_qna(user_id, cl_id, body)

@router.patch("/{cl_id}/qnas/{qna_id}", response_model=CoverLetterResponse, summary="문항 수정 (유저가 question/answer 수정)")
async def update_qna(
    cl_id: str,
    qna_id: UUID,
    body: QnAUpdate,
    user_id: str = Depends(get_current_user_id)
):
    return await svc.update_qna(user_id, cl_id, qna_id, body)

@router.delete("/{cl_id}/qnas/{qna_id}", response_model=CoverLetterResponse, summary="문항 삭제")
async def delete_qna(
    cl_id: str,
    qna_id: UUID,
    user_id: str = Depends(get_current_user_id),
):
    return await svc.delete_qna(user_id, cl_id, qna_id)
