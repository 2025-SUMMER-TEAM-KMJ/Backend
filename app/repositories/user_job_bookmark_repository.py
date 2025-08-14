# app/repositories/user_job_bookmark_repository.py
from typing import Iterable, Set, List, Tuple
from app.models.user_job_bookmark_document import UserJobBookmarkDocument
from beanie import SortDirection

class UserJobBookmarkRepository:
    # 북마크한 공고인지 확인
    async def is_bookmarked(self, user_id: str, job_id: str) -> bool:
        doc = await UserJobBookmarkDocument.find_one(
            UserJobBookmarkDocument.user_id == user_id,
            UserJobBookmarkDocument.job_id == job_id,
        )
        return doc is not None

    # 특정 ids 중 유저가 북마크한 것만 집합으로 반환
    async def list_bookmarked_job_ids(
            self, user_id: str, job_ids: Iterable[str]
    ) -> Set[str]:
        ids = list({*job_ids})  # 중복 제거
        if not ids:
            return set()

        docs = await UserJobBookmarkDocument.find(
            UserJobBookmarkDocument.user_id == user_id,
            UserJobBookmarkDocument.job_id.in_(ids),
        ).to_list()
        return {d.job_id for d in docs}

    # 북마크한 공고들 반환
    async def list_user_bookmark_ids(
        self, user_id: str, skip: int, limit: int
    ) -> Tuple[List[str], int]:
        total = await UserJobBookmarkDocument.find(
            UserJobBookmarkDocument.user_id == user_id
        ).count()

        docs = await (
            UserJobBookmarkDocument.find(UserJobBookmarkDocument.user_id == user_id)
            .sort([("created_at", SortDirection.ASCENDING), ("_id", SortDirection.ASCENDING)])
            .skip(skip)
            .limit(limit)
            .to_list()
        )
        return [d.job_id for d in docs], total

    # 북마크 추가
    async def add(self, user_id: str, job_id: str) -> None:
        if not await self.is_bookmarked(user_id, job_id):
            await UserJobBookmarkDocument(user_id=user_id, job_id=job_id).insert()

    # 북마크 삭제
    async def remove(self, user_id: str, job_id: str) -> None:
        doc = await UserJobBookmarkDocument.find_one(
            UserJobBookmarkDocument.user_id == user_id,
            UserJobBookmarkDocument.job_id == job_id,
        )
        if doc:
            await doc.delete()
