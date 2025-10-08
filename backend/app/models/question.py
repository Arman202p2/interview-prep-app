from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Question(Base):
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    
    # Question content
    question_text = Column(Text, nullable=False)
    question_type = Column(String, default="mcq")  # mcq, coding, descriptive
    difficulty_level = Column(String, default="medium")  # easy, medium, hard
    
    # MCQ specific fields
    options = Column(JSON, nullable=True)  # List of options for MCQ
    correct_answer = Column(String, nullable=True)  # Correct option or answer
    
    # Source information
    source_url = Column(String, nullable=True)
    source_name = Column(String, nullable=True)  # tcyonline, prepinsta, etc.
    company_name = Column(String, nullable=True)  # If from company-specific interview
    
    # AI-generated content
    ai_answer = Column(Text, nullable=True)
    ai_explanation = Column(Text, nullable=True)
    ai_confidence_score = Column(Float, nullable=True)  # 0.0 to 1.0
    
    # Metadata
    tags = Column(JSON, nullable=True)  # List of tags
    estimated_time = Column(Integer, nullable=True)  # Time in seconds
    is_verified = Column(Boolean, default=False)
    verification_score = Column(Float, nullable=True)  # Community/AI verification score
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    topic = relationship("Topic", back_populates="questions")
    quiz_questions = relationship("QuizQuestion", back_populates="question")

class QuizQuestion(Base):
    __tablename__ = "quiz_questions"
    
    id = Column(Integer, primary_key=True, index=True)
    quiz_attempt_id = Column(Integer, ForeignKey("quiz_attempts.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    
    # User's response
    user_answer = Column(String, nullable=True)
    is_correct = Column(Boolean, nullable=True)
    time_taken = Column(Integer, nullable=True)  # Time in seconds
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    quiz_attempt = relationship("QuizAttempt", back_populates="quiz_questions")
    question = relationship("Question", back_populates="quiz_questions")