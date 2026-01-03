#!/bin/bash
# Test Garmin Activity Sync

echo "🧪 Testing Garmin Activity Sync"
echo "================================"
echo ""

# Check if backend is running
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "❌ Backend is not running!"
    echo "   Start it with: ./start-backend.sh"
    exit 1
fi

echo "✅ Backend is running"
echo ""

# Get auth token (you'll need to provide credentials)
read -p "Enter your email: " EMAIL
read -sp "Enter your password: " PASSWORD
echo ""
echo ""

echo "🔐 Logging in..."
TOKEN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=$EMAIL&password=$PASSWORD")

TOKEN=$(echo $TOKEN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

if [ -z "$TOKEN" ]; then
    echo "❌ Login failed!"
    echo "$TOKEN_RESPONSE" | python3 -m json.tool 2>&1 | head -20
    exit 1
fi

echo "✅ Logged in successfully"
echo ""

# Check Garmin connection status
echo "🔍 Checking Garmin connection..."
GARMIN_STATUS=$(curl -s http://localhost:8000/api/v1/garmin/status \
  -H "Authorization: Bearer $TOKEN")

echo "$GARMIN_STATUS" | python3 -m json.tool

CONNECTED=$(echo "$GARMIN_STATUS" | python3 -c "import sys, json; print(json.load(sys.stdin)['connected'])" 2>/dev/null)

if [ "$CONNECTED" != "True" ]; then
    echo ""
    echo "❌ Garmin not connected!"
    echo "   Connect via: Settings > Garmin Connect"
    exit 1
fi

echo ""
echo "✅ Garmin is connected"
echo ""

# Sync activities
echo "📥 Syncing Garmin activities (last 30 days)..."
SYNC_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/garmin/sync-activities \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"days": 30}')

echo "$SYNC_RESPONSE" | python3 -m json.tool

echo ""
echo "✅ Sync complete!"
