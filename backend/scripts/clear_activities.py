#!/usr/bin/env python3
"""
Clear all Garmin activities from database
"""
import sqlite3
import os

def clear_activities():
    # Get database path
    db_path = os.path.join(os.path.dirname(__file__), '..', 'trainingplan.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Count activities
    cursor.execute("SELECT COUNT(*) FROM garmin_activities")
    count = cursor.fetchone()[0]
    
    if count == 0:
        print("ℹ️  No activities to delete")
        conn.close()
        return
    
    print(f"🗑️  Found {count} activities in database")
    
    # Ask for confirmation
    response = input(f"\n⚠️  This will delete ALL {count} Garmin activities. Continue? (yes/no): ")
    if response.lower() != 'yes':
        print("❌ Cancelled")
        conn.close()
        return
    
    # Delete all activities
    cursor.execute("DELETE FROM garmin_activities")
    conn.commit()
    conn.close()
    
    print(f"✅ Deleted {count} activities")
    print()
    print("📥 Now please sync activities through the app:")
    print("   1. Open http://localhost:5173")
    print("   2. Go to Settings > Garmin Connect")
    print("   3. Click 'Sync Activities'")

if __name__ == "__main__":
    print("🔄 Garmin Activities Cleanup")
    print("=" * 50)
    print()
    clear_activities()
