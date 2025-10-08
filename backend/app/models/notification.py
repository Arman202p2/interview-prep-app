from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Notification content
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String, nullable=False)  # quiz_reminder, achievement, system
    
    # Delivery details
    is_sent = Column(Boolean, default=False)
    is_read = Column(Boolean, default=False)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    read_at = Column(DateTime(timezone=True), nullable=True)
    
    # Firebase specific
    fcm_token = Column(String, nullable=True)
    fcm_message_id = Column(String, nullable=True)
    
    # Additional data
    data = Column(JSON, nullable=True)  # Extra data for the notification
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="notifications")

class NotificationSchedule(Base):
    __tablename__ = "notification_schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Schedule details
    notification_type = Column(String, nullable=False)
    scheduled_time = Column(DateTime(timezone=True), nullable=False)
    frequency = Column(String, default="daily")  # daily, weekly, monthly
    
    # Status
    is_active = Column(Boolean, default=True)
    last_sent = Column(DateTime(timezone=True), nullable=True)
    next_send = Column(DateTime(timezone=True), nullable=True)
    
    # Content template
    title_template = Column(String, nullable=False)
    message_template = Column(Text, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User")