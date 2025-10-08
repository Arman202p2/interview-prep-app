from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Quiz metadata
    quiz_type = Column(String, default="daily")  # daily, practice, mock
    total_questions = Column(Integer, nullable=False)
    completed_questions = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)
    
    # Timing
    total_time_taken = Column(Integer, nullable=True)  # Total time in seconds
    timer_enabled = Column(Boolean, default=True)
    
    # Status
    status = Column(String, default="in_progress")  # in_progress, completed, abandoned
    score_percentage = Column(Float, nullable=True)
    
    # Analytics
    topics_covered = Column(JSON, nullable=True)  # List of topic IDs
    difficulty_breakdown = Column(JSON, nullable=True)  # easy/medium/hard counts
    
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="quiz_attempts")
    quiz_questions = relationship("QuizQuestion", back_populates="quiz_attempt", cascade="all, delete-orphan")

class DailyQuizSchedule(Base):
    __tablename__ = "daily_quiz_schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Schedule details
    scheduled_date = Column(DateTime(timezone=True), nullable=False)
    topics = Column(JSON, nullable=False)  # List of topic IDs for the day
    questions_per_topic = Column(Integer, default=1)
    
    # Status
    is_completed = Column(Boolean, default=False)
    quiz_attempt_id = Column(Integer, ForeignKey("quiz_attempts.id"), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")
    quiz_attempt = relationship("QuizAttempt")