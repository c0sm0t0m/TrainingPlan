#!/usr/bin/env python3
"""
Test Activity Detail API Endpoints

Tests the new /api/v1/activities endpoints:
- GET /activities/{id} - Activity detail
- GET /activities/{id}/track - GPS track
- GET /activities/{id}/streams - Time-series data
- GET /activities/{id}/splits - Lap splits
- GET /activities - Activity list
"""
import asyncio
import httpx
import sys
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

async def main():
    print("🧪 Testing Activity Detail API Endpoints\n")
    print("=" * 60)
    
    # First, login to get token
    print("\n1. Logging in...")
    async with httpx.AsyncClient() as client:
        login_response = await client.post(
            f"{BASE_URL}/auth/login",
            data={
                "username": "test@example.com",  # Update with your credentials
                "password": "test123"
            }
        )
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            print(f"   Response: {login_response.text}")
            print("\n⚠️  Please update credentials in the script")
            return
        
        token = login_response.json()["access_token"]
        print("✅ Login successful")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get list of activities first
        print("\n2. Fetching activity list...")
        list_response = await client.get(
            f"{BASE_URL}/activities?page=1&page_size=5",
            headers=headers
        )
        
        if list_response.status_code != 200:
            print(f"❌ Failed to fetch activities: {list_response.status_code}")
            print(f"   Response: {list_response.text}")
            return
        
        activities_data = list_response.json()
        print(f"✅ Found {activities_data['total']} total activities")
        
        if not activities_data['activities']:
            print("⚠️  No activities found. Please sync from Garmin first.")
            return
        
        # Get first activity ID
        first_activity = activities_data['activities'][0]
        activity_id = first_activity['id']
        print(f"\n📍 Testing with activity ID {activity_id}:")
        print(f"   Name: {first_activity['activity_name']}")
        print(f"   Type: {first_activity['activity_type']}")
        print(f"   Date: {first_activity['date']}")
        
        # Test 1: Get activity detail
        print(f"\n3. Testing GET /activities/{activity_id}")
        detail_response = await client.get(
            f"{BASE_URL}/activities/{activity_id}",
            headers=headers
        )
        
        if detail_response.status_code == 200:
            detail = detail_response.json()
            print("✅ Activity detail retrieved")
            print(f"   Duration: {detail.get('duration_seconds', 0) / 60:.1f} minutes")
            print(f"   Distance: {(detail.get('distance_meters', 0) / 1000):.2f} km")
            print(f"   TSS: {detail.get('calculated_tss', 'N/A')}")
            print(f"   IF: {detail.get('intensity_factor', 'N/A')}")
            print(f"   Avg HR: {detail.get('average_hr', 'N/A')} bpm")
        else:
            print(f"❌ Failed: {detail_response.status_code}")
            print(f"   Response: {detail_response.text}")
        
        # Test 2: Get GPS track
        print(f"\n4. Testing GET /activities/{activity_id}/track")
        track_response = await client.get(
            f"{BASE_URL}/activities/{activity_id}/track",
            headers=headers
        )
        
        if track_response.status_code == 200:
            track = track_response.json()
            print(f"✅ GPS track retrieved")
            print(f"   Total points: {track['total_points']}")
            print(f"   Has elevation: {track['has_elevation']}")
            if track['track_points']:
                first_point = track['track_points'][0]
                print(f"   First point: ({first_point['lat']:.6f}, {first_point['lng']:.6f})")
        else:
            print(f"❌ Failed: {track_response.status_code}")
            print(f"   Response: {track_response.text}")
        
        # Test 3: Get time-series streams
        print(f"\n5. Testing GET /activities/{activity_id}/streams")
        streams_response = await client.get(
            f"{BASE_URL}/activities/{activity_id}/streams",
            headers=headers
        )
        
        if streams_response.status_code == 200:
            streams = streams_response.json()
            print(f"✅ Time-series streams retrieved")
            print(f"   Total samples: {streams['total_samples']}")
            stream_data = streams['streams']
            available_streams = []
            if stream_data.get('heart_rate_bpm'):
                available_streams.append(f"HR ({len(stream_data['heart_rate_bpm'])} points)")
            if stream_data.get('power_watts'):
                available_streams.append(f"Power ({len(stream_data['power_watts'])} points)")
            if stream_data.get('pace_min_per_km'):
                available_streams.append(f"Pace ({len(stream_data['pace_min_per_km'])} points)")
            if stream_data.get('elevation_meters'):
                available_streams.append(f"Elevation ({len(stream_data['elevation_meters'])} points)")
            print(f"   Available: {', '.join(available_streams) if available_streams else 'None'}")
        else:
            print(f"❌ Failed: {streams_response.status_code}")
            print(f"   Response: {streams_response.text}")
        
        # Test 4: Get lap splits
        print(f"\n6. Testing GET /activities/{activity_id}/splits")
        splits_response = await client.get(
            f"{BASE_URL}/activities/{activity_id}/splits",
            headers=headers
        )
        
        if splits_response.status_code == 200:
            splits = splits_response.json()
            print(f"✅ Lap splits retrieved")
            print(f"   Total laps: {splits['total_laps']}")
            if splits['splits']:
                first_lap = splits['splits'][0]
                print(f"   Lap 1: {(first_lap['distance_meters'] / 1000):.2f} km in {first_lap['duration_seconds'] / 60:.1f} min")
        else:
            print(f"❌ Failed: {splits_response.status_code}")
            print(f"   Response: {splits_response.text}")
        
        # Test 5: Update activity
        print(f"\n7. Testing PATCH /activities/{activity_id}")
        update_response = await client.patch(
            f"{BASE_URL}/activities/{activity_id}",
            headers=headers,
            json={"activity_name": f"{first_activity['activity_name']} (Updated)"}
        )
        
        if update_response.status_code == 200:
            updated = update_response.json()
            print(f"✅ Activity updated")
            print(f"   New name: {updated['activity_name']}")
            
            # Revert the change
            await client.patch(
                f"{BASE_URL}/activities/{activity_id}",
                headers=headers,
                json={"activity_name": first_activity['activity_name']}
            )
            print("   ↩️  Reverted change")
        else:
            print(f"❌ Failed: {update_response.status_code}")
            print(f"   Response: {update_response.text}")
        
        # Test 6: List with filters
        print(f"\n8. Testing GET /activities with filters")
        filtered_response = await client.get(
            f"{BASE_URL}/activities?page=1&page_size=3&sport_type=running",
            headers=headers
        )
        
        if filtered_response.status_code == 200:
            filtered = filtered_response.json()
            print(f"✅ Filtered list retrieved")
            print(f"   Running activities: {filtered['total']}")
            print(f"   Showing page {filtered['page']} ({len(filtered['activities'])} items)")
        else:
            print(f"❌ Failed: {filtered_response.status_code}")
            print(f"   Response: {filtered_response.text}")
    
    print("\n" + "=" * 60)
    print("✅ API endpoint testing complete!")
    print("\n📝 Next steps:")
    print("   1. Verify GPS track data is correctly parsed")
    print("   2. Check time-series data format for charts")
    print("   3. Test with activities that have power data")
    print("   4. Begin frontend implementation (Phase 2)")


if __name__ == "__main__":
    asyncio.run(main())
