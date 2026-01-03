#!/bin/bash
# Quick script to launch OBS and open recordings folder

echo "🎬 Starting OBS Studio for coding session..."

# Create recordings directory if it doesn't exist
mkdir -p ~/Movies/OBS_Recordings

# Open OBS
open -a OBS

# Wait a moment
sleep 2

echo "✅ OBS is ready!"
echo ""
echo "📹 Hotkeys:"
echo "   ⌘ + Shift + R - Start Recording"
echo "   ⌘ + Shift + S - Stop Recording"
echo "   ⌘ + Shift + P - Pause Recording"
echo ""
echo "📁 Recordings will be saved to: ~/Movies/OBS_Recordings"
echo ""
echo "💡 Tips:"
echo "   - Increase VS Code font size (View → Appearance → Zoom In)"
echo "   - Use a high-contrast theme"
echo "   - Hide distractions (dock, notifications)"
echo ""
