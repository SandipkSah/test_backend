#!/bin/bash

# Ensure the script exits on errors
set -e

# Function to handle errors
error_handler() {
    echo "Error occurred in script at line $1. Exiting." 
    exit 1
}

# Trap errors and call the error handler
trap 'error_handler $LINENO' ERR

# Install the required Python packages
pip install -r requirements.txt

# Run the application using Hypercorn with 2 workers
hypercorn app:app --bind 0.0.0.0 --workers 2