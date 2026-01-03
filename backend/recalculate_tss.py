#!/usr/bin/env python3
"""
Migration script to recalculate TSS for all historical activities.

This fixes the bug where max_hr was incorrectly used instead of threshold_hr.
"""

import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.models.garmin_activity import GarminActivity
from src.models.user import User
from src.utils.calculations.tss_calculator import calculate_tss_from_activity
from src.config import settings

async def recalculate_all_tss():
    """Recalculate TSS for all activities with corrected threshold_hr."""
    
    print("=" * 80)
    print("TSS Recalculation Script")
    print("=" * 80)
    print()
    print("This script will recalculate TSS for all activities using the correct")
    print("threshold HR values (instead of incorrectly using max_hr).")
    print()
    
    # Create async engine
    engine = create_async_engine(settings.database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as db:
        # Get all users
        users_result = await db.execute(select(User))
        users = users_result.scalars().all()
        
        print(f"Found {len(users)} user(s)")
        print()
        
        total_activities = 0
        total_recalculated = 0
        total_unchanged = 0
        
        for user in users:
            print(f"Processing user: {user.email}")
            print("-" * 80)
            
            # Get all activities for this user
            activities_result = await db.execute(
                select(GarminActivity).where(GarminActivity.user_id == user.id)
            )
            activities = activities_result.scalars().all()
            
            print(f"  Found {len(activities)} activities")
            
            if len(activities) == 0:
                continue
            
            for activity in activities:
                total_activities += 1
                
                # Determine sport-specific threshold HR
                sport_key = activity.activity_type.lower()
                if 'cycl' in sport_key or 'bike' in sport_key:
                    threshold_hr = user.cycling_threshold_hr
                elif 'run' in sport_key:
                    threshold_hr = user.running_threshold_hr
                elif 'swim' in sport_key:
                    threshold_hr = user.swim_threshold_hr
                else:
                    # For "other" sports (skiing, tennis, etc.), use max_hr like TrainingPeaks does
                    # This gives more accurate TSS than using running threshold
                    threshold_hr = user.max_hr if user.max_hr else (user.running_threshold_hr or 165)
                
                # Prepare user settings with CORRECT threshold_hr
                user_settings = {
                    "ftp": user.ftp,
                    "threshold_pace": user.threshold_pace,
                    "threshold_hr": threshold_hr,
                    "max_hr": user.max_hr,
                    "resting_hr": user.resting_hr,
                }
                
                # Recalculate TSS
                old_tss = activity.calculated_tss
                new_tss = calculate_tss_from_activity(activity.raw_data, user_settings)
                
                # Update if changed
                if old_tss is None or abs(old_tss - new_tss) > 0.1:
                    activity.calculated_tss = new_tss
                    total_recalculated += 1
                    
                    # Show significant changes
                    if old_tss and abs(old_tss - new_tss) > 5:
                        print(f"  {activity.activity_name[:40]:40s} | {old_tss:6.1f} → {new_tss:6.1f} TSS ({new_tss - old_tss:+6.1f})")
                else:
                    total_unchanged += 1
            
            # Commit changes for this user
            await db.commit()
            print(f"  ✅ Updated {total_recalculated} activities for {user.email}")
            print()
        
        print("=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"Total activities processed: {total_activities}")
        print(f"Activities recalculated:    {total_recalculated}")
        print(f"Activities unchanged:       {total_unchanged}")
        print()
        
        if total_recalculated > 0:
            print("✅ TSS recalculation complete!")
            print()
            print("Next steps:")
            print("1. Restart the backend server to use the corrected TSS values")
            print("2. Refresh the Dashboard to see updated CTL/ATL/TSB metrics")
            print("3. All future activity syncs will use the correct threshold HR")
        else:
            print("ℹ️  No activities needed recalculation.")
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(recalculate_all_tss())
