#!/bin/bash

# Basic Agent runner script

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the script directory
cd "$SCRIPT_DIR"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not found."
    exit 1
fi

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "Error: Ollama is required but not found."
    echo "Please install Ollama: https://github.com/ollama/ollama"
    exit 1
fi

# Check if Ollama is running
if ! ollama list &> /dev/null; then
    echo "Error: Ollama is not running."
    echo "Please start Ollama before running Basic Agent."
    exit 1
fi

# Parse arguments
MODEL=""
DEBUG=""
SAVE_HISTORY=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --model)
      MODEL="--model $2"
      shift 2
      ;;
    --debug|-d)
      DEBUG="--debug"
      shift
      ;;
    --save-history|-s)
      SAVE_HISTORY="--save-history"
      shift
      ;;
    *)
      # Any unknown arguments are passed directly to the Python script
      break
      ;;
  esac
done

# Run the agent
python3 run.py $MODEL $DEBUG $SAVE_HISTORY "$@" 