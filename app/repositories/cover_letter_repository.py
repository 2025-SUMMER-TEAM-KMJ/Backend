# app/repositories/cover_letter_repository.py
from __future__ import annotations
from typing import Optional, Dict, Any
from app.repositories.mongo_repositories.cover_letter_mongodb_repository import CoverLetterMongoDBRepository

class CoverLetterRepository:
    def __init__(
        self,
        mongo_repo: Optional[CoverLetterMongoDBRepository] = None,
        # rag_repo: Optional[CoverLetterRagRepository] = None,
    ):
        self.mongo = mongo_repo or CoverLetterMongoDBRepository()
        # self.rag = rag_repo

    async def get_by_id(self, cl_id: str):
        return await self.mongo.get_by_id(cl_id)

    async def list_by_user(
        self, user_id: str, skip: int, limit: int,
        *, type_filter: Optional[str] = None, job_posting_id: Optional[str] = None
    ):
        return await self.mongo.list_by_user(user_id, skip, limit, type_filter=type_filter, job_posting_id=job_posting_id)

    # async def create(self, doc: Dict[str, Any]):
    # rag repository에서 구현 후 주입 필요

    async def update_partial(self, cl_id: str, payload: Dict[str, Any]):
        return await self.mongo.update_partial(cl_id, payload)

    async def delete(self, cl_id: str) -> bool:
        return await self.mongo.delete(cl_id)
