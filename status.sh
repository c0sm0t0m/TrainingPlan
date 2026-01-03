#!/bin/bash
# Check status of TrainingPlan services

echo "🔍 TrainingPlan Service Status"
echo "=============================="
echo ""

# Check backend
if pgrep -f "uvicorn src.main:app" > /dev/null; then
    echo "✅ Backend:  Running on http://localhost:8000"
    echo "   API Docs: http://localhost:8000/docs"
else
    echo "❌ Backend:  Not running"
fi

# Check frontend
if pgrep -f "vite" > /dev/null; then
    echo "✅ Frontend: Running on http://localhost:5173"
else
    echo "❌ Frontend: Not running"
fi

echo ""

# Check if services are accessible
echo "Testing connectivity..."
if curl -s http://localhost:8000/health > /dev/null 2>&1 || curl -s http://localhost:8000 > /dev/null 2>&1; then
    echo "✅ Backend is accessible"
else
    echo "⚠️  Backend is not accessible (may still be starting)"
fi

if curl -s http://localhost:5173 > /dev/null 2>&1; then
    echo "✅ Frontend is accessible"
else
    echo "⚠️  Frontend is not accessible (may still be starting)"
fi

echo ""
echo "💡 To start services: ./start-all.sh"
echo "💡 To stop services:  ./stop-all.sh"
