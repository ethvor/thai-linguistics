#!/bin/bash

echo "===================================="
echo "Thai Syllable Labeling System"
echo "===================================="
echo
echo "Starting Flask server..."
echo "Server will find an available port between 5001-5010"
echo

cd "$(dirname "$0")/.."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 is not installed or not in PATH"
    echo "Please install Python3 or make sure it's in your PATH"
    echo
    read -p "Press any key to exit..."
    exit 1
fi

# Check if the main Python file exists
if [ ! -f "thai_labeling_app.py" ]; then
    echo "ERROR: thai_labeling_app.py not found!"
    echo "Expected location: $(pwd)/"
    echo "Please make sure the file exists in the project root."
    echo
    read -p "Press any key to exit..."
    exit 1
fi

# Run the Flask server with restart capability
while true; do
    export LAUNCHER_TYPE=shell
    python3 thai_labeling_app.py
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