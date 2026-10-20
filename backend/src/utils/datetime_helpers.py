"""
DateTime utility functions for handling SQLite TEXT storage.

SQLite stores DateTime as TEXT strings, but we want to work with proper
datetime objects in Python for type safety and easier manipulation.
"""
from datetime import datetime, date
from typing import Optional, Union


def parse_sqlite_datetime(dt_str: Optional[str]) -> Optional[datetime]:
    """
    Parse SQLite TEXT datetime string to Python datetime object.
    
    SQLite format: "YYYY-MM-DD HH:MM:SS.ffffff"
    
    Args:
        dt_str: DateTime string from SQLite or None
        
    Returns:
        datetime object or None
    """
    if not dt_str:
        return None
    
    try:
        # Remove microseconds if present
        if '.' in dt_str:
            dt_str = dt_str.split('.')[0]
        return datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
    except (ValueError, AttributeError):
        # Fallback: try date-only format
        try:
            return datetime.strptime(dt_str[:10], "%Y-%m-%d")
        except (ValueError, AttributeError):
            return None


def datetime_to_sqlite_string(dt: Optional[Union[datetime, date]]) -> Optional[str]:
    """
    Convert Python datetime to SQLite TEXT format.
    
    Args:
        dt: datetime or date object
        
    Returns:
        String in SQLite format or None
    """
    if not dt:
        return None
    
    if isinstance(dt, datetime):
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    elif isinstance(dt, date):
        return dt.strftime("%Y-%m-%d")
    else:
        return str(dt)


def date_to_string(dt: Optional[Union[datetime, date, str]]) -> Optional[str]:
    """
    Extract date string (YYYY-MM-DD) from datetime, date, or string.
    
    Args:
        dt: datetime, date, or string
        
    Returns:
        Date string in YYYY-MM-DD format or None
    """
    if not dt:
        return None
    
    if isinstance(dt, datetime):
        return dt.date().isoformat()
    elif isinstance(dt, date):
        return dt.isoformat()
    elif isinstance(dt, str):
        # Parse from SQLite format and extract date
        parsed = parse_sqlite_datetime(dt)
        return parsed.date().isoformat() if parsed else dt[:10]
    else:
        return None


def compare_date_for_sqlite(dt: Union[datetime, date, str]) -> datetime:
    """
    Normalize a date/datetime for SQLAlchemy DateTime column comparisons.

    Returns a real datetime (not a date string). asyncpg/Postgres reject
    `timestamp >= varchar` when a YYYY-MM-DD string is bound as a parameter;
    SQLite DateTime columns still accept Python datetime via SQLAlchemy.
    """
    if isinstance(dt, datetime):
        return dt
    if isinstance(dt, date):
        return datetime.combine(dt, datetime.min.time())
    if isinstance(dt, str):
        parsed = parse_sqlite_datetime(dt)
        if parsed:
            return parsed
        try:
            return datetime.strptime(dt[:10], "%Y-%m-%d")
        except (ValueError, TypeError):
            raise ValueError(f"Cannot parse compare date: {dt!r}") from None
    raise TypeError(f"Unsupported compare date type: {type(dt)}")
