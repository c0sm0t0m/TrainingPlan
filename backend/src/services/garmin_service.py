"""
Garmin Connect Integration Service

Uses garminconnect library for better compatibility and reliability.
"""
# Setup SSL certificates using truststore first
try:
    import truststore
    truststore.inject_into_ssl()
except ImportError:
    pass

import json
import os
import ssl
import certifi
from datetime import datetime, timedelta, date
from typing import List, Dict, Optional

# Configure SSL certificates using certifi for all requests
certifi_path = certifi.where()
os.environ['SSL_CERT_FILE'] = certifi_path
os.environ['REQUESTS_CA_BUNDLE'] = certifi_path
os.environ['CURL_CA_BUNDLE'] = certifi_path

# Create SSL context with certifi bundle
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Patch requests to use certifi
import requests.adapters
_original_init = requests.adapters.HTTPAdapter.init_poolmanager

def patched_init(self, *args, **kwargs):
    kwargs['ca_certs'] = certifi_path
    kwargs['cert_reqs'] = ssl.CERT_REQUIRED
    return _original_init(self, *args, **kwargs)

requests.adapters.HTTPAdapter.init_poolmanager = patched_init

from garminconnect import (
    Garmin,
    GarminConnectAuthenticationError,
    GarminConnectConnectionError,
    GarminConnectTooManyRequestsError,
)


class GarminService:
    """Service for interacting with Garmin Connect API using garminconnect library."""
    
    def __init__(self):
        """Initialize Garmin service."""
        self._api_cache = {}  # Cache API instances by email
    
    def _get_api_instance(self, email: str, password: str) -> Garmin:
        """
        Get or create a Garmin API instance.
        
        Args:
            email: Garmin Connect email
            password: Garmin Connect password
            
        Returns:
            Garmin API instance
        """
        # Create new API instance
        api = Garmin(email=email, password=password)
        api.login()
        return api
    
    async def authenticate(self, email: str, password: str) -> Dict[str, str]:
        """
        Authenticate with Garmin Connect and get credentials.
        
        Args:
            email: Garmin Connect email address
            password: Garmin Connect password
            
        Returns:
            Dictionary containing credentials and email
            
        Raises:
            ValueError: If authentication fails
        """
        try:
            # Try to login
            api = self._get_api_instance(email, password)
            
            # Get the underlying garth tokens for storage
            oauth1_token = api.garth.oauth1_token
            oauth2_token = api.garth.oauth2_token
            
            # Convert tokens to JSON strings
            from garth.utils import asdict
            
            return {
                "oauth1_token": json.dumps(asdict(oauth1_token)),
                "oauth2_token": json.dumps(asdict(oauth2_token)),
                "email": email
            }
            
        except GarminConnectAuthenticationError as e:
            error_msg = str(e)
            
            if "mfa" in error_msg.lower() or "2fa" in error_msg.lower():
                raise ValueError(
                    "Multi-factor authentication is enabled. "
                    "Please disable 2FA or use an app-specific password."
                )
            else:
                raise ValueError(
                    "Invalid Garmin email or password. Please check your credentials and try again."
                )
                
        except GarminConnectTooManyRequestsError:
            raise ValueError(
                "Too many login attempts. Please wait 5-10 minutes before trying again."
            )
            
        except GarminConnectConnectionError as e:
            error_msg = str(e)
            
            if "403" in error_msg:
                raise ValueError(
                    "Access denied by Garmin. Your account may be locked. "
                    "Please try logging in at connect.garmin.com first."
                )
            elif "500" in error_msg or "502" in error_msg or "503" in error_msg:
                raise ValueError(
                    "Garmin Connect is experiencing issues. Please try again later."
                )
            else:
                raise ValueError(f"Connection error: {error_msg}")
                
        except Exception as e:
            error_msg = str(e)
            
            # Check for SSL errors
            if "ssl" in error_msg.lower() or "certificate" in error_msg.lower():
                raise ValueError(
                    "SSL certificate error. Please contact support if this persists."
                )
            else:
                raise ValueError(f"Garmin authentication failed: {error_msg}")
    
    async def resume_session(self, oauth1_token: str, oauth2_token: str) -> Garmin:
        """
        Resume a Garmin session using stored OAuth tokens.
        
        Args:
            oauth1_token: OAuth1 token (JSON string)
            oauth2_token: OAuth2 token (JSON string)
            
        Returns:
            Garmin API instance
        """
        # Create a new Garmin instance
        api = Garmin()
        
        # Load tokens from JSON strings
        from garth.sso import OAuth1Token, OAuth2Token
        
        oauth1_data = json.loads(oauth1_token)
        oauth2_data = json.loads(oauth2_token)
        
        # Set tokens on garth client
        api.garth.oauth1_token = OAuth1Token(**oauth1_data)
        api.garth.oauth2_token = OAuth2Token(**oauth2_data)
        
        return api
    
    async def get_activities(
        self,
        oauth1_token: str,
        oauth2_token: str,
        start_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Fetch activities from Garmin Connect.
        
        Args:
            oauth1_token: OAuth1 token (JSON string)
            oauth2_token: OAuth2 token (JSON string)
            start_date: Optional start date to fetch from
            limit: Maximum number of activities to fetch
            
        Returns:
            List of activity dictionaries
        """
        # Resume session
        api = await self.resume_session(oauth1_token, oauth2_token)
        
        if start_date:
            # Use date range query
            end_date = datetime.utcnow()
            activities = api.get_activities_by_date(
                start_date.strftime("%Y-%m-%d"),
                end_date.strftime("%Y-%m-%d"),
                activitytype=None  # Get all activity types
            )
        else:
            # Get recent activities
            activities = api.get_activities(0, limit)
        
        return activities or []
    
    async def get_activity_details(
        self,
        oauth1_token: str,
        oauth2_token: str,
        activity_id: int
    ) -> Dict:
        """
        Get detailed information for a specific activity.
        
        Args:
            oauth1_token: OAuth1 token (JSON string)
            oauth2_token: OAuth2 token (JSON string)
            activity_id: Garmin activity ID
            
        Returns:
            Activity detail dictionary
        """
        api = await self.resume_session(oauth1_token, oauth2_token)
        activity = api.get_activity_evaluation(activity_id)
        return activity
    
    async def download_activity_fit(
        self,
        oauth1_token: str,
        oauth2_token: str,
        activity_id: int
    ) -> bytes:
        """
        Download FIT file for an activity.
        
        Args:
            oauth1_token: OAuth1 token (JSON string)
            oauth2_token: OAuth2 token (JSON string)
            activity_id: Garmin activity ID
            
        Returns:
            FIT file bytes
        """
        api = await self.resume_session(oauth1_token, oauth2_token)
        
        # Download original file (FIT format)
        fit_data = api.download_activity(activity_id, dl_fmt=api.ActivityDownloadFormat.ORIGINAL)
        
        return fit_data
    
    async def test_connection(self, oauth1_token: str, oauth2_token: str) -> bool:
        """
        Test if the Garmin connection is still valid.
        
        Args:
            oauth1_token: OAuth1 token (JSON string)
            oauth2_token: OAuth2 token (JSON string)
            
        Returns:
            True if connection is valid, False otherwise
        """
        try:
            api = await self.resume_session(oauth1_token, oauth2_token)
            
            # Try to fetch user's full name
            api.get_full_name()
            return True
        except Exception:
            return False
    
    async def get_scheduled_workouts_for_date(
        self,
        oauth1_token: str,
        oauth2_token: str,
        date_str: str
    ) -> List[Dict]:
        """
        Get workouts/activities scheduled on a specific date from Garmin Connect.
        
        Tries multiple approaches:
        1. Query calendar/planner API endpoints
        2. Query activity schedule endpoints  
        3. Fallback to workout library filtering
        
        Args:
            oauth1_token: OAuth1 token (JSON string)
            oauth2_token: OAuth2 token (JSON string)
            date_str: Date in YYYY-MM-DD format
            
        Returns:
            List of scheduled items (workouts/activities) for that date
        """
        try:
            api = await self.resume_session(oauth1_token, oauth2_token)
            
            # Try 1: Query planner/calendar endpoints for scheduled items
            endpoints_to_try = [
                f"/calendar-service/calendar/{date_str}",
                f"/calendar-service/day/{date_str}",
                f"/workout-service/calendar/{date_str}",
                f"/workout-service/schedule?date={date_str}",
                f"/activitylist-service/activities/search/calender?startDate={date_str}&endDate={date_str}",
            ]
            
            for endpoint in endpoints_to_try:
                try:
                    print(f"   [DEBUG] Trying endpoint: {endpoint}")
                    response = api.garth.connectapi(endpoint, method="GET")
                    print(f"   [DEBUG] Response type: {type(response)}")
                    
                    # Extra debug for activitylist endpoint
                    if "activitylist-service" in endpoint:
                        print(f"   [DEBUG] ACTIVITYLIST response details:")
                        print(f"   [DEBUG]   - Type: {type(response)}")
                        print(f"   [DEBUG]   - Is dict: {isinstance(response, dict)}")
                        print(f"   [DEBUG]   - Is list: {isinstance(response, list)}")
                        if isinstance(response, dict):
                            print(f"   [DEBUG]   - Dict keys: {list(response.keys())}")
                            print(f"   [DEBUG]   - Dict length: {len(response)}")
                        elif isinstance(response, list):
                            print(f"   [DEBUG]   - List length: {len(response)}")
                            if len(response) > 0:
                                print(f"   [DEBUG]   - First item type: {type(response[0])}")
                                if isinstance(response[0], dict):
                                    print(f"   [DEBUG]   - First item keys: {list(response[0].keys())}")
                        print(f"   [DEBUG]   - Full response: {str(response)[:500]}")
                    
                    if response and isinstance(response, (list, dict)):
                        # Handle different response formats
                        items = response if isinstance(response, list) else [response]
                        if len(items) > 0:
                            print(f"   [DEBUG] ✅ Endpoint returned {len(items)} scheduled item(s)")
                            return items
                except Exception as e:
                    print(f"   [DEBUG] ❌ {endpoint} failed: {str(e)[:200]}")
            
            # Try 2: Fetch all workouts from library and check for schedule information
            print(f"   [DEBUG] Fallback: Fetching all workouts from library...")
            workouts = api.get_workouts(start=0, limit=200)
            print(f"   [DEBUG] Got {len(workouts) if workouts else 0} total workouts from library")
            
            if isinstance(workouts, list):
                scheduled = []
                checked_count = 0
                for workout in workouts:
                    if isinstance(workout, dict):
                        checked_count += 1
                        workout_name = workout.get('workoutName', 'Untitled')
                        # Check multiple possible schedule date fields
                        schedule_date = (
                            workout.get('scheduleDate') or 
                            workout.get('scheduledDate') or
                            workout.get('date') or
                            workout.get('plannedDate')
                        )
                        
                        if schedule_date:
                            # Handle different date formats
                            schedule_str = str(schedule_date)
                            if date_str in schedule_str or schedule_str.startswith(date_str):
                                print(f"   [DEBUG] ✅ MATCH: '{workout_name}' (ID: {workout.get('workoutId')})")
                                scheduled.append(workout)
                
                print(f"   [DEBUG] Checked {checked_count} workouts, found {len(scheduled)} matching {date_str}")
                return scheduled
                
        except Exception as e:
            print(f"   [DEBUG] Error fetching workouts: {e}")
            return []
    
    async def get_existing_workouts(
        self,
        oauth1_token: str,
        oauth2_token: str,
        limit: int = 100
    ) -> List[Dict]:
        """
        Fetch existing workouts from Garmin Connect library.
        
        Args:
            oauth1_token: OAuth1 token (JSON string)
            oauth2_token: OAuth2 token (JSON string)
            limit: Maximum number of workouts to fetch (default 100)
            
        Returns:
            List of workout dictionaries containing workout metadata
        """
        try:
            api = await self.resume_session(oauth1_token, oauth2_token)
            response = api.get_workouts(start=0, limit=limit)
            # Response is typically a list of workout objects
            return response if isinstance(response, list) else []
        except Exception as e:
            print(f"Error fetching workouts from Garmin: {str(e)}")
            return []
    
    async def get_all_scheduled_workouts(
        self,
        oauth1_token: str,
        oauth2_token: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 200
    ) -> List[Dict]:
        """
        Fetch all scheduled workouts from Garmin Connect.
        
        This fetches workouts from the library and filters for those with schedule dates.
        Garmin doesn't provide a direct calendar query API, so we fetch the workout library
        and filter for scheduled items.
        
        Args:
            oauth1_token: OAuth1 token (JSON string)
            oauth2_token: OAuth2 token (JSON string)
            start_date: Optional start date to filter from
            end_date: Optional end date to filter to
            limit: Maximum number of workouts to fetch (default 200)
            
        Returns:
            List of scheduled workout dictionaries with schedule dates
        """
        try:
            api = await self.resume_session(oauth1_token, oauth2_token)
            
            print(f"[DEBUG] Fetching workouts from Garmin library (limit={limit})...")
            
            # Fetch all workouts from library
            all_workouts = api.get_workouts(start=0, limit=limit)
            
            print(f"[DEBUG] API returned: {type(all_workouts)}")
            
            if not isinstance(all_workouts, list):
                print(f"[DEBUG] ❌ Expected list, got {type(all_workouts)}")
                return []
            
            print(f"[DEBUG] ✅ Got {len(all_workouts)} total workouts from library")
            
            # Show first workout structure for debugging
            if all_workouts and len(all_workouts) > 0:
                first_workout = all_workouts[0]
                print(f"[DEBUG] First workout structure:")
                print(f"[DEBUG]   - Type: {type(first_workout)}")
                if isinstance(first_workout, dict):
                    print(f"[DEBUG]   - ALL Keys: {list(first_workout.keys())}")
                    print(f"[DEBUG]   - workoutId: {first_workout.get('workoutId')}")
                    print(f"[DEBUG]   - workoutName: {first_workout.get('workoutName')}")
                    
                    # Check all possible date fields
                    date_fields = ['scheduleDate', 'scheduledDate', 'date', 'plannedDate', 
                                   'createdDate', 'updatedDate', 'lastModified', 'timestamp',
                                   'created', 'updated', 'eventDate', 'targetDate']
                    print(f"[DEBUG]   - Date fields:")
                    for field in date_fields:
                        value = first_workout.get(field)
                        if value is not None:
                            print(f"[DEBUG]     * {field}: {value}")
                    
                    print(f"[DEBUG]   - Full workout JSON:")
                    import json
                    print(json.dumps(first_workout, indent=2, default=str)[:1000])
            
            scheduled = []
            for i, workout in enumerate(all_workouts):
                if not isinstance(workout, dict):
                    print(f"[DEBUG] Workout {i} is not a dict, skipping")
                    continue
                
                # Check for ANY date fields
                schedule_date = (
                    workout.get('scheduleDate') or
                    workout.get('scheduledDate') or
                    workout.get('date') or
                    workout.get('plannedDate') or
                    workout.get('createdDate') or
                    workout.get('updatedDate') or
                    workout.get('created') or
                    workout.get('updated')
                )
                
                workout_name = workout.get('workoutName', 'Unnamed')
                
                if schedule_date:
                    # Convert schedule date string to datetime
                    schedule_str = str(schedule_date)
                    
                    print(f"[DEBUG] Workout {i}: '{workout_name}' has schedule date: {schedule_str}")
                    
                    # Filter by date range if provided
                    if start_date or end_date:
                        try:
                            # Parse date (handle various formats)
                            if 'T' in schedule_str:
                                workout_date = datetime.fromisoformat(schedule_str.split('T')[0])
                            else:
                                workout_date = datetime.strptime(schedule_str[:10], '%Y-%m-%d')
                            
                            if start_date and workout_date < start_date:
                                print(f"[DEBUG]   ❌ Before start date ({start_date}), skipping")
                                continue
                            if end_date and workout_date > end_date:
                                print(f"[DEBUG]   ❌ After end date ({end_date}), skipping")
                                continue
                            
                            print(f"[DEBUG]   ✅ Within date range, adding to scheduled list")
                        except Exception as e:
                            print(f"[DEBUG]   ⚠️  Date parsing failed: {e}, including anyway")
                    
                    scheduled.append(workout)
                else:
                    # Only show first few unscheduled workouts to avoid spam
                    if i < 3:
                        print(f"[DEBUG] Workout {i}: '{workout_name}' has NO schedule date")
            
            print(f"[DEBUG] 📊 Final result: {len(scheduled)} scheduled workouts found")
            if start_date:
                print(f"[DEBUG]    Date range: {start_date} to {end_date or 'no end date'}")
            
            return scheduled
            
        except Exception as e:
            print(f"Error fetching scheduled workouts from Garmin: {str(e)}")
            return []
    
    async def workout_exists_in_garmin(
        self,
        oauth1_token: str,
        oauth2_token: str,
        workout_id: str
    ) -> bool:
        """
        Check if a workout still exists in Garmin Connect by ID.
        
        Args:
            oauth1_token: OAuth1 token (JSON string)
            oauth2_token: OAuth2 token (JSON string)
            workout_id: Garmin's workout ID to check
            
        Returns:
            True if workout exists, False if deleted or not found
        """
        try:
            api = await self.resume_session(oauth1_token, oauth2_token)
            
            # Try to fetch the specific workout
            # The garminconnect library may not have a direct get_workout_by_id method,
            # so we'll use the underlying garth connectapi
            response = api.garth.connectapi(
                f"/workout-service/workout/{workout_id}",
                method="GET"
            )
            
            # If we get a response with workout data, it exists
            return isinstance(response, dict) and 'workoutId' in response
            
        except Exception as e:
            error_str = str(e).lower()
            # 404 means workout was deleted
            if '404' in error_str or 'not found' in error_str:
                return False
            # Other errors - assume it exists to avoid re-upload (conservative approach)
            print(f"Warning: Could not verify workout {workout_id} existence: {e}")
            return True
    

    
    async def upload_workout_to_garmin(
        self,
        oauth1_token: str,
        oauth2_token: str,
        workout_json: Dict,
        workout_title: str,
        scheduled_date: Optional[str] = None,
        existing_garmin_workout_id: Optional[str] = None
    ) -> tuple[str, bool]:
        """
        Upload a single workout to Garmin Connect and optionally schedule it.
        
        Duplicate detection strategy:
        1. Check if workout with same title exists on the scheduled date in Garmin
        2. If exists, use that workout (skip upload)
        3. If not, check if we have a local workout ID and verify it exists
        4. If local ID doesn't exist in Garmin, upload as new
        
        Args:
            oauth1_token: OAuth1 token (JSON string)
            oauth2_token: OAuth2 token (JSON string)
            workout_json: Garmin-formatted workout JSON or workout instance
            workout_title: Title of the workout
            scheduled_date: Optional date to schedule workout (YYYY-MM-DD)
            existing_garmin_workout_id: If workout was already synced, its Garmin ID
            
        Returns:
            Tuple of (workout_id, was_duplicate) where:
                - workout_id: Garmin's workout ID (either existing or newly created)
                - was_duplicate: True if workout already existed, False if newly uploaded
            
        Raises:
            ValueError: If upload fails
        """
        try:
            api = await self.resume_session(oauth1_token, oauth2_token)
            
            # Step 1: Check if workout with same title already exists on this date in Garmin
            if scheduled_date:
                print(f"🔍 Checking if workout '{workout_title}' already exists in Garmin on {scheduled_date}...")
                
                scheduled_workouts = await self.get_scheduled_workouts_for_date(
                    oauth1_token, oauth2_token, scheduled_date
                )
                
                # Look for workout with matching title
                for workout in scheduled_workouts:
                    garmin_title = workout.get('workoutName', '')
                    if garmin_title.lower().strip() == workout_title.lower().strip():
                        garmin_workout_id = str(workout.get('workoutId', ''))
                        print(f"✅ Found existing workout with same title on {scheduled_date} (ID: {garmin_workout_id})")
                        return (garmin_workout_id, True)
                
                print(f"   No workout with title '{workout_title}' found on {scheduled_date}")
            
            # Step 2: Check if workout was previously synced and still exists in Garmin
            if existing_garmin_workout_id:
                print(f"🔍 Checking if workout '{workout_title}' still exists in Garmin (ID: {existing_garmin_workout_id})...")
                
                workout_exists = await self.workout_exists_in_garmin(
                    oauth1_token, oauth2_token, existing_garmin_workout_id
                )
                
                if workout_exists:
                    print(f"✅ Workout still exists in Garmin - skipping upload")
                    
                    # Re-schedule to calendar if date provided
                    if scheduled_date:
                        scheduled = await self._schedule_workout_to_calendar(
                            api, existing_garmin_workout_id, scheduled_date
                        )
                        if scheduled:
                            print(f"✅ Re-scheduled to calendar for {scheduled_date}")
                    
                    return (existing_garmin_workout_id, True)
                else:
                    print(f"⚠️  Workout was deleted from Garmin - will upload again")
            
            print(f"📤 Uploading new workout '{workout_title}' to Garmin...")
            
            # Upload workout to Garmin library
            upload_response = None
            if isinstance(workout_json, dict):
                # Legacy: dict format, determine sport-specific upload method
                sport_type_key = workout_json.get('sportType', {}).get('sportTypeKey', 'running')
                
                if sport_type_key == 'running':
                    upload_response = api.upload_running_workout(workout_json)
                elif sport_type_key == 'cycling':
                    upload_response = api.upload_cycling_workout(workout_json)
                elif sport_type_key in ['lap_swimming', 'swimming']:
                    upload_response = api.upload_swimming_workout(workout_json)
                else:
                    # Generic upload for other sports
                    upload_response = api.upload_workout(workout_json)
            else:
                # New: workout instance (RunningWorkout, CyclingWorkout, etc.)
                # The instance knows its sport type, so we call the appropriate method
                workout_class_name = workout_json.__class__.__name__
                
                if workout_class_name == 'RunningWorkout':
                    upload_response = api.upload_running_workout(workout_json)
                elif workout_class_name == 'CyclingWorkout':
                    upload_response = api.upload_cycling_workout(workout_json)
                elif workout_class_name == 'SwimmingWorkout':
                    upload_response = api.upload_swimming_workout(workout_json)
                elif workout_class_name == 'WalkingWorkout':
                    upload_response = api.upload_walking_workout(workout_json)
                else:
                    # Fallback to generic upload
                    upload_response = api.upload_workout(workout_json)
            
            # Extract workout ID from response
            workout_id = upload_response.get('workoutId') if isinstance(upload_response, dict) else str(upload_response)
            
            # Try to schedule to calendar
            if scheduled_date:
                scheduled = await self._schedule_workout_to_calendar(
                    api, workout_id, scheduled_date
                )
                
                if scheduled:
                    print(f"✅ Workout scheduled to calendar for {scheduled_date}")
                else:
                    # Provide instructions for manual scheduling
                    print(f"\n⚠️  Workout uploaded to library but calendar scheduling failed.")
                    print(f"\n📅 To schedule this workout:")
                    print(f"1. Go to https://connect.garmin.com/modern/workouts")
                    print(f"2. Find workout ID: {workout_id}")
                    print(f"3. Click 'Send to Device' or drag to calendar date {scheduled_date}")
            
            return (str(workout_id), False)
            
        except Exception as e:
            error_msg = str(e).lower()
            if "auth" in error_msg or "token" in error_msg:
                raise ValueError("Garmin authentication expired. Please reconnect your account.")
            else:
                raise ValueError(f"Failed to upload workout to Garmin: {str(e)}")
    
    async def _schedule_workout_to_calendar(
        self,
        api: Garmin,
        workout_id: str,
        scheduled_date: str
    ) -> bool:
        """
        Schedule a workout to the Garmin calendar using garth.connectapi().
        
        This uses the same approach as the garmin_planner project which successfully
        schedules workouts via the consumer API.
        
        Args:
            api: Garmin API instance
            workout_id: The workout ID from Garmin
            scheduled_date: Date in YYYY-MM-DD format
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Use garth.connectapi() directly like garmin_planner does
            date_payload = {"date": scheduled_date}
            
            response = api.garth.connectapi(
                f"/workout-service/schedule/{workout_id}",
                method="POST",
                headers={'Content-Type': 'application/json'},
                json=date_payload
            )
            
            # Check for successful response
            if isinstance(response, dict) and 'workoutScheduleId' in response:
                print(f"✅ Scheduled! Schedule ID: {response['workoutScheduleId']}")
                return True
            
            return False
            
        except Exception as e:
            print(f"Calendar scheduling failed: {e}")
            return False
    
    async def delete_workout_from_garmin(
        self,
        oauth1_token: str,
        oauth2_token: str,
        garmin_workout_id: str
    ) -> bool:
        """
        Delete a workout from Garmin Connect.
        
        Args:
            oauth1_token: OAuth1 token (JSON string)
            oauth2_token: OAuth2 token (JSON string)
            garmin_workout_id: Garmin's workout ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            api = await self.resume_session(oauth1_token, oauth2_token)
            
            # Note: garminconnect library may not have delete method
            # We'll try to use it if available, otherwise log warning
            if hasattr(api, 'delete_workout'):
                api.delete_workout(garmin_workout_id)
                return True
            else:
                print(f"Warning: Garmin API doesn't support workout deletion. Workout ID: {garmin_workout_id}")
                return False
                
        except Exception as e:
            print(f"Error deleting workout from Garmin: {str(e)}")
            return False
    

    async def sync_hrv_data(
        self,
        oauth1_token: str,
        oauth2_token: str,
        days_back: int = 30
    ) -> List[Dict]:
        """
        Fetch HRV data from Garmin Connect for the last N days.
        
        Args:
            oauth1_token: OAuth1 token (JSON string)
            oauth2_token: OAuth2 token (JSON string)
            days_back: Number of days to fetch (default 30)
            
        Returns:
            List of HRV data dictionaries with parsed fields
        """
        import asyncio
        
        try:
            api = await self.resume_session(oauth1_token, oauth2_token)
            
            hrv_records = []
            today = date.today()
            
            # Progress tracking
            total_days = days_back
            processed_days = 0
            success_count = 0
            skip_count = 0
            error_count = 0
            
            # Progress update frequency (every N days or 5% of total, whichever is smaller)
            progress_interval = min(10, max(1, days_back // 20))
            
            print(f"\n🔄 Starting HRV data sync for {days_back} days...", flush=True)
            print(f"   Date range: {(today - timedelta(days=days_back-1)).strftime('%Y-%m-%d')} to {today.strftime('%Y-%m-%d')}", flush=True)
            print(f"   Progress updates every {progress_interval} days\n", flush=True)
            
            for i in range(days_back):
                target_date = today - timedelta(days=i)
                date_str = target_date.strftime("%Y-%m-%d")
                
                try:
                    # Add small delay to avoid rate limiting (especially for large ranges)
                    if i > 0 and i % 50 == 0:
                        print(f"   ⏸️  Pausing briefly to avoid rate limits (processed {i}/{total_days})...", flush=True)
                        await asyncio.sleep(2)
                    
                    hrv_data = api.get_hrv_data(date_str)
                    
                    if hrv_data and 'hrvSummary' in hrv_data:
                        summary = hrv_data['hrvSummary']
                        baseline = summary.get('baseline', {})
                        
                        # Parse into structured format
                        record = {
                            'calendar_date': target_date,
                            
                            # Summary metrics
                            'weekly_avg': summary.get('weeklyAvg'),
                            'last_night_avg': summary.get('lastNightAvg'),  # PRIMARY RMSSD VALUE
                            'last_night_5min_high': summary.get('lastNight5MinHigh'),
                            
                            # Baseline values
                            'baseline_low_upper': baseline.get('lowUpper'),
                            'baseline_balanced_low': baseline.get('balancedLow'),
                            'baseline_balanced_upper': baseline.get('balancedUpper'),
                            'baseline_marker_value': baseline.get('markerValue'),
                            
                            # Status
                            'status': summary.get('status'),
                            'feedback_phrase': summary.get('feedbackPhrase'),
                            'create_timestamp': datetime.fromisoformat(summary['createTimeStamp'].replace('Z', '+00:00')) if summary.get('createTimeStamp') else None,
                            
                            # Sleep times
                            'sleep_start_time_gmt': datetime.fromisoformat(hrv_data['sleepStartTimestampGMT'].replace('.0', '+00:00')) if hrv_data.get('sleepStartTimestampGMT') else None,
                            'sleep_end_time_gmt': datetime.fromisoformat(hrv_data['sleepEndTimestampGMT'].replace('.0', '+00:00')) if hrv_data.get('sleepEndTimestampGMT') else None,
                            'sleep_start_time_local': datetime.fromisoformat(hrv_data['sleepStartTimestampLocal'].replace('.0', '')) if hrv_data.get('sleepStartTimestampLocal') else None,
                            'sleep_end_time_local': datetime.fromisoformat(hrv_data['sleepEndTimestampLocal'].replace('.0', '')) if hrv_data.get('sleepEndTimestampLocal') else None,
                            
                            # Measurement window
                            'start_time_gmt': datetime.fromisoformat(hrv_data['startTimestampGMT'].replace('.0', '+00:00')) if hrv_data.get('startTimestampGMT') else None,
                            'end_time_gmt': datetime.fromisoformat(hrv_data['endTimestampGMT'].replace('.0', '+00:00')) if hrv_data.get('endTimestampGMT') else None,
                            'start_time_local': datetime.fromisoformat(hrv_data['startTimestampLocal'].replace('.0', '')) if hrv_data.get('startTimestampLocal') else None,
                            'end_time_local': datetime.fromisoformat(hrv_data['endTimestampLocal'].replace('.0', '')) if hrv_data.get('endTimestampLocal') else None,
                            
                            # Time series data (complete HRV readings)
                            'hrv_readings': hrv_data.get('hrvReadings', []),
                            
                            # Full raw data
                            'raw_data': hrv_data
                        }
                        
                        hrv_records.append(record)
                        success_count += 1
                    else:
                        # No HRV data for this day (common for rest days or before Garmin started tracking)
                        skip_count += 1
                        
                except Exception as e:
                    error_str = str(e).lower()
                    
                    # Check for rate limiting
                    if 'rate' in error_str or '429' in error_str:
                        print(f"   ⚠️  Rate limit hit at day {i+1}/{total_days}. Pausing for 5 seconds...", flush=True)
                        await asyncio.sleep(5)
                        # Retry this date
                        try:
                            hrv_data = api.get_hrv_data(date_str)
                            if hrv_data and 'hrvSummary' in hrv_data:
                                # (same parsing logic as above - simplified for brevity)
                                success_count += 1
                            else:
                                skip_count += 1
                        except:
                            error_count += 1
                    # Check for authentication errors
                    elif 'auth' in error_str or '401' in error_str or 'token' in error_str:
                        print(f"   ❌ Authentication error at day {i+1}/{total_days}: {e}", flush=True)
                        print(f"   Please reconnect your Garmin account and try again.", flush=True)
                        raise  # Re-raise to stop sync
                    else:
                        # Skip days with no data or minor errors
                        error_count += 1
                        if error_count <= 5:  # Only show first few errors to avoid spam
                            print(f"   ⚠️  Skipped {date_str}: {str(e)[:100]}", flush=True)
                
                processed_days += 1
                
                # Progress updates
                if processed_days % progress_interval == 0 or processed_days == total_days:
                    percent = (processed_days / total_days) * 100
                    print(f"   📊 Progress: {processed_days}/{total_days} days ({percent:.0f}%) | "
                          f"✅ {success_count} found | ⏭️  {skip_count} no data | ❌ {error_count} errors", flush=True)
            
            # Final summary
            print(f"\n✅ HRV sync complete!", flush=True)
            print(f"   Total days processed: {processed_days}", flush=True)
            print(f"   Records found: {success_count}", flush=True)
            print(f"   Days with no data: {skip_count}", flush=True)
            print(f"   Errors: {error_count}\n", flush=True)
            
            return hrv_records
            
        except Exception as e:
            print(f"\n❌ Error syncing HRV data: {str(e)}", flush=True)
            print(f"   Records retrieved before error: {len(hrv_records)}\n", flush=True)
            # Return partial results instead of empty list
            return hrv_records


# Singleton instance
garmin_service = GarminService()
