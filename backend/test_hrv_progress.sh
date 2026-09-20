#!/bin/bash
# Quick Test - HRV Sync with Progress Tracking
# Run this to verify the enhanced HRV sync works correctly

set -e  # Exit on error

echo "======================================================================"
echo "HRV Sync Enhancement - Quick Verification"
echo "======================================================================"
echo ""
echo "This test verifies the enhanced progress tracking for HRV data sync."
echo ""

# Check if backend is running
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "⚠️  Backend is not running!"
    echo "   Please start the backend with: ./start-backend.sh"
    echo "   Or: cd backend && source venv313/bin/activate && uvicorn src.main:app --reload"
    exit 1
fi

echo "✅ Backend is running"
echo ""

# Check if user is logged in (has JWT token)
if [ -z "$JWT_TOKEN" ]; then
    echo "⚠️  No JWT token found in environment"
    echo ""
    echo "To test the enhanced HRV sync:"
    echo ""
    echo "1. Get your JWT token by logging in:"
    echo "   curl -X POST http://localhost:8000/api/v1/auth/login \\"
    echo "     -H \"Content-Type: application/json\" \\"
    echo "     -d '{\"email\":\"your@email.com\",\"password\":\"yourpassword\"}'"
    echo ""
    echo "2. Set the token:"
    echo "   export JWT_TOKEN=\"your-token-here\""
    echo ""
    echo "3. Connect Garmin account (if not already connected):"
    echo "   curl -X POST http://localhost:8000/api/v1/garmin/connect \\"
    echo "     -H \"Authorization: Bearer \$JWT_TOKEN\" \\"
    echo "     -H \"Content-Type: application/json\" \\"
    echo "     -d '{\"email\":\"garmin@email.com\",\"password\":\"garminpassword\"}'"
    echo ""
    echo "4. Run the sync (example with 180 days):"
    echo "   curl -X POST http://localhost:8000/api/v1/garmin/sync-health-data \\"
    echo "     -H \"Authorization: Bearer \$JWT_TOKEN\" \\"
    echo "     -H \"Content-Type: application/json\" \\"
    echo "     -d '{\"days\": 180}'"
    echo ""
    echo "5. Watch the backend terminal for progress updates like:"
    echo "   🔄 Starting HRV data sync for 180 days..."
    echo "   📊 Progress: 50/180 days (28%) | ✅ 42 found | ⏭️  8 no data | ❌ 0 errors"
    echo "   ⏸️  Pausing briefly to avoid rate limits..."
    echo ""
    exit 0
fi

echo "✅ JWT token found"
echo ""

# Test the endpoint
echo "Testing enhanced HRV sync with 30 days..."
echo ""

RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/garmin/sync-health-data" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"days": 30}')

echo "Response:"
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
echo ""

echo "======================================================================"
echo "✅ Test complete!"
echo ""
echo "Check the backend terminal to see the enhanced progress output:"
echo "   - Date range display"
echo "   - Progress percentages"
echo "   - Success/skip/error counters"
echo "   - Rate limiting pauses (for larger ranges)"
echo "======================================================================"
