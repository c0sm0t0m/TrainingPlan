#!/bin/bash
# Start TrainingPlan Frontend

echo "🚀 Starting TrainingPlan Frontend..."
echo "==================================="

cd "$(dirname "$0")/frontend"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing npm dependencies..."
    npm install
fi

echo ""
echo "🌐 Starting Vite dev server on http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Start the frontend
npm run dev
