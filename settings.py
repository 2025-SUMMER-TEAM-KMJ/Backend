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
