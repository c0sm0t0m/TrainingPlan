"""
User database model
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from src.database import Base


class User(Base):
    """User account model."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Garmin Connect Integration
    garmin_email = Column(String, nullable=True)
    garmin_oauth1_token = Column(String, nullable=True)
    garmin_oauth2_token = Column(String, nullable=True)
    garmin_connected = Column(Boolean, default=False)
    garmin_last_sync = Column(DateTime, nullable=True)
    
    # Training Thresholds & Zones
    # Cycling
    ftp = Column(Integer, nullable=True)  # Functional Threshold Power (watts)
    cycling_threshold_hr = Column(Integer, nullable=True)  # Lactate Threshold Heart Rate for cycling
    
    # Running
    threshold_pace = Column(Integer, nullable=True)  # Threshold pace in seconds per km
    running_threshold_hr = Column(Integer, nullable=True)  # Lactate Threshold Heart Rate for running
    
    # Swimming
    swim_threshold_pace = Column(Integer, nullable=True)  # Threshold pace in seconds per 100m
    swim_threshold_hr = Column(Integer, nullable=True)  # Lactate Threshold Heart Rate for swimming
    
    # General Heart Rate Settings
    max_hr = Column(Integer, nullable=True)  # Maximum Heart Rate
    resting_hr = Column(Integer, nullable=True)  # Resting Heart Rate
    
    # Relationships
    training_plans = relationship("TrainingPlan", back_populates="user")
    garmin_activities = relationship("GarminActivity", back_populates="user")
    weekly_thresholds = relationship("WeeklyThreshold", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.email}>"
