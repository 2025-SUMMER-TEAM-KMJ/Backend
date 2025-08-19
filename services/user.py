# services/user.py
import os
from typing import Any, Dict, Tuple
from schemas.user import SignUpRequest, UserUpdateRequest, UserResponse, QnACreate, QnAUpdate
from repositories.user_repository import UserRepository
from services import file
from uuid import UUID, uuid4
from datetime import datetime, timezone

class UserService:
    def __init__(self):
        self.repo = UserRepository()

    # 회원가입
    async def sign_up(self, req: SignUpRequest) -> UserResponse:
        # 중복 이메일 체크
        existed = await self.repo.get_by_email(str(req.email))
        if existed:
            raise ValueError("이미 존재하는 이메일입니다.")

        # 초기 유저 문서 구성 (응답 안정성을 위해 기본값 포함)
        doc: Dict[str, Any] = {
            "email": str(req.email),
            "password": req.password,
            "name": req.name,
            "age": req.age,
            "gender": req.gender,
            "phone": req.phone,

            # 선택/리스트 필드 기본값
            "urls": [],
            "brief": None,
            "competencies": [],
            "preferred_position": [],
            "educations": [],
            "work_experience": [],
            "experiences": [],
            "certifications": [],
            "qnas": [],
            "interest_jobs": [],
        }

        created = await self.repo.create(doc)
        # 일관성을 위해 DB에서 다시 읽어오기
        saved = await self.repo.get_by_email(str(req.email))
        return UserResponse.from_doc(saved.dict())

    # 프로필 조회
    async def get_profile(self, user_id: str) -> UserResponse:
        doc = await self.repo.get_by_id(user_id)
        if not doc:
            raise ValueError("사용자를 찾을 수 없습니다.")
        return UserResponse.from_doc(doc.dict())

    # 프로필 업데이트
    async def update_profile(self, user_id: str, req: UserUpdateRequest) -> UserResponse:
        # 보낸 필드만 반영
        try:
            payload: Dict[str, Any] = req.model_dump(exclude_unset=True)
        except AttributeError:
            payload = req.dict(exclude_unset=True)

        # 보호 필드 제거 (이메일/비밀번호 등)
        payload.pop("email", None)
        payload.pop("password", None)

        updated = await self.repo.update(user_id, payload)
        if not updated:
            raise ValueError("업데이트 실패 또는 사용자를 찾을 수 없습니다.")
        return UserResponse.from_doc(updated.dict())

    # 이미지 업로드
    async def upload_profile_image(self, user_id: str, raw: bytes, content_type: str) -> Dict[str, Any]:
        file.validate_file_request(raw, content_type)
        extension = file.choose_file_extension(content_type)
        if extension == "None":
            raise ValueError("확장자 매칭에 실패했습니다.")

        user = await self.repo.get_by_id(user_id)
        if not user:
            raise ValueError("사용자를 찾을 수 없습니다.")
        old_profile_img_key = user.profile_img_key

        key = f"users/{user_id}/profile/{os.urandom(8).hex()}.{extension}"
        file.upload_file(key, raw, content_type)

        await self.repo.update(user_id, {"profile_img_key": key})
        if old_profile_img_key:
            try:
                file.delete_file(old_profile_img_key)
            except Exception:
                pass

        return {"key": key, "contentType": content_type}

    # 이미지 다운로드
    async def download_profile_image(self, user_id: str) -> Tuple[bytes, str, str]:
        user = await self.repo.get_by_id(user_id)
        if not user or not user.profile_img_key:
            raise ValueError("프로필 이미지가 존재하지 않습니다.")
        data, content_type = file.download_file(user.profile_img_key)
        file_name = os.path.basename(user.profile_img_key)
        return data, content_type, file_name

    # 이미지 삭제
    async def delete_profile_image(self, user_id: str) -> Dict[str, Any]:
        user = await self.repo.get_by_id(user_id)
        if not user or not user.profile_img_key:
            raise ValueError("프로필 이미지가 존재하지 않습니다.")
        key = user.profile_img_key
        try:
            file.delete_file(key)
        except Exception:
            pass
        await self.repo.update(user_id, {"profile_img_key": None})
        return {"deleted": True, "key": key}

    # === QNA ===
    async def add_qna(self, user_id: str, body: QnACreate) -> UserResponse:
        qna = {
            "id": uuid4(),
            "title": body.title,
            "content": body.content,
            "category": body.category,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
        updated = await self.repo.add_qna(user_id, qna)
        if not updated:
            raise ValueError("사용자를 찾을 수 없습니다.")
        return UserResponse.from_doc(updated.dict())

    async def update_qna(self, user_id: str, qna_id: UUID, body: QnAUpdate) -> UserResponse:
        fields = body.model_dump(exclude_unset=True)
        updated = await self.repo.update_qna(user_id, qna_id, fields)
        if not updated:
            raise ValueError("사용자 또는 QnA를 찾을 수 없습니다.")
        return UserResponse.from_doc(updated.dict())

    async def delete_qna(self, user_id: str, qna_id: UUID) -> UserResponse:
        updated = await self.repo.delete_qna(user_id, qna_id)
        if not updated:
            raise ValueError("사용자 또는 QnA를 찾을 수 없습니다.")
        return UserResponse.from_doc(updated.dict())
