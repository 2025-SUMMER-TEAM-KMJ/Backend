# app/services/cover_letter.py
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from uuid import UUID
from repositories.cover_letter_repository import CoverLetterRepository
from repositories.job_posting_repository import JobPostingRepository
from schemas.cover_letter import (
    CoverLetterCreate, CoverLetterUpdate,
    CoverLetterResponse, CoverLetterListResponse, QnACreate, QnAUpdate
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
        if req.type == "job_posting" and not req.job_posting_id:
            raise HTTPException(status_code=400, detail="채용 공고 ID가 필요합니다.")

        payload = req.model_dump()
        payload["user_id"] = user_id

        # LLM 답변 생성 자리
        # 답변 생성: 여기서 LLM을 호출해 payload["qnas"] 각 항목에 answer 필드 채우기

        created = await self.repo.create(payload)

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

    # === 자기소개서 항목 관련 로직 ===
    # 자기소개서 항목 추가
    async def create_qna(self, user_id: str, cl_id: str, body: QnACreate) -> CoverLetterResponse:
        doc = await self.repo.get_by_id(cl_id)
        if not doc or doc.user_id != user_id:
            raise HTTPException(status_code=404, detail="자기소개서를 찾을 수 없습니다.")

        new_qna = {
            "question": body.question,
            "answer": body.answer,  # None 또는 ""일 수 있음
        }

        # LLM으로 답변 생성할 수도 있기 때문에 주석 처리
        # new_qna["answer"] = llm으로 처리한 답변

        created = await self.repo.create_qna(cl_id, new_qna)
        return CoverLetterResponse.from_doc(created)

    # 자기소개서 항목 수정
    async def update_qna(self, user_id: str, cl_id: str, qna_id: UUID, body: QnAUpdate) -> CoverLetterResponse:
        doc = await self.repo.get_by_id(cl_id)
        if not doc or doc.user_id != user_id:
            raise HTTPException(status_code=404, detail="자기소개서를 찾을 수 없습니다.")

        fields: Dict[str, Any] = {}
        if body.question is not None:
            fields["qnas.$[elem].question"] = body.question
        if body.answer is not None:
            fields["qnas.$[elem].answer"] = body.answer

        if not fields:
            return CoverLetterResponse.from_doc(doc)

        updated = await self.repo.update_qna(cl_id, qna_id, fields)
        if not updated:
            raise HTTPException(status_code=404, detail="문항을 찾을 수 없습니다.")
        return CoverLetterResponse.from_doc(updated)

    # 자기소개서 항목 삭제
    async def delete_qna(self, user_id: str, cl_id: str, qna_id: UUID) -> CoverLetterResponse:
        doc = await self.repo.get_by_id(cl_id)
        if not doc or doc.user_id != user_id:
            raise HTTPException(status_code=404, detail="자기소개서를 찾을 수 없습니다.")

        updated = await self.repo.delete_qna(cl_id, qna_id)
        if not updated:
            raise HTTPException(status_code=404, detail="문항을 찾을 수 없습니다.")
        return CoverLetterResponse.from_doc(updated)
