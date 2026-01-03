#!/bin/bash
# Run the duplicate detection test

echo "======================================================================"
echo "Calendar-Based Duplicate Detection Test"
echo "======================================================================"
echo ""
echo "This test will:"
echo "1. Retrieve workouts from database calendar for user tboettger@gmail.com"
echo "2. Check Garmin calendar to see which workouts already exist"
echo "3. Use API to sync workouts (should skip existing ones)"
echo "4. Verify all workouts are in Garmin calendar"
echo "5. Sync again to verify duplicate detection"
echo ""
echo "Prerequisites:"
echo "- Backend server must be running on http://localhost:8000"
echo "- User tboettger@gmail.com must exist and be connected to Garmin"
echo "- User must have upcoming workouts in the database (next 7 days)"
echo "  (Create workouts via the app or database before running this test)"
echo ""
echo "======================================================================"
echo ""

# Check if server is running
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "❌ Backend server is not running!"
    echo ""
    echo "Please start it in another terminal:"
    echo "  cd backend"
    echo "  source venv313/bin/activate"
    echo "  uvicorn src.main:app --reload"
    echo ""
    exit 1
fi

echo "✅ Backend server is running"
echo ""

# Run the test
./venv313/bin/python test_calendar_duplicate_check.py

echo ""
echo "======================================================================"
echo "Test Complete"
echo "======================================================================"
