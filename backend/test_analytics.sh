#!/bin/bash
# Test analytics endpoint

echo "Testing Analytics Endpoint"
echo "=========================="
echo ""

# Get token
echo "1. Login..."
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=tboettger@gmail.com&password=Test123!" \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

if [ -z "$TOKEN" ]; then
  echo "❌ Login failed"
  exit 1
fi

echo "✅ Login successful"
echo ""

# Test analytics endpoint
echo "2. Testing /api/v1/analytics/key-sessions..."
curl -s "http://localhost:8000/api/v1/analytics/key-sessions?sport=running&limit=3&days_back=90" \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -m json.tool | head -80

echo ""
echo "✅ Test complete!"
