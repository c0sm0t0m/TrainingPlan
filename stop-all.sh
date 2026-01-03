#!/bin/bash
# Stop all TrainingPlan services

echo "🛑 Stopping TrainingPlan services..."
echo "===================================="

# Find and kill backend processes
echo "Stopping backend (uvicorn)..."
pkill -f "uvicorn src.main:app" && echo "✅ Backend stopped" || echo "ℹ️  Backend not running"

# Find and kill frontend processes
echo "Stopping frontend (vite)..."
pkill -f "vite" && echo "✅ Frontend stopped" || echo "ℹ️  Frontend not running"

echo ""
echo "✅ All services stopped"
