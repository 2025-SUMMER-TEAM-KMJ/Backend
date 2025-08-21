# app/repositories/job_posting_repository.py
from typing import Optional, List
from repositories.mongo_repositories.job_posting_mongodb_repository import JobPostingMongoDBRepository
from repositories.rag_repositories.job_poasting_rag_repository import JobPostingRagRepository

class JobPostingRepository:
    def __init__(
        self,
        mongo_repo: Optional[JobPostingMongoDBRepository] = None,
        rag_repo: Optional[JobPostingRagRepository] = None
    ):
        self.mongo = mongo_repo or JobPostingMongoDBRepository()
        self.rag = rag_repo or JobPostingRagRepository()

    async def get_by_id(self, job_id: str):
        return await self.mongo.get_by_id(job_id)

    async def get_by_ids_preserve_order(self, job_ids: List[str]):
        return await self.mongo.get_by_ids_preserve_order(job_ids)

    async def list_recent(self, offset: int, limit: int):
        return await self.mongo.list_recent_with_total(skip=offset, limit=limit)

    async def list(self, q: Optional[str], offset: int, limit: int):
        q_norm = (q or "").strip().lower()

        if q_norm in ("", "null", "undefined"):
            return await self.list_recent(offset=offset, limit=limit)
        else: # query가 존재하는 경우 RAG repository 요청
            job_ids = self.rag.search(q, offset=offset, limit=limit)
            if job_ids == [] or job_ids == None:
                return [], 0
            return await self.get_by_ids_preserve_order(job_ids), len(job_ids)

        

        
