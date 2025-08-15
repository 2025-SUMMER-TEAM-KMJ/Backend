# app/services/user.py
from typing import Any, Dict
from schemas.user import SignUpRequest, UserUpdateRequest, UserResponse
from repositories.user_repository import UserRepository

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
