from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Topic(Base):
    __tablename__ = "topics"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String, nullable=False)  # programming, aptitude, technical, hr, etc.
    is_default = Column(Boolean, default=False)  # System-defined topics
    difficulty_level = Column(String, default="medium")  # easy, medium, hard
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user_topics = relationship("UserTopic", back_populates="topic")
    questions = relationship("Question", back_populates="topic")

class UserTopic(Base):
    __tablename__ = "user_topics"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=1)  # 1-5, higher number = higher priority
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="user_topics")
    topic = relationship("Topic", back_populates="user_topics")