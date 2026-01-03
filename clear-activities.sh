#!/bin/bash
# Clear all Garmin activities from database
# User must manually reimport via app UI

echo "🗑️  Clear All Garmin Activities"
echo "========================================"
echo ""

cd "$(dirname "$0")/backend"

# Check if venv exists
if [ ! -d "venv313" ]; then
    echo "❌ Virtual environment not found!"
    exit 1
fi

source venv313/bin/activate

echo "Clearing activities from database..."
python scripts/clear_activities.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Database cleared!"
    echo ""
    echo "📥 Next step: Reimport manually through app"
    echo "   1. Open http://localhost:5173"
    echo "   2. Go to Settings > Garmin Connect"
    echo "   3. Click 'Sync Activities'"
fi
