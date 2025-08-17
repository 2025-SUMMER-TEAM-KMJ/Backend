# services/file.py
import os, json
from typing import Tuple
from google.cloud import storage
from google.oauth2 import service_account
from settings import BUCKET, GCP_SA_KEY, GCP_PROJECT_ID

if GCP_SA_KEY:
    creds_dict = json.loads(GCP_SA_KEY)
    credentials = service_account.Credentials.from_service_account_info(creds_dict)
    client = storage.Client(credentials=credentials, project=GCP_PROJECT_ID)
else:
    client = storage.Client()

ALLOWED_EXTENSIONS = {"image/jpeg", "image/png", "image/jpg"}
MAX_MB = 10

def validate_file_request(raw: bytes, content_type: str):
    if content_type not in ALLOWED_EXTENSIONS:
        raise ValueError("허용되지 않은 파일 확장자입니다. jpeg/jpg/png 파일만 허용됩니다.")
    if len(raw) > MAX_MB * 1024 * 1024:
        raise ValueError("파일은 ", MAX_MB, "MB 이하만 허용됩니다.")

def choose_file_extension(content_type: str) -> str:
    if content_type in ("image/jpeg", "image/jpg"):
        return "jpg"
    if content_type == "image/png":
        return "png"
    return "none"

def upload_file(key: str, raw: bytes, content_type: str):
    bucket = client.get_bucket(BUCKET)
    blob = bucket.blob(key)
    blob.cache_control = "public, max-age=31536000, immutable"
    blob.upload_from_string(raw, content_type=content_type)

def download_file(key: str) -> Tuple[bytes, str]:
    bucket = client.get_bucket(BUCKET)
    blob = bucket.blob(key)
    if not blob.exists():
        raise ValueError("파일이 존재하지 않습니다.")
    data = blob.download_as_bytes()
    content_type = blob.content_type or "application/octet-stream"
    return data, content_type

def delete_file(key: str):
    bucket = client.get_bucket(BUCKET)
    blob = bucket.blob(key)
    blob.delete(if_generation_match=None)
