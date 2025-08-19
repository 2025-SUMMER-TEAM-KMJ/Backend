# app/repositories/user_repository.py
from typing import Optional, Dict, Any
from bson import ObjectId
from passlib.hash import bcrypt
from models.user_document import UserDocument
from uuid import UUID
from datetime import datetime, timezone

class UserRepository:
    # 생성
    async def create(self, doc: Dict[str, Any]) -> UserDocument:
        """
        사용자를 생성합니다.
        - 비밀번호를 해시한 뒤 저장합니다.
        - 저장된 문서를 반환합니다.
        """
        to_insert = dict(doc)
        to_insert["password"] = bcrypt.hash(to_insert["password"])
        user = UserDocument(**to_insert)
        await user.insert()
        return user

    # 조회
    async def get_by_email(self, email: str) -> Optional[UserDocument]:
        """
        이메일로 사용자를 조회합니다.
        """
        return await UserDocument.find_one(UserDocument.email == email)

    async def get_by_id(self, user_id: str) -> Optional[UserDocument]:
        """
        ObjectId로 사용자를 조회합니다.
        """
        return await UserDocument.get(ObjectId(user_id))

    # 부분 업데이트
    async def update(self, user_id: str, payload: Dict[str, Any]) -> Optional[UserDocument]:
        """
        사용자를 부분 업데이트합니다.
        - 값이 None인 필드는 unset으로 제거합니다.
        - 값이 있는 필드는 set으로 업데이트합니다.
        - 업데이트 후의 문서를 반환합니다.
        """
        to_set, to_unset = {}, {}
        for key, value in payload.items():
            if value is None:
                to_unset[key] = ""          # 필드 제거
            else:
                to_set[key] = value         # 필드 교체/설정

        update_ops: Dict[str, Any] = {}
        if to_set:
            update_ops["$set"] = to_set
        if to_unset:
            update_ops["$unset"] = to_unset

        if update_ops:
            await UserDocument.find_one(UserDocument.id == ObjectId(user_id)).update(update_ops)

        return await self.get_by_id(user_id)

    # === QNA ===
    async def add_qna(self, user_id: str, qna: Dict[str, Any]) -> Optional[UserDocument]:
        await UserDocument.find_one(UserDocument.id == ObjectId(user_id)).update({
            "$push": {"qnas": qna}
        })
        return await self.get_by_id(user_id)

    async def update_qna(self, user_id: str, qna_id: UUID, fields: Dict[str, Any]) -> Optional[UserDocument]:
        if not fields:
            return await self.get_by_id(user_id)
        # updated_at 자동 갱신
        fields = {f"qnas.$[elem].{k}": v for k, v in fields.items()}
        fields["qnas.$[elem].updated_at"] = datetime.now(timezone.utc)

        await UserDocument.find_one(UserDocument.id == ObjectId(user_id)).update(
            {"$set": fields},
            array_filters=[{"elem.id": qna_id}]
        )
        return await self.get_by_id(user_id)

    async def delete_qna(self, user_id: str, qna_id: UUID) -> Optional[UserDocument]:
        await UserDocument.find_one(UserDocument.id == ObjectId(user_id)).update({
            "$pull": {"qnas": {"id": qna_id}}
        })
        return await self.get_by_id(user_id)
