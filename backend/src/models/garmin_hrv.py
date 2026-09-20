"""
Garmin HRV (Heart Rate Variability) Database Model
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Date, JSON, Index
from sqlalchemy.orm import relationship

from src.database import Base


class GarminHRV(Base):
    """Garmin HRV model - stores daily HRV data from Garmin Connect"""
    __tablename__ = "garmin_hrv"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Date reference (one record per day)
    calendar_date = Column(Date, nullable=False, index=True)
    
    # Daily HRV Summary Metrics (from hrvSummary)
    weekly_avg = Column(Float, nullable=True)  # 7-day rolling average (ms)
    last_night_avg = Column(Float, nullable=True)  # Average HRV during sleep (ms) - PRIMARY RMSSD VALUE
    last_night_5min_high = Column(Float, nullable=True)  # Highest 5-min average (ms)
    
    # Baseline Values (personalized ranges)
    baseline_low_upper = Column(Float, nullable=True)  # Upper bound of "low" zone
    baseline_balanced_low = Column(Float, nullable=True)  # Lower bound of "balanced" zone
    baseline_balanced_upper = Column(Float, nullable=True)  # Upper bound of "balanced" zone
    baseline_marker_value = Column(Float, nullable=True)  # Normalized marker (0-1)
    
    # Status & Feedback
    status = Column(String, nullable=True)  # BALANCED, LOW, UNBALANCED, etc.
    feedback_phrase = Column(String, nullable=True)  # Garmin feedback key
    create_timestamp = Column(DateTime, nullable=True)  # When Garmin processed this data
    
    # Sleep Window (when HRV was measured)
    sleep_start_time_gmt = Column(DateTime, nullable=True)
    sleep_end_time_gmt = Column(DateTime, nullable=True)
    sleep_start_time_local = Column(DateTime, nullable=True)
    sleep_end_time_local = Column(DateTime, nullable=True)
    
    # Measurement Window (can be broader than sleep window)
    start_time_gmt = Column(DateTime, nullable=True)
    end_time_gmt = Column(DateTime, nullable=True)
    start_time_local = Column(DateTime, nullable=True)
    end_time_local = Column(DateTime, nullable=True)
    
    # Time Series Data (complete HRV readings throughout the night)
    # Each reading: { "hrvValue": 45, "readingTimeGMT": "...", "readingTimeLocal": "..." }
    hrv_readings = Column(JSON, nullable=True)  # Array of individual HRV measurements
    
    # Full raw response from Garmin (for future analysis)
    raw_data = Column(JSON, nullable=True)
    
    # Metadata
    synced_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationship to user
    user = relationship("User", back_populates="garmin_hrv_data")
    
    # Composite unique constraint: one HRV record per user per day
    __table_args__ = (
        Index('idx_user_date', 'user_id', 'calendar_date', unique=True),
    )
