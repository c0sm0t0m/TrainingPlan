"""
Event Database Models
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Date
from sqlalchemy.orm import relationship
import enum

from src.database import Base


class EventType(str, enum.Enum):
    """Event types"""
    RACE = "race"
    COMPETITION = "competition"
    CHALLENGE = "challenge"
    OTHER = "other"


class Event(Base):
    """Event model for races, competitions, and fitness events"""
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    event_date = Column(Date, nullable=False)
    event_type = Column(String, nullable=False, default=EventType.RACE.value)
    
    # Event details
    location = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    goal_time = Column(String, nullable=True)  # e.g., "3:30:00" for marathon
    target_distance = Column(String, nullable=True)  # e.g., "5K", "Half Marathon"
    
    # Additional metadata
    registration_link = Column(String, nullable=True)
    cost = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Completion tracking
    is_completed = Column(Integer, default=0)  # SQLite boolean
    actual_time = Column(String, nullable=True)  # Actual finish time
    actual_result = Column(String, nullable=True)  # Place, rank, or result
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="events")
