# app/api/routers/cover_letter.py
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from deps.auth import get_current_user_id
from schemas.cover_letter import (
    CoverLetterCreate, CoverLetterUpdate,
    CoverLetterResponse, CoverLetterListResponse,
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
