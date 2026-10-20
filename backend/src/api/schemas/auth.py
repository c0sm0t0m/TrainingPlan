"""
Pydantic schemas for authentication
"""
from typing import Optional
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class User(UserBase):
    """Schema for user response."""
    id: int
    is_active: bool
    
    # Athlete
    weight_kg: Optional[float] = None

    # Training Thresholds
    ftp: Optional[int] = None
    cycling_threshold_hr: Optional[int] = None
    threshold_pace: Optional[int] = None
    running_threshold_hr: Optional[int] = None
    swim_threshold_pace: Optional[int] = None
    swim_threshold_hr: Optional[int] = None
    max_hr: Optional[int] = None
    resting_hr: Optional[int] = None
    
    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """Schema for updating user thresholds."""
    weight_kg: Optional[float] = None
    ftp: Optional[int] = None
    cycling_threshold_hr: Optional[int] = None
    threshold_pace: Optional[int] = None
    running_threshold_hr: Optional[int] = None
    swim_threshold_pace: Optional[int] = None
    swim_threshold_hr: Optional[int] = None
    max_hr: Optional[int] = None
    resting_hr: Optional[int] = None


class Token(BaseModel):
    """Schema for authentication token response."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for token payload data."""
    email: Optional[str] = None
