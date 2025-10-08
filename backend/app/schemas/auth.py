from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: str
    job_role: Optional[str] = None
    experience_level: Optional[str] = None
    target_companies: Optional[List[str]] = None

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    notification_enabled: bool
    notification_frequency: int
    notification_time: str
    quiz_completion_goal: int
    timer_enabled: bool
    quiz_difficulty: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    job_role: Optional[str] = None
    experience_level: Optional[str] = None
    target_companies: Optional[List[str]] = None
    notification_enabled: Optional[bool] = None
    notification_frequency: Optional[int] = None
    notification_time: Optional[str] = None
    quiz_completion_goal: Optional[int] = None
    timer_enabled: Optional[bool] = None
    quiz_difficulty: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None