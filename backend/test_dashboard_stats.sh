#!/bin/bash

echo "=========================================="
echo "Testing Dashboard Activity Stats"
echo "=========================================="

# Backend URL
BACKEND_URL="http://localhost:8000"

# Test credentials - use the test user from test_full_flow.sh
EMAIL="test@example.com"
PASSWORD="testpassword123"

echo -e "\n1. Logging in..."
LOGIN_RESPONSE=$(curl -s -X POST "$BACKEND_URL/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=$EMAIL&password=$PASSWORD")

# Extract token
TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

if [ -z "$TOKEN" ]; then
    echo "✗ Login failed"
    echo "$LOGIN_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$LOGIN_RESPONSE"
    exit 1
fi

echo "✓ Login successful"

echo -e "\n2. Fetching activity stats..."
STATS_RESPONSE=$(curl -s -X GET "$BACKEND_URL/api/v1/garmin/activities/stats" \
  -H "Authorization: Bearer $TOKEN")

echo "$STATS_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$STATS_RESPONSE"

echo -e "\n3. Fetching stored activities (limit 5)..."
ACTIVITIES_RESPONSE=$(curl -s -X GET "$BACKEND_URL/api/v1/garmin/activities/stored?limit=5" \
  -H "Authorization: Bearer $TOKEN")

echo "$ACTIVITIES_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$ACTIVITIES_RESPONSE"

echo -e "\n=========================================="
echo "✓ Test complete!"
echo "=========================================="
