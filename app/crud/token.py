# app/crud/token.py
from datetime import datetime, timedelta, timezone
from pymongo.collection import Collection

def save_refresh_token(tokens_col: Collection, user_id: str, token: str, days: int) -> None:
    now = datetime.now(timezone.utc)
    exp = now + timedelta(days=days)
    tokens_col.insert_one({
        "user_id": user_id,
        "token": token,
        "expires_at": exp
    })

def find_refresh_token(tokens_col: Collection, user_id: str, token: str):
    return tokens_col.find_one({"user_id": user_id, "token": token})

def delete_refresh_token(tokens_col: Collection, user_id: str, token: str) -> None:
    tokens_col.delete_one({"user_id": user_id, "token": token})

def delete_all_refresh_tokens(tokens_col: Collection, user_id: str) -> None:
    tokens_col.delete_many({"user_id": user_id})
