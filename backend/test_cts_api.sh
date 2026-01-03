#!/bin/bash
# Test CTS API endpoint

# Get auth token
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test1234!"}' | \
  grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
  echo "❌ Login failed or test user doesn't exist"
  exit 1
fi

echo "✅ Got auth token"
echo ""
echo "Testing CTS method via API..."
echo ""

# Test CTS zones with threshold pace 270 seconds (4:30/km)
curl -s "http://localhost:8000/api/v1/auth/zones/pace_running?method=cts&threshold=270" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

echo ""
echo "✅ API test complete"
