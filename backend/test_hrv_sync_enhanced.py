#!/usr/bin/env python3
"""
Test HRV Sync with Enhanced Progress Tracking

Tests the improved HRV sync functionality with:
- Progress tracking for large date ranges
- Rate limiting handling
- Better error reporting
- Frequent progress updates
"""
import asyncio
import sys
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, '/Users/boetthw3/Documents/99_Other/TrainingPlan/backend')

from src.services.garmin_service import garmin_service


async def test_hrv_sync_small():
    """Test with small date range (30 days) - baseline test."""
    print("=" * 80)
    print("TEST 1: Small Date Range (30 days)")
    print("=" * 80)
    
    # These should be replaced with your actual Garmin credentials
    # Or load from database
    oauth1_token = '{"oauth_token": "..."}' 
    oauth2_token = '{"access_token": "..."}' 
    
    try:
        hrv_records = await garmin_service.sync_hrv_data(
            oauth1_token=oauth1_token,
            oauth2_token=oauth2_token,
            days_back=30
        )
        
        print(f"\n📊 Results:")
        print(f"   Records fetched: {len(hrv_records)}")
        
        if hrv_records:
            print(f"   Latest date: {hrv_records[0]['calendar_date']}")
            print(f"   Oldest date: {hrv_records[-1]['calendar_date']}")
            print(f"   Sample HRV value: {hrv_records[0].get('last_night_avg')} ms")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


async def test_hrv_sync_large():
    """Test with large date range (180 days) - stress test."""
    print("\n" + "=" * 80)
    print("TEST 2: Large Date Range (180 days) - Progress Tracking Test")
    print("=" * 80)
    
    oauth1_token = '{"oauth_token": "..."}' 
    oauth2_token = '{"access_token": "..."}' 
    
    try:
        start_time = datetime.now()
        
        hrv_records = await garmin_service.sync_hrv_data(
            oauth1_token=oauth1_token,
            oauth2_token=oauth2_token,
            days_back=180
        )
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"\n📊 Results:")
        print(f"   Records fetched: {len(hrv_records)}")
        print(f"   Duration: {duration:.1f} seconds")
        print(f"   Avg per day: {duration/180:.2f} seconds")
        
        if hrv_records:
            print(f"   Latest date: {hrv_records[0]['calendar_date']}")
            print(f"   Oldest date: {hrv_records[-1]['calendar_date']}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


async def test_hrv_sync_very_large():
    """Test with very large date range (365 days) - extreme test."""
    print("\n" + "=" * 80)
    print("TEST 3: Very Large Date Range (365 days) - Rate Limiting Test")
    print("=" * 80)
    
    oauth1_token = '{"oauth_token": "..."}' 
    oauth2_token = '{"access_token": "..."}' 
    
    try:
        start_time = datetime.now()
        
        hrv_records = await garmin_service.sync_hrv_data(
            oauth1_token=oauth1_token,
            oauth2_token=oauth2_token,
            days_back=365
        )
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"\n📊 Results:")
        print(f"   Records fetched: {len(hrv_records)}")
        print(f"   Duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
        print(f"   Avg per day: {duration/365:.2f} seconds")
        
        if hrv_records:
            print(f"   Latest date: {hrv_records[0]['calendar_date']}")
            print(f"   Oldest date: {hrv_records[-1]['calendar_date']}")
            
            # Data quality check
            with_data = sum(1 for r in hrv_records if r.get('last_night_avg'))
            print(f"   Records with HRV data: {with_data}/{len(hrv_records)} ({with_data/len(hrv_records)*100:.1f}%)")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Run all tests."""
    print("🧪 HRV Sync Enhanced Progress Tracking Tests")
    print(f"   Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    print("⚠️  NOTE: This test requires valid Garmin OAuth tokens.")
    print("   You can get these by:")
    print("   1. Running the backend: uvicorn src.main:app --reload")
    print("   2. Connecting your Garmin account via the API")
    print("   3. Copying the tokens from the database")
    print()
    
    response = input("Do you have valid tokens to test? (y/n): ")
    if response.lower() != 'y':
        print("\n⏭️  Skipping tests. Please connect Garmin account first.")
        return
    
    # Run tests sequentially
    await test_hrv_sync_small()
    
    response = input("\n\nContinue with 180-day test? (y/n): ")
    if response.lower() == 'y':
        await test_hrv_sync_large()
    
    response = input("\n\nContinue with 365-day test? (y/n): ")
    if response.lower() == 'y':
        await test_hrv_sync_very_large()
    
    print("\n\n" + "=" * 80)
    print("✅ All tests complete!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
