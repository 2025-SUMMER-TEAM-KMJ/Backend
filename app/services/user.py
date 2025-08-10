# app/services/user.py
from typing import Dict, Any, Mapping
from fastapi import HTTPException
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError
from bson import ObjectId

from app.schemas.user import UserCreate, ProfileUpdateRequest
from app.crud.user import (
    create_user as create_user_crud,
    get_user_by_email,
)

def _sanitize_user(doc: Mapping[str, Any]) -> Dict[str, Any]:
    """DB 문서를 API 응답용으로 변환: _id->id(str), 비밀번호 제거."""
    if not doc:
        return {}
    d = dict(doc)
    _id = d.pop("_id", None)
    if isinstance(_id, ObjectId):
        d["id"] = str(_id)
    elif _id is not None:
        d["id"] = _id
    d.pop("hashed_password", None)
    return d


def signup(users_col: Collection, user_in: UserCreate) -> Dict[str, Any]:
    """이메일 중복 체크 + 사용자 생성 + 응답 정리."""
    if get_user_by_email(users_col, user_in.email):
        raise HTTPException(status_code=400, detail="이미 등록된 이메일입니다.")
    try:
        created = create_user_crud(users_col, user_in)
        return _sanitize_user(created)
    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail="이미 등록된 이메일입니다.")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


def update_profile(
    users_col: Collection,
    user_id: str | ObjectId,
    payload: ProfileUpdateRequest,
) -> Dict[str, Any]:
    """
    부분 업데이트 지원.
    - 허용 필드만 업데이트: name, age, gender, phone
    - 변경 없음이면 현재 프로필 반환
    """
    allowed_fields = {"name", "age", "gender", "phone"}

    update_data = {
        k: v for k, v in payload.dict(exclude_unset=True).items()
        if v is not None and k in allowed_fields
    }

    # 이메일/비밀번호 등 허용하지 않는 필드는 무시
    if not update_data:
        # 변경 없으면 현재 상태 반환
        _id = user_id if isinstance(user_id, ObjectId) else ObjectId(user_id)
        current = users_col.find_one({"_id": _id})
        if not current:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
        return _sanitize_user(current)

    _id = user_id if isinstance(user_id, ObjectId) else ObjectId(user_id)
    result = users_col.update_one({"_id": _id}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

    updated = users_col.find_one({"_id": _id})
    return _sanitize_user(updated)


def get_profile(users_col: Collection, user_id: str | ObjectId) -> Dict[str, Any]:
    """현재 사용자 프로필 조회"""
    _id = user_id if isinstance(user_id, ObjectId) else ObjectId(user_id)
    doc = users_col.find_one({"_id": _id})
    if not doc:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    return _sanitize_user(doc)
