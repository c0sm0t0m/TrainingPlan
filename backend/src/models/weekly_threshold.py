"""
Weekly Threshold Model - Historic threshold values per week
"""
from sqlalchemy import Column, Integer, Float, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import relationship
from src.database import Base


class WeeklyThreshold(Base):
    """
    Store historic threshold values per week for accurate TSS calculations.
    
    Thresholds are calculated backwards from current values based on performance trends.
    Each week-year combination stores the estimated thresholds for that period.
    """
    __tablename__ = "weekly_thresholds"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Week identification (ISO week format)
    year = Column(Integer, nullable=False, index=True)  # e.g., 2025
    week = Column(Integer, nullable=False, index=True)  # 1-53 (ISO week number)
    
    # Threshold values for this week
    running_threshold_hr = Column(Integer)  # Lactate threshold HR for running
    cycling_threshold_hr = Column(Integer)  # Lactate threshold HR for cycling
    ftp = Column(Integer)  # Functional Threshold Power (watts)
    threshold_pace = Column(Float)  # Running threshold pace (min/km)
    swim_threshold_pace = Column(Float)  # Swimming threshold pace (min/100m)
    
    # Reference values
    max_hr = Column(Integer)  # Maximum heart rate
    resting_hr = Column(Integer)  # Resting heart rate
    
    # Calculation metadata
    calculation_method = Column(String)  # How this was calculated (e.g., "performance_trend", "manual", "current")
    confidence_score = Column(Float)  # 0-1, how confident we are in these values
    activities_used = Column(Integer)  # Number of activities analyzed for this week
    
    # Relationships
    user = relationship("User", back_populates="weekly_thresholds")
    
    # Ensure one threshold per week per user
    __table_args__ = (
        UniqueConstraint('user_id', 'year', 'week', name='_user_year_week_uc'),
    )
    
    def __repr__(self):
        return f"<WeeklyThreshold(user_id={self.user_id}, {self.year}-W{self.week:02d}, running_hr={self.running_threshold_hr}, ftp={self.ftp})>"
