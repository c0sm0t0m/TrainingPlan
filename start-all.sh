#!/bin/bash
# Start both Backend and Frontend in separate terminal tabs/windows

echo "🚀 Starting TrainingPlan - Full Stack"
echo "======================================"
echo ""
echo "This will open separate terminal windows for:"
echo "  📡 Backend  (http://localhost:8000)"
echo "  🌐 Frontend (http://localhost:5173)"
echo ""

# Get the absolute path to the project directory
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Function to open new terminal based on OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS - use Terminal.app
    osascript <<EOF
        tell application "Terminal"
            -- Backend
            do script "cd '$PROJECT_DIR' && ./start-backend.sh"
            
            -- Wait a bit, then start frontend
            delay 2
            do script "cd '$PROJECT_DIR' && ./start-frontend.sh"
            
            activate
        end tell
EOF
    echo "✅ Services started in new Terminal windows"
    
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux - try common terminals
    if command -v gnome-terminal &> /dev/null; then
        gnome-terminal -- bash -c "cd '$PROJECT_DIR' && ./start-backend.sh; exec bash"
        gnome-terminal -- bash -c "cd '$PROJECT_DIR' && ./start-frontend.sh; exec bash"
    elif command -v xterm &> /dev/null; then
        xterm -e "cd '$PROJECT_DIR' && ./start-backend.sh" &
        xterm -e "cd '$PROJECT_DIR' && ./start-frontend.sh" &
    else
        echo "❌ No supported terminal found. Please run manually:"
        echo "   Terminal 1: ./start-backend.sh"
        echo "   Terminal 2: ./start-frontend.sh"
    fi
    
else
    echo "❌ Unsupported OS. Please run manually:"
    echo "   Terminal 1: ./start-backend.sh"
    echo "   Terminal 2: ./start-frontend.sh"
fi

echo ""
echo "📊 Application URLs:"
echo "   Frontend:  http://localhost:5173"
echo "   Backend:   http://localhost:8000"
echo "   API Docs:  http://localhost:8000/docs"
echo ""
echo "💡 To stop services, press Ctrl+C in each terminal window"
