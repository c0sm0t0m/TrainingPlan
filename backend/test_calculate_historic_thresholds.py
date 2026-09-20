"""
Test script to calculate historic thresholds for all users.
"""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database import AsyncSessionLocal
from src.models.user import User
from src.utils.historic_thresholds import calculate_historic_thresholds
from sqlalchemy import select


async def main():
    """Calculate historic thresholds for all users."""
    print("=" * 80)
    print("HISTORIC THRESHOLD CALCULATION")
    print("=" * 80)
    
    async with AsyncSessionLocal() as db:
        # Get all users
        result = await db.execute(select(User))
        users = result.scalars().all()
        
        print(f"\n📋 Found {len(users)} users")
        
        for user in users:
            print(f"\n" + "=" * 80)
            print(f"USER: {user.email}")
            print("=" * 80)
            
            # Calculate thresholds
            stats = await calculate_historic_thresholds(
                user=user,
                db=db,
                lookback_weeks=104  # 2 years
            )
            
            print(f"\n✅ COMPLETED")
            print(f"   Weeks calculated: {stats['weeks_calculated']}")
            print(f"   Activities analyzed: {stats['activities_analyzed']}")
            print(f"   Date range: {stats['oldest_week']} to {stats['newest_week']}")
    
    print(f"\n" + "=" * 80)
    print("CALCULATION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
