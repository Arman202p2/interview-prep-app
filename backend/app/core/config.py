from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "Interview Prep App"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/interview_prep"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Security
    JWT_SECRET_KEY: str = "your-super-secret-jwt-key-change-this-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # External APIs
    OPENROUTER_API_KEY: str = ""
    FIRECRAWL_API_KEY: str = ""
    
    # Firebase
    FIREBASE_PROJECT_ID: str = ""
    FIREBASE_PRIVATE_KEY_ID: str = ""
    FIREBASE_PRIVATE_KEY: str = ""
    FIREBASE_CLIENT_EMAIL: str = ""
    FIREBASE_CLIENT_ID: str = ""
    FIREBASE_AUTH_URI: str = "https://accounts.google.com/o/oauth2/auth"
    FIREBASE_TOKEN_URI: str = "https://oauth2.googleapis.com/token"
    
    # Scraping Settings
    SCRAPING_DELAY: int = 2
    MAX_CONCURRENT_REQUESTS: int = 5
    USER_AGENT: str = "InterviewPrepBot/1.0"
    
    # Notification Settings
    DAILY_QUIZ_NOTIFICATIONS: int = 10
    DEFAULT_NOTIFICATION_TIME: str = "09:00"
    
    # Question Sources
    QUESTION_SOURCES: List[str] = [
        "https://www.tcyonline.com",
        "https://prepinsta.com",
        "https://www.indiabix.com",
        "https://www.reddit.com/r/cscareerquestions",
        "https://www.reddit.com/r/interviews"
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()