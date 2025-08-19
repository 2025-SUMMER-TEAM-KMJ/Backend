# job_recommendation.py
# 백엔드 AI 부분에 들어가야하는 부분
from __future__ import annotations

from typing import List, Dict, Any, Tuple
from sentence_transformers import SentenceTransformer
from chromadb import Client
import numpy as np
from where_minimal import build_where_from_llm

# ── Chroma ──
from chromadb import PersistentClient

PERSIST_DIR = r""  # chroma_db의 경로로 변경
vc_client = PersistentClient(path=PERSIST_DIR) 
vc_collection = vc_client.get_or_create_collection(
    "master_job_postings",
    metadata={"hnsw:space": "cosine"}
)

# ── 페이징을 위해 후보 넉넉히 가져오는 n_results 계산 ──
def _calc_n_results_for_paging(offset: int, limit: int, *, dup_factor: int = 5, floor: int = 100, ceil: int = 2000) -> int:
    need = (offset + limit) * dup_factor
    return max(min(max(need, floor), ceil), limit)

# ── L2 정규화 ──
def _l2norm(v: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(v, ord=2, axis=-1, keepdims=True) + 1e-12
    return v / n

# ── 점수기반 질의 (코사인 직접계산) ──
def query_with_scores(
    collection,
    query_text: str,
    encoder,                     
    where: dict | None = None,
    n_results: int = 50,
) -> list:
    q = np.asarray(encoder.encode([query_text]))
    q = _l2norm(q)[0]

    raw = collection.query(
        query_embeddings=q.reshape(1, -1).tolist(),
        n_results=n_results,
        include=["documents", "metadatas", "embeddings"],
        **({"where": where} if where else {})
    )

    docs  = raw.get("documents", [[]])[0]
    metas = raw.get("metadatas", [[]])[0]
    embs  = raw.get("embeddings", [[]])[0]
    if not docs:
        return []

    E = _l2norm(np.asarray(embs))
    scores = (E @ q)

    items = [{"doc": d, "meta": m, "score": float(s)}
             for d, m, s in zip(docs, metas, scores)]
    items.sort(key=lambda x: x["score"], reverse=True)
    return items

# ── 검색: 랭킹 전체에서 offset/limit 구간의 job_id(source_id)만 반환 ──
def search(
    query: str,
    *,
    offset: int,
    limit: int,
) -> List[str]:
    """
    입력 query로 검색하고, score 기준으로 랭킹된 문서의 job_id(source_id)를
    offset/limit 페이지네이션으로 잘라 반환한다.
    """
    # 사전 인덱싱된 컬렉션에 대해 where 필터(있으면) 적용
    where_cond = build_where_from_llm(query) or None

    # 청크 중복 가능성을 고려해 후보 넉넉히
    n_results = _calc_n_results_for_paging(offset, limit)

    # 임베딩 모델 (질문 시에만 로드)
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

    items = query_with_scores(
        collection=vc_collection,
        query_text=query,
        encoder=model,
        where=where_cond,
        n_results=n_results,
    )
    if not items:
        return []

    # 문서(source_id == job_id) 단위 dedup: 최고 점수만 유지
    best_by_source: Dict[str, Tuple[float, Dict[str, Any]]] = {}
    for it in items:
        meta = it["meta"] or {}
        sid = meta.get("source_id")  # == job_id
        if not sid:
            continue
        sc = it["score"]
        if (sid not in best_by_source) or (sc > best_by_source[sid][0]):
            best_by_source[sid] = (sc, meta)

    ranked_all = sorted(best_by_source.items(), key=lambda x: x[1][0], reverse=True)
    total = len(ranked_all)
    if total == 0:
        return []

    start = max(0, offset)
    end = min(total, offset + limit)
    if start >= total:
        return []

    job_ids = [sid for sid, _ in ranked_all[start:end]]
    return job_ids
