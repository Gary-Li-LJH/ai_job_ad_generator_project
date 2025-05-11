#!/bin/bash

# --- Run Script for AI Job Ad Generator (Linux/macOS) ---

VENV_NAME="venv_job_ad_generator" # Must match the one in setup.sh
APP_SCRIPT="app.py" # Your main Streamlit application file

# Check if virtual environment directory exists
if [ ! -d "$VENV_NAME" ]; then
    echo "ERROR: Virtual environment '$VENV_NAME' not found."
    echo "Please run the 'setup.sh' script first to create it and install dependencies."
    exit 1
fi

# Activate the virtual environment
echo "Activating virtual environment: $VENV_NAME..."
source "$VENV_NAME/bin/activate"
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to activate virtual environment."
    exit 1
fi
echo "Virtual environment activated."

# Check if app.py exists
if [ ! -f "$APP_SCRIPT" ]; then
    echo "ERROR: Application script '$APP_SCRIPT' not found!"
    echo "Ensure you are in the project root directory."
    exit 1
fi

# Launch the Streamlit application
echo "Launching Streamlit application: $APP_SCRIPT..."
streamlit run $APP_SCRIPT

# Deactivate (optional, happens when script exits or user Ctrl+C)
# echo "Deactivating virtual environment..."
# deactivate