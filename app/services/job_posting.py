# app/services/job_posting.py
from typing import Any, Dict, List, Union
from pymongo.collection import Collection
from bson import ObjectId

def _prune_nulls(obj: Any) -> Any:
    """
    - dict: value가 None이면 키 제거, 하위도 재귀 처리
    - list: None 요소 제거, 하위도 재귀 처리
    - 그 외: 그대로 반환
    """
    if isinstance(obj, dict):
        cleaned = {}
        for k, v in obj.items():
            if v is None:
                continue
            pv = _prune_nulls(v)
            # 빈 dict/list 까지 없애기
            # if pv in ({}, []): continue
            cleaned[k] = pv
        return cleaned
    if isinstance(obj, list):
        cleaned_list = []
        for v in obj:
            if v is None:
                continue
            pv = _prune_nulls(v)
            cleaned_list.append(pv)
        return cleaned_list
    return obj

def search_jobs_nl(
    postings_col: Collection, q: str, offset: int, limit: int
) -> Dict[str, Any]:
    base_match = {"$and": [{"$text": {"$search": q}}, {"status": "active"}]}

    total = postings_col.count_documents(base_match)

    pipeline: List[Dict[str, Any]] = [
        {"$match": base_match},
        # due_time이 null/없음 → 가장 뒤로 보내기
        {"$addFields": {
            "parsed_due": {
                "$cond": [
                    {"$ifNull": ["$due_time", False]},
                    {
                        "$dateFromString": {
                            "dateString": "$due_time",
                            "onError": {"$dateFromString": {"dateString": "9999-12-31T23:59:59Z"}},
                            "onNull": {"$dateFromString": {"dateString": "9999-12-31T23:59:59Z"}},
                        }
                    },
                    {"$dateFromString": {"dateString": "9999-12-31T23:59:59Z"}}
                ]
            },
            "textScore": {"$meta": "textScore"},
        }},
        {"$sort": {"parsed_due": 1, "textScore": -1}},  # 마감 임박순, 동점 시 텍스트 점수
        {"$skip": max(0, offset)},
        {"$limit": max(1, min(100, limit))},
        # 문서 전체 반환하되 원문(sourceData)만 제거
        {"$project": {
            "parsed_due": 0,
            "textScore": 0,
            "sourceData": 0,   # 원본 너무 크니 제외
        }},
    ]

    raw_docs = list(postings_col.aggregate(pipeline))

    items: List[Dict[str, Any]] = []
    for d in raw_docs:
        doc = dict(d)
        # _id → id(str)
        _id = doc.pop("_id", None)
        if isinstance(_id, ObjectId):
            doc["id"] = str(_id)
        elif _id is not None:
            doc["id"] = _id
        # null 전부 제거
        doc = _prune_nulls(doc)
        items.append(doc)

    return {"total": total, "offset": offset, "limit": limit, "items": items}
