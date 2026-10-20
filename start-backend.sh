#!/bin/bash
# Start TrainingPlan Backend

echo "🚀 Starting TrainingPlan Backend..."
echo "=================================="

cd "$(dirname "$0")/backend"

# Check if virtual environment exists and is valid
if [ ! -d "venv313" ]; then
    echo "❌ Virtual environment not found. Creating one..."
    python3.13 -m venv venv313
    source venv313/bin/activate
    pip install -r requirements.txt
elif [ ! -f "venv313/bin/python3" ] || ! venv313/bin/python3 --version &>/dev/null; then
    echo "⚠️  Virtual environment is broken (possibly from moving the project)."
    echo "   Recreating virtual environment..."
    rm -rf venv313
    python3.13 -m venv venv313
    source venv313/bin/activate
    echo "📦 Installing dependencies..."
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

# Dev and production share the NAS Postgres. A local SQLite file drifts.
if grep -q '^DATABASE_URL=sqlite' .env 2>/dev/null; then
    echo "❌ DATABASE_URL points at SQLite."
    echo "   Local dev uses the NAS Postgres (192.168.178.42). Refusing to start."
    exit 1
fi

echo ""
echo "📡 Starting FastAPI server on http://0.0.0.0:8000 (accessible via LAN)"
echo "📚 API Documentation: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Start the backend - use 0.0.0.0 to allow LAN access
# Use full path to uvicorn from venv to ensure it's found
venv313/bin/uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
