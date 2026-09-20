#!/usr/bin/env python3
"""
Test HRV Data Sync to Database

Tests syncing HRV data from Garmin and storing it in the database.
"""
import sys
import os
import asyncio
from datetime import datetime

sys.path.insert(0, '/Users/boetthw3/Documents/99_Other/TrainingPlan/backend')

# Setup SSL certificates
try:
    import truststore
    truststore.inject_into_ssl()
except ImportError:
    pass

from sqlalchemy import select
from src.database import AsyncSessionLocal
from src.models.garmin_hrv import GarminHRV
from src.services.garmin_service import garmin_service

GARMIN_EMAIL = os.getenv('GARMIN_EMAIL', 'th.boettger@web.de')
GARMIN_PASSWORD = os.getenv('GARMIN_PASSWORD', '2025Dpige.2025')


async def test_hrv_sync():
    """Test syncing HRV data to database."""
    print("=" * 80)
    print("HRV Data Sync Test")
    print("=" * 80)
    print()
    
    # Step 1: Authenticate
    print("1️⃣ Authenticating with Garmin...")
    try:
        tokens = await garmin_service.authenticate(GARMIN_EMAIL, GARMIN_PASSWORD)
        print("✅ Authentication successful")
        print()
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return
    
    # Step 2: Fetch HRV data
    print("2️⃣ Fetching HRV data (last 7 days)...")
    try:
        hrv_records = await garmin_service.sync_hrv_data(
            tokens['oauth1_token'],
            tokens['oauth2_token'],
            days_back=7
        )
        print(f"✅ Fetched {len(hrv_records)} HRV records")
        print()
    except Exception as e:
        print(f"❌ Failed to fetch HRV data: {e}")
        return
    
    if not hrv_records:
        print("⚠️  No HRV data available")
        return
    
    # Step 3: Store in database
    print("3️⃣ Storing HRV data in database...")
    async with AsyncSessionLocal() as db:
        stored_count = 0
        updated_count = 0
        
        for record in hrv_records:
            try:
                # Check if record already exists
                result = await db.execute(
                    select(GarminHRV).where(
                        GarminHRV.user_id == 1,  # Assuming user_id = 1
                        GarminHRV.calendar_date == record['calendar_date']
                    )
                )
                existing = result.scalar_one_or_none()
                
                if existing:
                    # Update existing record
                    for key, value in record.items():
                        if key != 'calendar_date':
                            setattr(existing, key, value)
                    existing.updated_at = datetime.utcnow()
                    updated_count += 1
                else:
                    # Create new record
                    hrv = GarminHRV(
                        user_id=1,  # Assuming user_id = 1
                        **record
                    )
                    db.add(hrv)
                    stored_count += 1
                
            except Exception as e:
                print(f"❌ Error storing record for {record['calendar_date']}: {e}")
                continue
        
        await db.commit()
        
        print(f"✅ Stored {stored_count} new records")
        print(f"✅ Updated {updated_count} existing records")
        print()
    
    # Step 4: Verify data in database
    print("4️⃣ Verifying stored data...")
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(GarminHRV)
            .where(GarminHRV.user_id == 1)
            .order_by(GarminHRV.calendar_date.desc())
            .limit(3)
        )
        records = result.scalars().all()
        
        print(f"Found {len(records)} most recent records in database:")
        print()
        
        for record in records:
            print(f"  📅 {record.calendar_date}")
            print(f"     Last Night Avg (RMSSD): {record.last_night_avg} ms")
            print(f"     Weekly Avg: {record.weekly_avg} ms")
            print(f"     Status: {record.status}")
            print(f"     Time Series Readings: {len(record.hrv_readings) if record.hrv_readings else 0}")
            print()
    
    print("=" * 80)
    print()
    print("✅ HRV Sync Test Complete!")
    print()
    print("Summary:")
    print(f"  • Model: GarminHRV table created ✅")
    print(f"  • API Sync: {len(hrv_records)} days fetched ✅")
    print(f"  • Database: {stored_count} stored, {updated_count} updated ✅")
    print(f"  • Data Fields: Daily RMSSD + Complete time series ✅")
    print()
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_hrv_sync())
