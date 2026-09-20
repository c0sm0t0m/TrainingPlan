#!/usr/bin/env python3
"""
Test CTL Consistency
Verifies that CTL values are the same regardless of the time range queried.
"""
import asyncio
import httpx
import sys

BASE_URL = "http://localhost:8000/api/v1"

async def test_ctl_consistency():
    """Test that CTL values are consistent across different time ranges."""
    
    # Login first
    async with httpx.AsyncClient() as client:
        print("🔐 Logging in...")
        login_response = await client.post(
            f"{BASE_URL}/auth/login",
            data={  # Use form data, not JSON
                "username": "tboettger@gmail.com",
                "password": "test123"
            }
        )
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            print(login_response.text)
            return
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        print("✅ Login successful\n")
        
        # Test 1: Get current metrics (uses 50 days)
        print("📊 Test 1: Current Metrics (/training-metrics)")
        print("=" * 60)
        metrics_response = await client.get(
            f"{BASE_URL}/garmin/training-metrics",
            headers=headers
        )
        
        if metrics_response.status_code != 200:
            print(f"❌ Failed: {metrics_response.status_code}")
            print(metrics_response.text)
            return
        
        current_metrics = metrics_response.json()
        current_ctl = current_metrics.get('ctl', 0)
        print(f"   CTL from /training-metrics: {current_ctl}")
        print(f"   ATL: {current_metrics.get('atl', 0)}")
        print(f"   TSB: {current_metrics.get('tsb', 0)}")
        print()
        
        # Test 2: Get 90 days performance data
        print("📊 Test 2: Performance Data - 90 Days")
        print("=" * 60)
        perf_90_response = await client.get(
            f"{BASE_URL}/garmin/training-load?days=90",
            headers=headers
        )
        
        if perf_90_response.status_code != 200:
            print(f"❌ Failed: {perf_90_response.status_code}")
            return
        
        perf_90_data = perf_90_response.json()
        ctl_90 = perf_90_data[-1].get('ctl', 0) if perf_90_data else None
        if perf_90_data:
            print(f"   Latest CTL (90 days): {ctl_90}")
            print(f"   Date: {perf_90_data[-1].get('date')}")
            print()
        else:
            print("   ⚠️  No data returned")
            print()
        
        # Test 3: Get 180 days performance data
        print("📊 Test 3: Performance Data - 180 Days")
        print("=" * 60)
        perf_180_response = await client.get(
            f"{BASE_URL}/garmin/training-load?days=180",
            headers=headers
        )
        
        if perf_180_response.status_code != 200:
            print(f"❌ Failed: {perf_180_response.status_code}")
            return
        
        perf_180_data = perf_180_response.json()
        ctl_180 = perf_180_data[-1].get('ctl', 0) if perf_180_data else None
        if perf_180_data:
            print(f"   Latest CTL (180 days): {ctl_180}")
            print(f"   Date: {perf_180_data[-1].get('date')}")
            print()
        else:
            print("   ⚠️  No data returned")
            print()
        
        # Test 4: Get 365 days performance data
        print("📊 Test 4: Performance Data - 365 Days")
        print("=" * 60)
        perf_365_response = await client.get(
            f"{BASE_URL}/garmin/training-load?days=365",
            headers=headers
        )
        
        if perf_365_response.status_code != 200:
            print(f"❌ Failed: {perf_365_response.status_code}")
            return
        
        perf_365_data = perf_365_response.json()
        ctl_365 = perf_365_data[-1].get('ctl', 0) if perf_365_data else None
        if perf_365_data:
            print(f"   Latest CTL (365 days): {ctl_365}")
            print(f"   Date: {perf_365_data[-1].get('date')}")
            print()
        else:
            print("   ⚠️  No data returned")
            print()
        
        # Test 5: Sport-specific (Running) - 90 days
        print("📊 Test 5: Sport-Specific CTL - Running (90 Days)")
        print("=" * 60)
        running_90_response = await client.get(
            f"{BASE_URL}/garmin/training-load?days=90&sport_type=running",
            headers=headers
        )
        
        running_90_data = running_90_response.json() if running_90_response.status_code == 200 else []
        ctl_running_90 = running_90_data[-1].get('ctl', 0) if running_90_data else None
        if ctl_running_90:
            print(f"   Running CTL (90 days): {ctl_running_90}")
            print()
        else:
            print("   ⚠️  No running data")
            print()
        
        # Test 6: Sport-specific (Running) - 365 days
        print("📊 Test 6: Sport-Specific CTL - Running (365 Days)")
        print("=" * 60)
        running_365_response = await client.get(
            f"{BASE_URL}/garmin/training-load?days=365&sport_type=running",
            headers=headers
        )
        
        running_365_data = running_365_response.json() if running_365_response.status_code == 200 else []
        ctl_running_365 = running_365_data[-1].get('ctl', 0) if running_365_data else None
        if ctl_running_365:
            print(f"   Running CTL (365 days): {ctl_running_365}")
            print()
        else:
            print("   ⚠️  No running data")
            print()
        
        # Test 7: Sport-specific (Cycling) - 90 days
        print("📊 Test 7: Sport-Specific CTL - Cycling (90 Days)")
        print("=" * 60)
        cycling_90_response = await client.get(
            f"{BASE_URL}/garmin/training-load?days=90&sport_type=cycling",
            headers=headers
        )
        
        cycling_90_data = cycling_90_response.json() if cycling_90_response.status_code == 200 else []
        ctl_cycling_90 = cycling_90_data[-1].get('ctl', 0) if cycling_90_data else None
        if ctl_cycling_90:
            print(f"   Cycling CTL (90 days): {ctl_cycling_90}")
            print()
        else:
            print("   ⚠️  No cycling data")
            print()
        
        # Test 8: Sport-specific (Cycling) - 365 days
        print("📊 Test 8: Sport-Specific CTL - Cycling (365 Days)")
        print("=" * 60)
        cycling_365_response = await client.get(
            f"{BASE_URL}/garmin/training-load?days=365&sport_type=cycling",
            headers=headers
        )
        
        cycling_365_data = cycling_365_response.json() if cycling_365_response.status_code == 200 else []
        ctl_cycling_365 = cycling_365_data[-1].get('ctl', 0) if cycling_365_data else None
        if ctl_cycling_365:
            print(f"   Cycling CTL (365 days): {ctl_cycling_365}")
            print()
        else:
            print("   ⚠️  No cycling data")
            print()
        
        # Verification
        print("🔍 VERIFICATION - ALL SPORTS")
        print("=" * 60)
        
        # Group CTL values by category
        overall_ctls = [
            ("Training Metrics", current_ctl),
            ("90 Days", ctl_90),
            ("180 Days", ctl_180),
            ("365 Days", ctl_365)
        ]
        
        running_ctls = [
            ("Running 90 Days", ctl_running_90),
            ("Running 365 Days", ctl_running_365)
        ]
        
        cycling_ctls = [
            ("Cycling 90 Days", ctl_cycling_90),
            ("Cycling 365 Days", ctl_cycling_365)
        ]
        
        # Filter out None values
        valid_overall = [(name, ctl) for name, ctl in overall_ctls if ctl is not None]
        valid_running = [(name, ctl) for name, ctl in running_ctls if ctl is not None]
        valid_cycling = [(name, ctl) for name, ctl in cycling_ctls if ctl is not None]
        
        # Check overall CTL consistency
        print("1️⃣  OVERALL CTL (All Sports Combined)")
        print("-" * 60)
        if len(valid_overall) >= 2:
            unique_overall = set(ctl for _, ctl in valid_overall)
            print(f"   Unique values: {unique_overall}")
            for name, ctl in valid_overall:
                print(f"   {name:25s}: {ctl}")
            
            if len(unique_overall) == 1:
                print("   ✅ Overall CTL is consistent!")
            else:
                print("   ❌ Overall CTL differs across time ranges!")
        else:
            print("   ⚠️  Not enough data")
        print()
        
        # Check running CTL consistency
        print("2️⃣  RUNNING-ONLY CTL")
        print("-" * 60)
        if len(valid_running) >= 2:
            unique_running = set(ctl for _, ctl in valid_running)
            print(f"   Unique values: {unique_running}")
            for name, ctl in valid_running:
                print(f"   {name:25s}: {ctl}")
            
            if len(unique_running) == 1:
                print("   ✅ Running CTL is consistent!")
            else:
                print("   ❌ Running CTL differs across time ranges!")
        else:
            print("   ⚠️  Not enough running data")
        print()
        
        # Check cycling CTL consistency
        print("3️⃣  CYCLING-ONLY CTL")
        print("-" * 60)
        if len(valid_cycling) >= 2:
            unique_cycling = set(ctl for _, ctl in valid_cycling)
            print(f"   Unique values: {unique_cycling}")
            for name, ctl in valid_cycling:
                print(f"   {name:25s}: {ctl}")
            
            if len(unique_cycling) == 1:
                print("   ✅ Cycling CTL is consistent!")
            else:
                print("   ❌ Cycling CTL differs across time ranges!")
        else:
            print("   ⚠️  Not enough cycling data")
        print()
        
        # Final verdict
        print("=" * 60)
        all_consistent = True
        
        if len(valid_overall) >= 2:
            unique_overall = set(ctl for _, ctl in valid_overall)
            if len(unique_overall) > 1:
                all_consistent = False
        
        if len(valid_running) >= 2:
            unique_running = set(ctl for _, ctl in valid_running)
            if len(unique_running) > 1:
                all_consistent = False
        
        if len(valid_cycling) >= 2:
            unique_cycling = set(ctl for _, ctl in valid_cycling)
            if len(unique_cycling) > 1:
                all_consistent = False
        
        if all_consistent:
            print("✅ SUCCESS: All CTL calculations are consistent!")
            print("   The fix is working correctly for all sports.")
            return 0
        else:
            print("❌ FAILURE: Some CTL values still differ!")
            print("   There are still inconsistencies in the calculation.")
            return 1

if __name__ == "__main__":
    result = asyncio.run(test_ctl_consistency())
    sys.exit(result or 0)
