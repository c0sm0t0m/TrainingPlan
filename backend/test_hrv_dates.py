import asyncio
from datetime import date, timedelta

async def test_hrv_dates():
    """Test HRV date filtering logic"""
    
    # Calculate what the backend should be doing for 30-day request
    days_back = 30
    end_date = date.today()  # 2026-01-05
    start_date = end_date - timedelta(days=days_back)  # 2026-01-05 - 30 = 2025-12-06
    extended_start_date = start_date - timedelta(days=30)  # 2025-12-06 - 30 = 2025-11-06
    
    print(f"Today: {end_date}")
    print(f"Days back requested: {days_back}")
    print(f"Start date (displayed): {start_date}")
    print(f"Extended start (for calculation): {extended_start_date}")
    print(f"\nDate range shown in UI: {start_date} to {end_date}")
    print(f"Date range fetched for calculations: {extended_start_date} to {end_date}")
    print(f"\nTotal days displayed: {(end_date - start_date).days + 1}")
    print(f"Total days fetched: {(end_date - extended_start_date).days + 1}")

asyncio.run(test_hrv_dates())
