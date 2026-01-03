#!/bin/bash
# Test Garmin authentication via HTTP API

echo "=========================================="
echo "Garmin Authentication API Test"
echo "=========================================="
echo ""

# First, check if backend is running
echo "Checking if backend is running..."
if ! curl -s http://localhost:8000/ > /dev/null 2>&1; then
    echo "✗ Backend is not running on port 8000"
    echo "Please start the backend first:"
    echo "  cd backend && uvicorn src.main:app --reload --port 8000"
    exit 1
fi

echo "✓ Backend is running"
echo ""

# Test Garmin authentication
echo "Testing Garmin authentication..."
echo "Email: th.boettger@web.de"
echo ""

RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/garmin/connect \
  -H "Content-Type: application/json" \
  -d '{
    "email": "th.boettger@web.de",
    "password": "2025Dpige.2025"
  }')

echo "Response:"
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
echo ""

# Check if authentication was successful
if echo "$RESPONSE" | grep -q '"success".*true'; then
    echo "✓ Authentication successful!"
elif echo "$RESPONSE" | grep -q '"detail"'; then
    echo "✗ Authentication failed"
    echo ""
    echo "Error details:"
    echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('detail', 'Unknown error'))" 2>/dev/null
else
    echo "✗ Unexpected response format"
fi

echo ""
echo "=========================================="
