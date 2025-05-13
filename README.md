# Offline Code Assistant

A local AI chat interface for offline development using local LLMs through Ollama.

The agent has context access to both the current directory and its parent directory, allowing you to easily reference and analyze other folders or projects. For example, if the agent is located at `Documents/project/agent`, it will have access to everything inside `project`, and you can analyze any folder in the parent directory with simple commands.

## Features

- Uses local LLMs (Ollama) for code assistance
- Supports multiple models (deepseek-r1, llama3.1, mistral)
- Transforms your terminal in chat interface with intelligent commands
- Has awareness of parent directory for multi-project context
- Fully functional offline with local models
- Saves conversation history to markdown files for future reference

## Prerequisites

- Python 3.x
- [Ollama](https://github.com/ollama/ollama) installed and running

## Setup

### Automated Setup

1. Run the setup script:
   ```bash
   ./setup.sh
   ```
   
   For a virtual environment, use:
   ```bash
   ./setup.sh --venv
   ```

### Manual Setup

1. Ensure Ollama is installed and running
2. Make sure you have the following models available in Ollama:
   ```bash
   ollama pull deepseek-r1
   ollama pull llama3.1
   ollama pull mistral
   ```
3. Install dependencies: 
   ```bash
   pip install -r requirements.txt
   ```
4. Make scripts executable:
   ```bash
   chmod +x run.py offline-assistant.sh
   ```

## Usage

```bash
# Start the agent with the default model (deepseek-r1)
./offline-assistant.sh

# Or specify a model directly
./offline-assistant.sh --model llama3.1

# Enable debug mode
./offline-assistant.sh --debug

# Save conversation history to a file
./offline-assistant.sh --save-history
```

## Chat Commands

Once the agent is running, you can use these commands:

```
# Get help for available commands
help

# Analyze a file in the current project
analyze src/main.py

# Analyze a folder in the parent directory
repo flying-sausage

# Analyze an error message
error "segmentation fault at 0x00000"

# Generate code based on a description
generate "A Python function to parse GPS data"

# Enable conversation history saving or change the filename
save_history my_conversation_name

# For any other input, the agent treats it as a direct query to the LLM
What's the best way to optimize GPS tracking for skydivers?
```

## Configuration

Edit the `config/config.yaml` file to customize:
- Default model selection
- Model temperature and max tokens
- System prompts for each model
- Project settings (ignored directories, file extensions)

## Conversation History

The agent can save your conversation history to Markdown files for future reference:

- Use the `--save-history` flag when starting the agent to automatically save all conversations
- Use the `save_history [filename]` command during a session to start saving or change the filename
- Conversation files are saved in the `history/` folder with timestamps
- Each file includes both your inputs and the LLM's responses in a readable format

## Working Offline

Offline Code Assistant is designed for offline use:

1. Ensure all required LLM models are downloaded before going offline
2. The agent operates entirely locally, with no internet connection required
3. All code analysis, suggestions, and generation happen on your machine
4. Project documentation can be generated without external resources
5. The system keeps all context in your local memory 