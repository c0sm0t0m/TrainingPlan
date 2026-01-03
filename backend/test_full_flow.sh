#!/bin/bash
# Test Garmin authentication via HTTP API with proper user authentication

echo "=========================================="
echo "Garmin Authentication Full Flow Test"
echo "=========================================="
echo ""

# Check if backend is running
echo "1. Checking backend status..."
if ! curl -s http://localhost:8000/ > /dev/null 2>&1; then
    echo "✗ Backend is not running"
    exit 1
fi
echo "✓ Backend is running"
echo ""

# Step 1: Register or login a test user
echo "2. Authenticating test user..."
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=testpassword123")

# Check if login succeeded
if echo "$LOGIN_RESPONSE" | grep -q '"access_token"'; then
    echo "✓ User login successful"
    ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)
else
    echo "⚠ User doesn't exist, trying to register..."
    
    REGISTER_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/register \
      -H "Content-Type: application/json" \
      -d '{
        "email": "test@example.com",
        "full_name": "Test User",
        "password": "testpassword123"
      }')
    
    if echo "$REGISTER_RESPONSE" | grep -q '"email"'; then
        echo "✓ User registered, now logging in..."
        
        LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
          -H "Content-Type: application/x-www-form-urlencoded" \
          -d "username=test@example.com&password=testpassword123")
        
        if echo "$LOGIN_RESPONSE" | grep -q '"access_token"'; then
            echo "✓ Login successful"
            ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)
        else
            echo "✗ Failed to login after registration"
            echo "$LOGIN_RESPONSE"
            exit 1
        fi
    else
        echo "✗ Failed to register user"
        echo "$REGISTER_RESPONSE"
        exit 1
    fi
fi

echo "  Access token: ${ACCESS_TOKEN:0:20}..."
echo ""

# Step 2: Connect to Garmin
echo "3. Connecting to Garmin..."
echo "  Email: th.boettger@web.de"
echo ""

GARMIN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/garmin/connect \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d '{
    "email": "th.boettger@web.de",
    "password": "2025Dpige.2025"
  }')

echo "Response:"
echo "$GARMIN_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$GARMIN_RESPONSE"
echo ""

# Check result
if echo "$GARMIN_RESPONSE" | grep -q '"connected".*true'; then
    echo "=========================================="
    echo "✓ SUCCESS: Garmin connected!"
    echo "=========================================="
    
    # Get connection status
    echo ""
    echo "4. Verifying connection status..."
    STATUS_RESPONSE=$(curl -s http://localhost:8000/api/v1/garmin/status \
      -H "Authorization: Bearer $ACCESS_TOKEN")
    
    echo "$STATUS_RESPONSE" | python3 -m json.tool 2>/dev/null

echo ""
echo "5. Testing activity sync (connection persistence)..."
SYNC_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/garmin/sync \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d '{"days": 7}')

echo "$SYNC_RESPONSE" | python3 -m json.tool 2>/dev/null

if echo "$SYNC_RESPONSE" | grep -q '"activities_count"'; then
    echo ""
    echo "✓ Sync successful - connection is persisted!"
else
    echo ""
    echo "⚠ Sync may have failed"
fi
    echo ""
    echo "Error: $ERROR"
    echo ""
    
    # Provide helpful hints
    if [[ "$ERROR" == *"SSL"* ]] || [[ "$ERROR" == *"certificate"* ]]; then
        echo "⚠ SSL Certificate Issue"
        echo "  The SSL configuration should have 3 fallback tiers."
        echo "  Check backend logs for details."
    elif [[ "$ERROR" == *"authentication"* ]] || [[ "$ERROR" == *"credentials"* ]]; then
        echo "⚠ Credential Issue"
        echo "  - Verify email and password are correct"
        echo "  - Check if MFA/2FA is enabled on Garmin account"
        echo "  - Try logging in at connect.garmin.com"
    fi
else
    echo "=========================================="
    echo "✗ FAILED: Unexpected response"
    echo "=========================================="
fi

echo ""
