# app/api/routers/job_posting.py
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Depends, status
from services.job_posting import JobPostingService
from schemas.job_posting import JobPostingResponse, JobPostingListResponse
from deps.auth import get_current_user_id, get_optional_user_id

router = APIRouter(prefix="/job-postings", tags=["jobs"])
svc = JobPostingService()

# 전체/검색 조회: 공개 (로그인 시 bookmarked 포함)
@router.get(
    "",
    response_model=JobPostingListResponse,
    response_model_exclude_none=True,
    summary="채용 공고 목록 조회 (로그인 하지 않아도 확인 가능)"
)
async def get_job_postings(
    q: Optional[str] = Query(None, description="사용자 쿼리(AI가 전처리하여 전달)"),
    offset: int = Query(0, ge=0, description="페이지네이션 시작점"),
    limit: int = Query(20, ge=1, le=100, description="한 번에 가져올 개수"),
    user_id: Optional[str] = Depends(get_optional_user_id),
):

    return await svc.list(q=q, offset=offset, limit=limit, user_id=user_id)

# 맞춤 추천: 로그인 필요 (bookmarked 포함)
@router.get(
    "/recommendations",
    response_model=List[JobPostingResponse],
    response_model_exclude_none=True,
    summary="사용자 맞춤 채용 공고 추천"
)
async def recommendations_job_postings(
    offset: int = Query(0, ge=0, description="페이지네이션 시작점"),
    limit: int = Query(20, ge=1, le=100, description="한 번에 가져올 개수"),
    user_id: str = Depends(get_current_user_id),
):
    return await svc.recommendations(user_id=user_id, offset=offset, limit=limit)

# 북마크한 공고만 반환
@router.get(
    "/bookmarks",
    response_model=JobPostingListResponse,
    response_model_exclude_none=True,
    summary="내가 북마크한 공고 목록 (로그인 필요)"
)
async def list_my_bookmarks(
    offset: int = Query(0, ge=0, description="페이지네이션 시작점"),
    limit: int = Query(20, ge=1, le=100, description="한 번에 가져올 개수"),
    user_id: str = Depends(get_current_user_id),
):
    return await svc.list_bookmarks(user_id=user_id, offset=offset, limit=limit)

# 단건 조회: 공개 (로그인 시 bookmarked 포함)
@router.get(
    "/{job_id}",
    response_model=JobPostingResponse,
    response_model_exclude_none=True,  # 로그인 안 하면 bookmarked 필드 제외
    summary="채용 공고 목록 조회 (로그인 하지 않아도 확인 가능)"
)
async def get_job(job_id: str, user_id: Optional[str] = Depends(get_optional_user_id)):
    try:
        return await svc.get(job_id, user_id=user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# 북마크 추가
@router.post(
    "/bookmark/{job_id}",
    status_code=status.HTTP_200_OK,
    summary="해당 공고를 북마크 (로그인 필요)"
)
async def add_bookmark(job_id: str, user_id: str = Depends(get_current_user_id)) -> Dict[str, Any]:
    try:
        return await svc.add_bookmark(user_id=user_id, job_id=job_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# 북마크 삭제
@router.delete(
    "/bookmark/{job_id}",
    status_code=status.HTTP_200_OK,
    summary="해당 공고의 북마크 해제 (로그인 필요)"
)
async def remove_bookmark(job_id: str, user_id: str = Depends(get_current_user_id)) -> Dict[str, Any]:
    try:
        return await svc.remove_bookmark(user_id=user_id, job_id=job_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
