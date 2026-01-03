#!/bin/bash
# Start TrainingPlan Backend

echo "🚀 Starting TrainingPlan Backend..."
echo "=================================="

cd "$(dirname "$0")/backend"

# Check if virtual environment exists
if [ ! -d "venv313" ]; then
    echo "❌ Virtual environment not found. Creating one..."
    python3 -m venv venv313
    source venv313/bin/activate
    pip install -r requirements.txt
else
    echo "✅ Activating virtual environment..."
    source venv313/bin/activate
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "   Copy .env.example to .env and configure it"
fi

echo ""
echo "📡 Starting FastAPI server on http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Start the backend
uvicorn src.main:app --reload --port 8000
