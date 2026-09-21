#!/bin/bash
# Start TrainingPlan Frontend

echo "🚀 Starting TrainingPlan Frontend..."
echo "==================================="

# Load nvm when present (script often runs outside a login bash shell)
export NVM_DIR="${NVM_DIR:-$HOME/.nvm}"
if [ -s "$NVM_DIR/nvm.sh" ]; then
    # shellcheck source=/dev/null
    . "$NVM_DIR/nvm.sh"
fi

if ! command -v npm >/dev/null 2>&1; then
    echo "❌ npm not found."
    echo "   Node is expected via nvm at ~/.nvm (found Node there earlier),"
    echo "   or install with: brew install node"
    exit 1
fi

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
