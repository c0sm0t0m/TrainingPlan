"""
Event Pydantic Schemas
"""
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


class EventBase(BaseModel):
    """Base event schema"""
    name: str = Field(..., min_length=1, max_length=200)
    event_date: date
    event_type: str = Field(default="race")
    location: Optional[str] = None
    description: Optional[str] = None
    goal_time: Optional[str] = None
    target_distance: Optional[str] = None
    registration_link: Optional[str] = None
    cost: Optional[str] = None
    notes: Optional[str] = None
    is_main_goal: bool = False


class EventCreate(EventBase):
    """Schema for creating an event"""
    pass


class EventUpdate(BaseModel):
    """Schema for updating an event"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    event_date: Optional[date] = None
    event_type: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    goal_time: Optional[str] = None
    target_distance: Optional[str] = None
    registration_link: Optional[str] = None
    cost: Optional[str] = None
    notes: Optional[str] = None
    is_main_goal: Optional[bool] = None
    is_completed: Optional[bool] = None
    actual_time: Optional[str] = None
    actual_result: Optional[str] = None


class Event(EventBase):
    """Full event schema"""
    id: int
    user_id: int
    is_completed: bool
    actual_time: Optional[str] = None
    actual_result: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
