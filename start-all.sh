#!/bin/bash
# Start both Backend and Frontend in separate terminal tabs/windows

echo "🚀 Starting TrainingPlan - Full Stack"
echo "======================================"
echo ""

# Get the absolute path to the project directory
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Function to kill processes on a specific port
kill_port() {
    local port=$1
    local process_name=$2
    echo "🔍 Checking for existing $process_name on port $port..."
    
    # Find and kill process using the port
    if lsof -ti:$port >/dev/null 2>&1; then
        echo "   Found existing process on port $port"
        lsof -ti:$port | xargs kill -9 2>/dev/null
        echo "   ✅ Killed process on port $port"
        sleep 1
    else
        echo "   ✓ Port $port is free"
    fi
}

# Function to kill uvicorn processes by pattern
kill_uvicorn() {
    echo "🔍 Checking for existing uvicorn (backend) processes..."
    
    # Find uvicorn processes
    local pids=$(pgrep -f "uvicorn.*src.main:app" 2>/dev/null)
    
    if [ -n "$pids" ]; then
        echo "   Found uvicorn processes: $pids"
        echo "$pids" | xargs kill -9 2>/dev/null
        echo "   ✅ Killed uvicorn processes"
        sleep 1
    else
        echo "   ✓ No uvicorn processes found"
    fi
}

# Function to kill npm/vite processes
kill_vite() {
    echo "🔍 Checking for existing Vite (frontend) processes..."
    
    # Find vite processes
    local pids=$(pgrep -f "vite.*frontend" 2>/dev/null)
    
    if [ -n "$pids" ]; then
        echo "   Found Vite processes: $pids"
        echo "$pids" | xargs kill -9 2>/dev/null
        echo "   ✅ Killed Vite processes"
        sleep 1
    else
        echo "   ✓ No Vite processes found"
    fi
}

echo "🧹 Cleaning up existing processes..."
echo ""

# Kill existing processes
kill_port 8000 "Backend"
kill_port 5173 "Frontend"
kill_uvicorn
kill_vite

echo ""
echo "🚀 Starting new services..."
echo "This will open separate terminal windows for:"
echo "  📡 Backend  (http://localhost:8000)"
echo "  🌐 Frontend (http://localhost:5173)"
echo ""

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
