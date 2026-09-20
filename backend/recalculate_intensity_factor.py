"""
Recalculate Intensity Factor (IF) for all existing activities.

This script updates all garmin_activities with calculated IF values.
Run after adding the intensity_factor column to existing activities.
"""
import asyncio
import sys
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

# Add parent directory to path
sys.path.insert(0, '/Users/boetthw3/Documents/99_Other/TrainingPlan/backend')

from src.database import AsyncSessionLocal
from src.models.garmin_activity import GarminActivity
from src.models.user import User
from src.utils.calculations.tss_calculator import calculate_tss_from_activity


async def recalculate_all_intensity_factors():
    """Recalculate IF for all activities."""
    
    async with AsyncSessionLocal() as db:
        # Get all activities
        result = await db.execute(
            select(GarminActivity, User)
            .join(User, GarminActivity.user_id == User.id)
            .order_by(GarminActivity.start_time_local)
        )
        
        activities_with_users = result.all()
        total = len(activities_with_users)
        
        print(f"Found {total} activities to process\n")
        
        updated_count = 0
        skipped_count = 0
        error_count = 0
        
        for idx, (activity, user) in enumerate(activities_with_users, 1):
            try:
                # Prepare activity dict (mimicking Garmin API response format)
                activity_dict = {
                    "activityType": {"typeKey": activity.activity_type},
                    "movingDuration": activity.moving_duration_seconds or activity.duration_seconds,
                    "duration": activity.duration_seconds,
                    "elapsedDuration": activity.elapsed_duration_seconds,
                    "averageHR": activity.average_hr,
                    "distance": activity.distance_meters,
                    "averageSpeed": activity.average_speed_mps,
                    "normPower": activity.normalized_power_watts,
                    "activityTrainingLoad": activity.training_load,
                }
                
                # Prepare user settings - select correct threshold_hr based on sport
                sport_key = activity.activity_type or ''
                if 'cycling' in sport_key.lower() or 'bike' in sport_key.lower():
                    threshold_hr = user.cycling_threshold_hr
                elif 'running' in sport_key.lower() or 'run' in sport_key.lower():
                    threshold_hr = user.running_threshold_hr
                elif 'swim' in sport_key.lower():
                    threshold_hr = user.swim_threshold_hr
                else:
                    # For other sports (skiing, hiking, etc.), use running threshold as baseline
                    threshold_hr = user.running_threshold_hr or 165
                
                user_settings = {
                    "ftp": user.ftp,
                    "threshold_pace": user.threshold_pace,
                    "swim_threshold_pace": user.swim_threshold_pace,
                    "threshold_hr": threshold_hr,
                    "max_hr": user.max_hr,
                    "resting_hr": user.resting_hr,
                }
                
                # Calculate TSS and IF
                calculated_tss, intensity_factor = calculate_tss_from_activity(activity_dict, user_settings)
                
                # Update activity
                activity.intensity_factor = intensity_factor
                
                if intensity_factor is not None:
                    updated_count += 1
                    status = f"✅ IF={intensity_factor:.2f}"
                else:
                    skipped_count += 1
                    status = "⚠️  IF=None (no threshold data)"
                
                # Progress update every 50 activities
                if idx % 50 == 0:
                    print(f"Progress: {idx}/{total} - Updated: {updated_count}, Skipped: {skipped_count}, Errors: {error_count}")
                
                # Show individual activity details for first 10 and last 10
                if idx <= 10 or idx > total - 10:
                    print(f"{idx:4d}. {activity.activity_name[:40]:40s} | {activity.activity_type:15s} | {status}")
                
            except Exception as e:
                error_count += 1
                print(f"❌ Error processing activity {activity.id}: {str(e)}")
                continue
        
        # Commit all changes
        await db.commit()
        
        print(f"\n{'='*80}")
        print(f"Recalculation Complete!")
        print(f"{'='*80}")
        print(f"Total activities:        {total}")
        print(f"✅ Updated with IF:      {updated_count}")
        print(f"⚠️  Skipped (no data):   {skipped_count}")
        print(f"❌ Errors:               {error_count}")
        print(f"{'='*80}\n")


if __name__ == "__main__":
    print("=" * 80)
    print("Intensity Factor (IF) Recalculation Script")
    print("=" * 80)
    print()
    
    asyncio.run(recalculate_all_intensity_factors())
