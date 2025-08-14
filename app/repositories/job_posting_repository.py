# app/repositories/job_posting_repository.py
from typing import Optional, List
from app.repositories.mongo_repositories.job_posting_mongodb_repository import JobPostingMongoDBRepository

class JobPostingRepository:
    def __init__(
        self,
        mongo_repo: Optional[JobPostingMongoDBRepository] = None,
        # rag_port: Optional[JobPostingRagRepository] = None
    ):
        self.mongo = mongo_repo or JobPostingMongoDBRepository()
        # self.rag = rag_port or JobPostingRagRepository()

    async def get_by_id(self, job_id: str):
        return await self.mongo.get_by_id(job_id)

    async def get_by_ids_preserve_order(self, job_ids: List[str]):
        return await self.mongo.get_by_ids_preserve_order(job_ids)

    async def list_recent(self, offset: int, limit: int):
        return await self.mongo.list_recent_with_total(skip=offset, limit=limit)

    async def list(self, q: Optional[str], offset: int, limit: int):
        """
        q가 없거나 빈 문자열이면 전체 최신순.
        q가 있으면 RAG.
        """
        if not q or not q.strip():
            return await self.list_recent(offset=offset, limit=limit)

        # RAG repository 관련 로직 추가 필요
