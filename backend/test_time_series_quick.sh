#!/bin/bash
# Quick test of time series API endpoint

echo "🧪 Testing time series data import..."
echo ""

# Get recent activity ID
ACTIVITY_ID=$(sqlite3 trainingplan.db "SELECT id FROM garmin_activities WHERE activity_type = 'running' ORDER BY start_time_local DESC LIMIT 1;")

echo "📊 Testing activity ID: $ACTIVITY_ID"
echo ""

# Test the endpoint (requires backend running)
curl -s "http://localhost:8000/api/v1/garmin/activities/${ACTIVITY_ID}/time-series" \
  -H "Authorization: Bearer YOUR_TOKEN" | jq -r '.metadata'

echo ""
echo "✅ Done! Check if time series data is returned."
