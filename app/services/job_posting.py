# app/services/job_posting.py
from __future__ import annotations
from typing import Optional, List, Dict, Any, Set
from app.repositories.job_posting_repository import JobPostingRepository
from app.repositories.user_job_bookmark_repository import UserJobBookmarkRepository
from app.schemas.job_posting import JobPostingResponse, JobPostingListResponse

class JobPostingService:
    def __init__(
        self,
        posting_repo: Optional[JobPostingRepository] = None,
        bookmark_repo: Optional[UserJobBookmarkRepository] = None,
    ):
        self.repo = posting_repo or JobPostingRepository()
        self.bookmarks = bookmark_repo or UserJobBookmarkRepository()

    async def get(self, job_id: str, user_id: Optional[str] = None) -> JobPostingResponse:
        doc = await self.repo.get_by_id(job_id)
        if not doc:
            raise ValueError("공고를 찾을 수 없습니다.")
        res = JobPostingResponse.from_doc(doc)
        if user_id:
            res.bookmarked = await self.bookmarks.is_bookmarked(user_id, res.id)
        return res

    async def list(
        self,
        q: Optional[str],
        offset: int,
        limit: int,
        user_id: Optional[str] = None,
    ) -> JobPostingListResponse:
        """
        q가 비었으면 전체 최신순(ObjectId desc) 반환.
        q가 있으면 검색(파사드: RAG→Mongo).
        로그인 했을 때는 북마크 정보도 추가해서 반환.
        """
        docs, total = await self.repo.list(q=q, offset=offset, limit=limit)
        items = [JobPostingResponse.from_doc(d) for d in docs]

        if user_id and items:
            ids = [i.id for i in items]
            bookmarked_ids: Set[str] = await self.bookmarks.list_bookmarked_job_ids(user_id, ids)
            for i in items:
                i.bookmarked = i.id in bookmarked_ids

        return JobPostingListResponse(total=total, items=items)

    async def recommendations(
        self,
        user_id: str,
        offset: int,
        limit: int,
    ) -> List[JobPostingResponse]:
        """
        사용자 맞춤 추천, AI 연결 필요
        """

    async def add_bookmark(self, user_id: str, job_id: str) -> Dict[str, Any]:
        # 존재 확인 (없으면 404)
        doc = await self.repo.get_by_id(job_id)
        if not doc:
            raise ValueError("공고를 찾을 수 없습니다.")
        await self.bookmarks.add(user_id, job_id)
        return {"job_id": job_id, "bookmarked": True}

    async def remove_bookmark(self, user_id: str, job_id: str) -> Dict[str, Any]:
        # 존재 확인 (없어도 삭제는 idempotent 하게 처리 가능하지만, UX 위해 확인)
        doc = await self.repo.get_by_id(job_id)
        if not doc:
            raise ValueError("공고를 찾을 수 없습니다.")
        await self.bookmarks.remove(user_id, job_id)
        return {"job_id": job_id, "bookmarked": False}

    async def list_bookmarks(
        self, user_id: str, offset: int, limit: int
    ) -> JobPostingListResponse:
        """
        유저의 북마크 목록을 created_at DESC로 가져와 상세 붙여 반환.
        """
        job_ids, total = await self.bookmarks.list_user_bookmark_ids(
            user_id, skip=offset, limit=limit
        )
        if not job_ids:
            return JobPostingListResponse(total=total, items=[])

        docs = await self.repo.get_by_ids_preserve_order(job_ids)
        items = [JobPostingResponse.from_doc(d) for d in docs]
        for i in items:
            i.bookmarked = True  # 북마크 목록이므로 모두 True
        return JobPostingListResponse(total=total, items=items)
