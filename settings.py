import os
from dotenv import load_dotenv

load_dotenv()

# DB Configs
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "db")

# JWT Configs
JWT_SECRET = os.getenv("JWT_SECRET", "secret")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 14

# Gemini Configs
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL")

# GCS
BUCKET = os.getenv("BUCKET")
GCP_SA_KEY = os.getenv("GCP_SA_KEY")
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")

# VectorDB
VC_HOST = os.getenv("VC_HOST")
VC_PORT = os.getenv("VC_PORT", 8000)
