#!/bin/bash

echo
echo "========================================="
echo "   Thai Character Pattern Classifier"
echo "        (Flask Server)"
echo "========================================="
echo

# Change to the project root directory (parent of launcher)
cd "$(dirname "$0")/.."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 is not installed or not in PATH"
    echo "Please install Python3 or make sure it's in your PATH"
    echo
    read -p "Press any key to exit..."
    exit 1
fi

# Check if the HTML file exists
if [ ! -f "thai_pattern_classifier.html" ]; then
    echo "ERROR: thai_pattern_classifier.html not found!"
    echo "Expected location: $(pwd)/"
    echo "Please make sure the file exists in the project root."
    echo
    read -p "Press any key to exit..."
    exit 1
fi

echo "Starting Flask server..."
echo

# Run the Flask server with restart capability
while true; do
    export LAUNCHER_TYPE=shell
    python3 launcher/flask_classifier.py
    exit_code=$?

    if [ $exit_code -eq 0 ]; then
        echo
        echo "Server shut down normally."
        break
    else
        echo
        echo "Server restarting... (exit code: $exit_code)"
        echo
        sleep 2
    fi
done

echo
echo "Server shut down normally."
read -p "Press any key to exit..."