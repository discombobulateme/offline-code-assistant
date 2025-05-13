#!/bin/bash

# Script to analyze specific files, lines, or errors in any local folder/repository
# using Basic Agent

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PARENT_DIR="$( dirname "$SCRIPT_DIR" )"

# Function to display usage information
show_usage() {
  echo "Usage: $0 [options]"
  echo ""
  echo "Options:"
  echo "  -r, --repo FOLDER_NAME    Local folder/repository name to analyze (required)"
  echo "  -f, --file FILE_PATH      Specific file to analyze (relative to folder root)"
  echo "  -l, --line LINE_NUMBER    Specific line number to analyze"
  echo "  -e, --error ERROR_TEXT    Error text to analyze"
  echo "  -m, --model MODEL_NAME    Model to use (default: from config)"
  echo "  -a, --analyze, --analize  Run project analysis"
  echo ""
  echo "Examples:"
  echo "  $0 --repo flysight --file src/main.c"
  echo "  $0 --repo flysight --file src/main.c --line 42"
  echo "  $0 --repo flysight --error \"segmentation fault\""
  echo "  $0 --repo flysight --analize"
  echo ""
  echo "Available local folders/repositories:"
  for dir in "$PARENT_DIR"/*; do
      if [ -d "$dir" ]; then
          echo "  - $(basename "$dir")"
      fi
  done
}

# Parse command line arguments
REPO_NAME=""
FILE_PATH=""
LINE_NUMBER=""
ERROR_TEXT=""
MODEL_NAME=""
ANALYZE_FLAG=""

while [[ $# -gt 0 ]]; do
  key="$1"

  case $key in
    -r|--repo)
      REPO_NAME="$2"
      shift
      shift
      ;;
    -f|--file)
      FILE_PATH="$2"
      shift
      shift
      ;;
    -l|--line)
      LINE_NUMBER="$2"
      shift
      shift
      ;;
    -e|--error)
      ERROR_TEXT="$2"
      shift
      shift
      ;;
    -m|--model)
      MODEL_NAME="$2"
      shift
      shift
      ;;
    -a|--analyze|--analize)
      ANALYZE_FLAG="--analyze"
      shift
      ;;
    -h|--help)
      show_usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      show_usage
      exit 1
      ;;
  esac
done

# Check if repository name was provided
if [ -z "$REPO_NAME" ]; then
    echo "Error: Local folder/repository name is required."
    show_usage
    exit 1
fi

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

# Check if file exists if specified
if [ ! -z "$FILE_PATH" ]; then
    FULL_FILE_PATH="$REPO_PATH/$FILE_PATH"
    if [ ! -f "$FULL_FILE_PATH" ]; then
        echo "File not found: $FULL_FILE_PATH"
        exit 1
    fi
fi

# Change to the script directory
cd "$SCRIPT_DIR"

# Build model parameter
MODEL_PARAM=""
if [ ! -z "$MODEL_NAME" ]; then
    MODEL_PARAM="--model $MODEL_NAME"
fi

# Print analysis information
echo "Analyzing local folder/repository: $REPO_NAME"
echo "Path: $REPO_PATH"

if [ ! -z "$FILE_PATH" ]; then
    echo "Target file: $FILE_PATH"
fi

if [ ! -z "$LINE_NUMBER" ]; then
    echo "Target line: $LINE_NUMBER"
fi

if [ ! -z "$ERROR_TEXT" ]; then
    echo "Error to analyze: $ERROR_TEXT"
fi

echo ""

# Run Basic Agent with appropriate parameters
if [ ! -z "$ANALYZE_FLAG" ]; then
    python3 run.py $MODEL_PARAM --project-path "$REPO_PATH" --analyze
elif [ ! -z "$ERROR_TEXT" ]; then
    python3 run.py $MODEL_PARAM --project-path "$REPO_PATH" --error "$ERROR_TEXT"
elif [ ! -z "$FILE_PATH" ]; then
    COMMAND="python3 run.py $MODEL_PARAM --project-path \"$REPO_PATH\" --file \"$FILE_PATH\""
    if [ ! -z "$LINE_NUMBER" ]; then
        COMMAND="$COMMAND --line $LINE_NUMBER"
    fi
    eval $COMMAND
else
    # Default: analyze the repository
    python3 run.py $MODEL_PARAM --project-path "$REPO_PATH" --analyze
fi 