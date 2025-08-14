# app/repositories/mongo_repositories/cover_letter_mongodb_repository.py
from typing import Optional, Tuple, List, Dict, Any
from bson import ObjectId
from beanie import SortDirection
from app.models.cover_letter_document import CoverLetterDocument

class CoverLetterMongoDBRepository:
    # id로 자기소개서 조회
    async def get_by_id(self, cl_id: str) -> Optional[CoverLetterDocument]:
        if not ObjectId.is_valid(cl_id):
            return None
        return await CoverLetterDocument.get(ObjectId(cl_id))

    # 타입(프로필, 공고 기반)으로 자기소개서 조회
    async def list_by_user(
        self,
        user_id: str,
        skip: int,
        limit: int,
        *,
        type_filter: Optional[str] = None,
        job_posting_id: Optional[str] = None,
    ) -> Tuple[List[CoverLetterDocument], int]:
        q: Dict[str, Any] = {"user_id": user_id}
        if type_filter:
            q["type"] = type_filter
        if job_posting_id:
            q["job_posting_id"] = job_posting_id

        total = await CoverLetterDocument.find(q).count()
        docs = await (
            CoverLetterDocument.find(q)
            .sort([("updated_at", SortDirection.DESCENDING), ("_id", SortDirection.DESCENDING)])
            .skip(skip)
            .limit(limit)
            .to_list()
        )
        return docs, total

    # 자기소개서 수정
    async def update_partial(self, cl_id: str, payload: Dict[str, Any]) -> Optional[CoverLetterDocument]:
        doc = await CoverLetterDocument.get(ObjectId(cl_id))
        if not doc:
            return None

        # updated_at 갱신
        from datetime import datetime, timezone
        to_set = dict(payload)
        to_set["updated_at"] = datetime.now(timezone.utc)

        await doc.update({"$set": to_set})
        return await self.get_by_id(cl_id)

    # 자기소개서 삭제
    async def delete(self, cl_id: str) -> bool:
        doc = await self.get_by_id(cl_id)
        if not doc:
            return False
        await doc.delete()
        return True
