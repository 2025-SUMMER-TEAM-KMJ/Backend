# app/crud/user.py
from typing import Dict, Any, Optional
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError
from bson import ObjectId

from app.schemas.user import UserCreate
from app.core.security import hash_password

def _sanitize_user(doc: Dict[str, Any]) -> Dict[str, Any]:
    # None 방지: doc이 없으면 빈 dict 반환
    if not doc:
        return {}

    # 원본 변경 방지: 복사본 생성
    doc = dict(doc)

    # _id를 꺼내고 문자열 id로 변환
    _id = doc.pop("_id", None)
    if isinstance(_id, ObjectId):
        doc["id"] = str(_id)
    elif _id is not None:
        doc["id"] = _id

    # 민감 정보 삭제
    doc.pop("hashed_password", None)

    return doc

def get_user_by_email(users_col: Collection, email: str) -> Optional[Dict[str, Any]]:
    return users_col.find_one({"email": email})

def create_user(users_col: Collection, user_in: UserCreate) -> Dict[str, Any]:
    if get_user_by_email(users_col, user_in.email):
        raise ValueError("이미 등록된 이메일입니다.")

    doc = {
        "email": user_in.email,
        "hashed_password": hash_password(user_in.password),
        "name": user_in.name,
        "age": user_in.age,
        "gender": user_in.gender,
        "phone": user_in.phone,
    }

    try:
        result = users_col.insert_one(doc)
    except DuplicateKeyError:
        raise ValueError("이미 등록된 이메일입니다.")

    inserted = users_col.find_one({"_id": result.inserted_id})
    return _sanitize_user(inserted)
