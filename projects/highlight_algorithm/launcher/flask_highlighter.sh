#!/bin/bash
# Thai Grapheme Highlighter - Unix/Mac Launcher
# Activates virtual environment and starts Flask server

echo "==============================================="
echo "Thai Grapheme Highlighting Tool"
echo "==============================================="
echo ""

# Change to this project's directory
cd "$(dirname "$0")/.." || exit

# Activate virtual environment (at repository root)
if [ -f "../../../.venv/bin/activate" ]; then
    echo "Activating virtual environment..."
    source ../../../.venv/bin/activate
else
    echo "WARNING: Virtual environment not found at repository root"
    echo "Attempting to run with system Python..."
    echo ""
fi

# Start Flask server with restart loop
echo "Starting Flask server..."
echo ""

while true; do
    python3 src/server.py
    exit_code=$?

    if [ $exit_code -eq 0 ]; then
        echo ""
        echo "Server shut down normally."
        break
    else
        echo ""
        echo "Server restarting... (exit code: $exit_code)"
        echo ""
        sleep 1
    fi
done

echo ""
echo "Press any key to exit..."
read -n 1