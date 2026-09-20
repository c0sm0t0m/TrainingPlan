#!/bin/bash

# Test Events API
# This script tests the complete Events feature implementation

echo "🧪 Testing Events API"
echo "===================="

# Get auth token (assumes user exists and is logged in)
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=test123" | jq -r .access_token)

if [ "$TOKEN" = "null" ]; then
  echo "❌ Failed to get auth token. Please register a user first."
  exit 1
fi

echo "✅ Got auth token"
echo ""

# Test 1: Create a new event
echo "📝 Test 1: Creating a new event..."
EVENT_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/events" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Berlin Marathon 2026",
    "event_date": "2026-09-27",
    "event_type": "race",
    "location": "Berlin, Germany",
    "description": "The famous Berlin Marathon",
    "goal_time": "3:30:00",
    "target_distance": "Marathon (42.2km)",
    "cost": "€150",
    "registration_link": "https://www.bmw-berlin-marathon.com"
  }')

EVENT_ID=$(echo $EVENT_RESPONSE | jq -r .id)

if [ "$EVENT_ID" = "null" ]; then
  echo "❌ Failed to create event"
  echo "$EVENT_RESPONSE" | jq .
  exit 1
fi

echo "✅ Event created with ID: $EVENT_ID"
echo ""

# Test 2: Get all events
echo "📋 Test 2: Getting all events..."
EVENTS=$(curl -s -X GET "http://localhost:8000/api/v1/events" \
  -H "Authorization: Bearer $TOKEN")

EVENT_COUNT=$(echo $EVENTS | jq '. | length')
echo "✅ Found $EVENT_COUNT event(s)"
echo ""

# Test 3: Get specific event
echo "🔍 Test 3: Getting event details..."
EVENT_DETAIL=$(curl -s -X GET "http://localhost:8000/api/v1/events/$EVENT_ID" \
  -H "Authorization: Bearer $TOKEN")

EVENT_NAME=$(echo $EVENT_DETAIL | jq -r .name)
echo "✅ Retrieved event: $EVENT_NAME"
echo ""

# Test 4: Update event
echo "✏️  Test 4: Updating event..."
UPDATE_RESPONSE=$(curl -s -X PUT "http://localhost:8000/api/v1/events/$EVENT_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "notes": "Training started! 16 weeks to go.",
    "is_completed": false
  }')

UPDATED_NOTES=$(echo $UPDATE_RESPONSE | jq -r .notes)
echo "✅ Event updated. Notes: $UPDATED_NOTES"
echo ""

# Test 5: Mark as completed
echo "🏁 Test 5: Marking event as completed..."
COMPLETE_RESPONSE=$(curl -s -X PUT "http://localhost:8000/api/v1/events/$EVENT_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "is_completed": true,
    "actual_time": "3:25:42",
    "actual_result": "Beat goal time by 4 minutes!"
  }')

IS_COMPLETED=$(echo $COMPLETE_RESPONSE | jq -r .is_completed)
ACTUAL_TIME=$(echo $COMPLETE_RESPONSE | jq -r .actual_time)
echo "✅ Event completed: $IS_COMPLETED, Time: $ACTUAL_TIME"
echo ""

# Test 6: Create another event
echo "📝 Test 6: Creating another event..."
EVENT2_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/events" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Local 5K Run",
    "event_date": "2026-02-15",
    "event_type": "race",
    "location": "City Park",
    "target_distance": "5K"
  }')

EVENT2_ID=$(echo $EVENT2_RESPONSE | jq -r .id)
echo "✅ Second event created with ID: $EVENT2_ID"
echo ""

# Test 7: Delete event
echo "🗑️  Test 7: Deleting second event..."
DELETE_RESPONSE=$(curl -s -w "\n%{http_code}" -X DELETE "http://localhost:8000/api/v1/events/$EVENT2_ID" \
  -H "Authorization: Bearer $TOKEN")

HTTP_CODE=$(echo "$DELETE_RESPONSE" | tail -n1)
if [ "$HTTP_CODE" = "204" ]; then
  echo "✅ Event deleted successfully"
else
  echo "❌ Failed to delete event (HTTP $HTTP_CODE)"
fi
echo ""

# Final check: List all events
echo "📋 Final check: Listing all events..."
FINAL_EVENTS=$(curl -s -X GET "http://localhost:8000/api/v1/events" \
  -H "Authorization: Bearer $TOKEN")

FINAL_COUNT=$(echo $FINAL_EVENTS | jq '. | length')
echo "✅ Final event count: $FINAL_COUNT"
echo ""

echo "🎉 All tests completed!"
echo ""
echo "Event summary:"
echo $FINAL_EVENTS | jq -r '.[] | "  - \(.name) on \(.event_date) (\(if .is_completed then "Completed" else "Upcoming" end))"'
