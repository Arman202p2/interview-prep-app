from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Profile information
    job_role = Column(String, nullable=True)
    experience_level = Column(String, nullable=True)  # fresher, 1-3, 3-5, 5+
    target_companies = Column(JSON, nullable=True)  # List of company names
    
    # Notification preferences
    notification_enabled = Column(Boolean, default=True)
    notification_frequency = Column(Integer, default=10)  # Number of notifications per day
    notification_time = Column(String, default="09:00")  # Preferred notification time
    quiz_completion_goal = Column(Integer, default=1)  # Daily quiz completion goal
    
    # Settings
    timer_enabled = Column(Boolean, default=True)
    quiz_difficulty = Column(String, default="medium")  # easy, medium, hard
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user_topics = relationship("UserTopic", back_populates="user", cascade="all, delete-orphan")
    quiz_attempts = relationship("QuizAttempt", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")