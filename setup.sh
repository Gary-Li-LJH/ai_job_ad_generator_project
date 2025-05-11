#!/bin/bash

# --- Setup Script for AI Job Ad Generator (Linux/macOS) ---

# Define the name for your virtual environment
VENV_NAME="venv_job_ad_generator" # Or just "venv" if you prefer

# Define the Python command (try python3, then python if python3 is not found)
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null
then
    PYTHON_CMD="python"
    if ! command -v python &> /dev/null
    then
        echo "ERROR: Python is not installed or not in PATH. Please install Python 3."
        exit 1
    fi
fi

echo "Using Python command: $PYTHON_CMD"
$PYTHON_CMD --version

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    echo "ERROR: requirements.txt not found in the current directory!"
    echo "Please ensure you are in the project root directory and requirements.txt exists."
    exit 1
fi

# Create the virtual environment if it doesn't exist
if [ ! -d "$VENV_NAME" ]; then
    echo "Creating virtual environment: $VENV_NAME..."
    $PYTHON_CMD -m venv $VENV_NAME
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create virtual environment."
        exit 1
    fi
    echo "Virtual environment created successfully."
else
    echo "Virtual environment '$VENV_NAME' already exists."
fi

# Activate the virtual environment
echo "Activating virtual environment..."
source "$VENV_NAME/bin/activate"
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to activate virtual environment."
    echo "Try running 'source $VENV_NAME/bin/activate' manually."
    exit 1
fi
echo "Virtual environment activated. (You should see '($VENV_NAME)' in your prompt)"

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to upgrade pip."
    # Don't exit, try to install requirements anyway
fi

# Install dependencies
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies. Check requirements.txt and your internet connection."
    echo "You might need to install system-level build dependencies for some packages (e.g., for lxml used by python-docx)."
    exit 1
fi

echo ""
echo "--- Setup Complete! ---"
echo "The virtual environment '$VENV_NAME' is set up and dependencies are installed."
echo "To run the application, use the 'run.sh' script or activate the venv manually:"
echo "  source $VENV_NAME/bin/activate"
echo "  streamlit run app.py"
echo ""
echo "IMPORTANT: Ensure your Google Cloud service account key is correctly placed in the 'keys/' directory"
echo "and the filename is updated in 'modules/app_config.py' (SERVICE_ACCOUNT_KEY_FILENAME)."