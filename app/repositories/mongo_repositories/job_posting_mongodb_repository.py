# app/repositories/mongo_repositories/job_posting_mongodb_repository.py
from typing import Optional, List, Dict, Tuple
from bson import ObjectId
from beanie import SortDirection
from beanie.operators import In
from app.models.job_posting_document import JobPostingDocument

class JobPostingMongoDBRepository:
    async def get_by_id(self, job_id: str) -> Optional[JobPostingDocument]:
        if not ObjectId.is_valid(job_id):
            return None
        return await JobPostingDocument.get(ObjectId(job_id))

    async def get_by_ids_preserve_order(self, job_ids: List[str]) -> List[JobPostingDocument]:
        """
        주어진 문자열 id 목록 순서를 유지하여 Document 목록 반환.
        """
        valid_oids = [ObjectId(j) for j in job_ids if ObjectId.is_valid(j)]
        if not valid_oids:
            return []

        docs = await JobPostingDocument.find(
            In(JobPostingDocument.id, valid_oids)
        ).to_list()

        doc_map: Dict[str, JobPostingDocument] = {str(d.id): d for d in docs}
        return [doc_map[str(oid)] for oid in valid_oids if str(oid) in doc_map]

    async def list_recent_with_total(self, skip: int, limit: int) -> Tuple[List[JobPostingDocument], int]:
        """
        ObjectId 생성 시간 기준 최신순으로 채용 공고 리스트 조회
        """
        total = await JobPostingDocument.find({}).count()
        docs = await (
            JobPostingDocument.find({})
            .sort([("_id", SortDirection.DESCENDING)])
            .skip(skip)
            .limit(limit)
            .to_list()
        )
        return docs, total
