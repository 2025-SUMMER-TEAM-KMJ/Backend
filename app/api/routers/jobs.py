# app/api/routers/jobs.py
from fastapi import APIRouter, Depends
from pymongo.collection import Collection
from app.database import get_collection
from app.schemas.jobs import JobSearchRequest, JobSearchResponse
from app.services.jobs import search_jobs_nl
from app.deps.auth import get_current_user

router = APIRouter(prefix="/jobs", tags=["jobs"])

@router.post(
    "/search",
    response_model=JobSearchResponse,
    response_model_exclude_none=True,  # null 필드 자동 제외
)
def search_jobs(
    payload: JobSearchRequest,
    _user=Depends(get_current_user),  # 토큰 필터
    postings_col: Collection = Depends(get_collection("wanted_job_postings")),
):
    return search_jobs_nl(
        postings_col=postings_col,
        q=payload.q,
        offset=payload.offset,
        limit=payload.limit,
    )
