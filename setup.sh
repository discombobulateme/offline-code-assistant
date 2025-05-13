#!/bin/bash

# Basic Agent setup script

echo "Setting up Basic Agent..."

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the script directory
cd "$SCRIPT_DIR"

# Check for required tools
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not found."
    exit 1
fi

if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is required but not found."
    exit 1
fi

if ! command -v ollama &> /dev/null; then
    echo "Warning: Ollama is not found."
    echo "Please install Ollama: https://github.com/ollama/ollama"
    echo "Visit: https://github.com/ollama/ollama for installation instructions."
    exit 1
fi

# Create virtual environment if requested
if [ "$1" == "--venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    
    # Activate virtual environment
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        echo "Virtual environment activated."
    else
        echo "Failed to create virtual environment."
        exit 1
    fi
fi

# Install dependencies
echo "Installing dependencies..."
pip3 install -r requirements.txt

# Make scripts executable
chmod +x run.py
chmod +x basic-agent.sh
chmod +x analyze-repo.sh
chmod +x analyze-specific.sh

echo "Setup complete!"
echo ""
echo "To run Basic Agent, use: ./basic-agent.sh"

# Check for Ollama models
echo ""
echo "Checking for required Ollama models..."
    
MODELS=("deepseek-r1" "llama3.1" "mistral")
MISSING_MODELS=()
    
for MODEL in "${MODELS[@]}"; do
    if ! ollama list | grep -q "$MODEL"; then
        MISSING_MODELS+=("$MODEL")
    fi
done
    
if [ ${#MISSING_MODELS[@]} -gt 0 ]; then
    echo "The following models need to be installed: ${MISSING_MODELS[*]}"
    echo "Install them with:"
    
    for MODEL in "${MISSING_MODELS[@]}"; do
        echo "  ollama pull $MODEL"
    done
else
    echo "All required models are installed."
fi 