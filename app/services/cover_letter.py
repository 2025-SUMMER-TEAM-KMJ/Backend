# app/services/cover_letter.py
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from app.repositories.cover_letter_repository import CoverLetterRepository
from app.repositories.job_posting_repository import JobPostingRepository
from app.schemas.cover_letter import (
    CoverLetterCreate, CoverLetterUpdate,
    CoverLetterResponse, CoverLetterListResponse,
)

class CoverLetterService:
    def __init__(
        self,
        repo: Optional[CoverLetterRepository] = None,
        job_repo: Optional[JobPostingRepository] = None,
    ):
        self.repo = repo or CoverLetterRepository()
        self.jobs = job_repo or JobPostingRepository()

    async def create(self, user_id: str, req: CoverLetterCreate) -> CoverLetterResponse:
        pass
        # RAG로 처리 필요

    async def get(self, user_id: str, cl_id: str) -> CoverLetterResponse:
        doc = await self.repo.get_by_id(cl_id)
        if not doc or doc.user_id != user_id:
            raise HTTPException(status_code=404, detail="자기소개서를 찾을 수 없습니다.")
        return CoverLetterResponse.from_doc(doc)

    async def list(
        self,
        user_id: str,
        offset: int,
        limit: int,
        type_filter: Optional[str] = None,
        job_posting_id: Optional[str] = None,
    ) -> CoverLetterListResponse:
        docs, total = await self.repo.list_by_user(
            user_id, skip=offset, limit=limit,
            type_filter=type_filter, job_posting_id=job_posting_id
        )
        items = [CoverLetterResponse.from_doc(d) for d in docs]
        return CoverLetterListResponse(total=total, items=items)

    async def update(self, user_id: str, cl_id: str, req: CoverLetterUpdate) -> CoverLetterResponse:
        payload = req.model_dump(exclude_unset=True)
        if not payload:
            # 변경 사항 없음 → 현재 문서 반환
            return await self.get(user_id, cl_id)

        doc = await self.repo.get_by_id(cl_id)
        if not doc or doc.user_id != user_id:
            raise HTTPException(status_code=404, detail="자기소개서를 찾을 수 없습니다.")

        updated = await self.repo.update_partial(cl_id, payload)
        return CoverLetterResponse.from_doc(updated)

    async def delete(self, user_id: str, cl_id: str) -> Dict[str, Any]:
        doc = await self.repo.get_by_id(cl_id)
        if not doc or doc.user_id != user_id:
            raise HTTPException(status_code=404, detail="자기소개서를 찾을 수 없습니다.")
        ok = await self.repo.delete(cl_id)
        if not ok:
            raise HTTPException(status_code=400, detail="삭제 실패")
        return {"deleted": True, "id": cl_id}