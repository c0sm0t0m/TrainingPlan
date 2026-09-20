#!/usr/bin/env python3
import asyncio
import httpx

BASE_URL = "http://localhost:8000/api/v1"

async def check_cycling_data():
    async with httpx.AsyncClient() as client:
        # Login
        login_response = await client.post(
            f"{BASE_URL}/auth/login",
            data={"username": "tboettger@gmail.com", "password": "test123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get user profile
        print("👤 USER PROFILE")
        print("=" * 60)
        profile = await client.get(f"{BASE_URL}/auth/me", headers=headers)
        user_data = profile.json()
        print(f"   Cycling FTP: {user_data.get('cycling_ftp') or user_data.get('ftp', 'NOT SET')}")
        print(f"   Running Threshold HR: {user_data.get('running_threshold_hr', 'NOT SET')}")
        print()
        
        # Get cycling activities with raw response
        print("🚴 CYCLING ACTIVITIES")
        print("=" * 60)
        activities_response = await client.get(
            f"{BASE_URL}/garmin/activities?limit=20",
            headers=headers
        )
        all_activities = activities_response.json()
        
        # Filter cycling manually
        cycling_activities = []
        for act in all_activities:
            if 'cycling' in act.get('activity_type', '').lower():
                cycling_activities.append(act)
        
        if cycling_activities:
            print(f"   Found {len(cycling_activities)} cycling activities")
            print()
            for i, act in enumerate(cycling_activities[:5], 1):
                print(f"   {i}. {act.get('activity_name', 'Unnamed')}")
                print(f"      Date: {act.get('start_time_local', 'N/A')[:10]}")
                print(f"      Distance: {act.get('distance_km', 0):.1f} km")
                print(f"      Duration: {act.get('duration_seconds', 0) / 60:.0f} min")
                print(f"      Avg Power: {act.get('average_power', 'N/A')} W")
                print(f"      TSS: {act.get('calculated_tss', 'N/A')}")
                print()
        else:
            print("   No cycling activities found")
        
        # Get cycling CTL details
        print("📈 CYCLING CTL BREAKDOWN (Last 30 Days)")
        print("=" * 60)
        ctl_data = await client.get(
            f"{BASE_URL}/garmin/training-load?days=30&sport_type=cycling",
            headers=headers
        )
        ctl_days = ctl_data.json()
        
        if ctl_days:
            print(f"   Total days: {len(ctl_days)}")
            # Show last 10 days with TSS
            print(f"   Last 10 days with activities:")
            for day in ctl_days[-10:]:
                tss = day.get('tss', 0)
                if tss > 0:
                    print(f"      {day['date']}: TSS={tss:.1f}, CTL={day['ctl']:.1f}")
            print()
            print(f"   Current Cycling CTL: {ctl_days[-1]['ctl']:.1f}")
        else:
            print("   No CTL data")

asyncio.run(check_cycling_data())
