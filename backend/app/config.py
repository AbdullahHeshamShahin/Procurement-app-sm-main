"""Application configuration."""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# MongoDB configuration
# Use local MongoDB by default; set MONGODB_URI env var to use Atlas
MONGODB_URI = os.getenv(
    "MONGODB_URI",
    "mongodb://localhost:27017",
)
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "procurement_db")

# OpenAI configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

# CORS configuration
CORS_ORIGINS = ["http://localhost:3000"]
