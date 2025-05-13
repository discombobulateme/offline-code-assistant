#!/bin/bash

# Script to analyze any local repository or folder in the parent directory using Basic Agent

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PARENT_DIR="$( dirname "$SCRIPT_DIR" )"

# Check if a repository name was provided
if [ $# -eq 0 ]; then
    echo "Please provide a local folder/repository name to analyze."
    echo "Available local folders/repositories:"
    
    # List all directories in the parent folder
    for dir in "$PARENT_DIR"/*; do
        if [ -d "$dir" ]; then
            echo "  - $(basename "$dir")"
        fi
    done
    
    exit 1
fi

REPO_NAME="$1"
REPO_PATH="$PARENT_DIR/$REPO_NAME"

# Check if the repository exists
if [ ! -d "$REPO_PATH" ]; then
    echo "Local folder/repository '$REPO_NAME' not found in $PARENT_DIR"
    echo "Available local folders/repositories:"
    
    for dir in "$PARENT_DIR"/*; do
        if [ -d "$dir" ]; then
            echo "  - $(basename "$dir")"
        fi
    done
    
    exit 1
fi

# Change to the script directory
cd "$SCRIPT_DIR"

# Get optional model parameter
MODEL_PARAM=""
if [ $# -ge 2 ]; then
    MODEL_PARAM="--model $2"
fi

echo "Analyzing local folder/repository: $REPO_NAME"
echo "Path: $REPO_PATH"
echo ""

# Run the agent with the repository path
python3 run.py $MODEL_PARAM --project-path "$REPO_PATH" --analyze 