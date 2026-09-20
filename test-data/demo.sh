#!/bin/bash

# Test Data Demo Script
# Demonstrates all available test data tools

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

echo "======================================================================"
echo "         Kinesis - AI Training Plan Test Data Demo"
echo "======================================================================"
echo ""

# Function to show menu
show_menu() {
    echo "What would you like to do?"
    echo ""
    echo "  1) View test configuration (JSON)"
    echo "  2) Run Python test helper (API testing)"
    echo "  3) Open visual editor (HTML)"
    echo "  4) Copy auto-fill script to clipboard"
    echo "  5) Show all files in test-data folder"
    echo "  6) View documentation (README)"
    echo "  7) View quick reference (QUICK_START)"
    echo "  8) Exit"
    echo ""
    read -p "Enter your choice [1-8]: " choice
}

# Function to view JSON config
view_json() {
    echo ""
    echo "======================================================================"
    echo "Test Configuration (JSON)"
    echo "======================================================================"
    echo ""
    cat "$SCRIPT_DIR/ai-training-plan-config.json"
    echo ""
    echo "----------------------------------------------------------------------"
    echo "File location: $SCRIPT_DIR/ai-training-plan-config.json"
    echo "======================================================================"
    echo ""
}

# Function to run Python helper
run_python_helper() {
    echo ""
    echo "======================================================================"
    echo "Running Python Test Helper..."
    echo "======================================================================"
    echo ""
    
    if command -v python3 &> /dev/null; then
        cd "$PROJECT_ROOT"
        python3 "$SCRIPT_DIR/test_ai_plan_config.py"
    else
        echo "❌ Error: python3 not found"
        echo "Please install Python 3 to use this feature"
    fi
    
    echo ""
}

# Function to open HTML editor
open_html_editor() {
    echo ""
    echo "======================================================================"
    echo "Opening Visual Editor..."
    echo "======================================================================"
    echo ""
    echo "The test data editor will open in your default browser."
    echo ""
    
    open "$SCRIPT_DIR/test-data-editor.html" 2>/dev/null || \
    xdg-open "$SCRIPT_DIR/test-data-editor.html" 2>/dev/null || \
    echo "❌ Could not open browser. Please open manually: $SCRIPT_DIR/test-data-editor.html"
    
    echo "✅ Opened: $SCRIPT_DIR/test-data-editor.html"
    echo ""
}

# Function to copy auto-fill script
copy_autofill() {
    echo ""
    echo "======================================================================"
    echo "Auto-Fill Script"
    echo "======================================================================"
    echo ""
    echo "To use this script:"
    echo "1. Open http://localhost:5173/ai-training-plan"
    echo "2. Press F12 to open DevTools"
    echo "3. Copy the contents of auto-fill-training-plan.js"
    echo "4. Paste into the Console tab"
    echo "5. Press Enter"
    echo ""
    echo "Attempting to copy to clipboard..."
    
    if command -v pbcopy &> /dev/null; then
        cat "$SCRIPT_DIR/auto-fill-training-plan.js" | pbcopy
        echo "✅ Copied to clipboard (macOS)"
    elif command -v xclip &> /dev/null; then
        cat "$SCRIPT_DIR/auto-fill-training-plan.js" | xclip -selection clipboard
        echo "✅ Copied to clipboard (Linux)"
    else
        echo "❌ Clipboard tool not found. Please copy manually:"
        echo "   File: $SCRIPT_DIR/auto-fill-training-plan.js"
    fi
    
    echo ""
    read -p "Press Enter to view the script content..."
    echo ""
    cat "$SCRIPT_DIR/auto-fill-training-plan.js"
    echo ""
}

# Function to list all files
list_files() {
    echo ""
    echo "======================================================================"
    echo "Test Data Folder Contents"
    echo "======================================================================"
    echo ""
    ls -lah "$SCRIPT_DIR"
    echo ""
    echo "----------------------------------------------------------------------"
    echo "Folder: $SCRIPT_DIR"
    echo "======================================================================"
    echo ""
}

# Function to view README
view_readme() {
    echo ""
    echo "======================================================================"
    echo "README.md"
    echo "======================================================================"
    echo ""
    
    if command -v bat &> /dev/null; then
        bat "$SCRIPT_DIR/README.md"
    elif command -v less &> /dev/null; then
        less "$SCRIPT_DIR/README.md"
    else
        cat "$SCRIPT_DIR/README.md"
    fi
    
    echo ""
}

# Function to view quick start
view_quickstart() {
    echo ""
    echo "======================================================================"
    echo "QUICK_START.md"
    echo "======================================================================"
    echo ""
    
    if command -v bat &> /dev/null; then
        bat "$SCRIPT_DIR/QUICK_START.md"
    elif command -v less &> /dev/null; then
        less "$SCRIPT_DIR/QUICK_START.md"
    else
        cat "$SCRIPT_DIR/QUICK_START.md"
    fi
    
    echo ""
}

# Main loop
while true; do
    show_menu
    
    case $choice in
        1)
            view_json
            read -p "Press Enter to continue..."
            ;;
        2)
            run_python_helper
            read -p "Press Enter to continue..."
            ;;
        3)
            open_html_editor
            read -p "Press Enter to continue..."
            ;;
        4)
            copy_autofill
            read -p "Press Enter to continue..."
            ;;
        5)
            list_files
            read -p "Press Enter to continue..."
            ;;
        6)
            view_readme
            read -p "Press Enter to continue..."
            ;;
        7)
            view_quickstart
            read -p "Press Enter to continue..."
            ;;
        8)
            echo ""
            echo "✨ Thank you for using Kinesis test data tools!"
            echo ""
            exit 0
            ;;
        *)
            echo ""
            echo "❌ Invalid choice. Please select 1-8."
            echo ""
            read -p "Press Enter to continue..."
            ;;
    esac
    
    clear
done
