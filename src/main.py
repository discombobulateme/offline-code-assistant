#!/usr/bin/env python3

import os
import sys
import yaml
import typer
import subprocess
from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel
from datetime import datetime

from src.llm_manager import LLMManager
from src.project_analyzer import ProjectAnalyzer
from src.code_generator import CodeGenerator

app = typer.Typer()
console = Console()

def load_config():
    """Load configuration from config file"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                              "config", "config.yaml")
    try:
        with open(config_path, 'r') as file:
            return yaml.safe_load(file)
    except Exception as e:
        console.print(f"[bold red]Error loading config: {str(e)}[/bold red]")
        sys.exit(1)

@app.command()
def main(
    model: str = None, 
    project_path: str = ".", 
    parent_context: bool = typer.Option(True, "--parent-context/--no-parent-context", help="Include parent folder as context"),
    debug: bool = typer.Option(False, "--debug", "-d", help="Enable debug mode"),
    save_history: bool = typer.Option(False, "--save-history", "-s", help="Save conversation history to file")
):
    """
    Start the Offline Code Assistant with optional model selection
    """
    console.print(Panel.fit(
        "[bold blue]Offline Code Assistant[/bold blue]\n"
        "[italic]Your offline coding assistant[/italic]",
        border_style="blue"
    ))
    
    # Load configuration
    config = load_config()
    
    # Use specified model or default from config
    model_name = model or config["models"]["default"]
    console.print(f"Using model: [bold green]{model_name}[/bold green]")
    
    # Initialize components
    llm_manager = LLMManager(config)
    project_analyzer = ProjectAnalyzer(config)
    code_generator = CodeGenerator(llm_manager)
    
    # Debug mode
    if debug:
        console.print("[bold yellow]Debug mode enabled[/bold yellow]")
        
    # Conversation history mode
    if save_history:
        console.print("[bold yellow]Conversation history will be saved[/bold yellow]")
    
    # Scan project
    console.print("[bold]Analyzing project structure...[/bold]")
    project_info = project_analyzer.analyze_project(project_path)
    console.print(f"Found [bold]{project_info['file_count']}[/bold] files in project")
    
    # Get parent directory context if enabled
    parent_context_info = None
    if parent_context:
        parent_dir = os.path.dirname(os.path.abspath(project_path))
        console.print(f"[bold]Using parent folder as additional context: {os.path.basename(parent_dir)}[/bold]")
        parent_folders = []
        for item in os.listdir(parent_dir):
            item_path = os.path.join(parent_dir, item)
            if os.path.isdir(item_path):
                parent_folders.append(item)
        console.print(f"Available folders in parent directory: [bold]{', '.join(parent_folders)}[/bold]")
    
    # Start interactive loop
    run_interactive_loop(llm_manager, project_analyzer, code_generator, project_path, parent_context, parent_dir if parent_context else None, save_history)

def run_interactive_loop(llm_manager, project_analyzer, code_generator, project_path, parent_context, parent_dir, save_history):
    """Run the interactive command loop"""
    from prompt_toolkit import PromptSession
    from prompt_toolkit.history import FileHistory
    from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
    
    history_file = os.path.join(os.path.expanduser("~"), ".offline_assistant_history")
    session = PromptSession(
        history=FileHistory(history_file),
        auto_suggest=AutoSuggestFromHistory(),
    )
    
    # Initialize conversation history
    conversation_history = []
    if save_history:
        # Create a timestamped history file name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        history_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "history")
        os.makedirs(history_folder, exist_ok=True)
        conversation_file = os.path.join(history_folder, f"conversation_{timestamp}.md")
        console.print(f"[bold]Saving conversation to: {conversation_file}[/bold]")
        
        # Write header to the file
        with open(conversation_file, 'w') as f:
            f.write(f"# Offline Code Assistant Conversation - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"Model: {llm_manager.model_name}\n")
            f.write(f"Project: {os.path.basename(os.path.abspath(project_path))}\n\n")
            f.write("---\n\n")
    
    while True:
        try:
            user_input = session.prompt("\n[offline-assistant] > ")
            
            if user_input.lower() in ("exit", "quit"):
                console.print("[bold]Exiting Offline Code Assistant. Goodbye![/bold]")
                break
            
            if user_input.strip() == "":
                continue
            
            # Save user input to conversation history
            if save_history:
                conversation_history.append(("user", user_input))
                save_conversation(conversation_file, conversation_history)
                
            if user_input == "help":
                show_help()
            elif user_input.startswith("analyze "):
                file_path = user_input[8:].strip()
                analyze_file(project_analyzer, llm_manager, file_path, project_path, save_history, conversation_history, conversation_file)
            elif user_input.startswith("repo "):
                folder_name = user_input[5:].strip()
                analyze_repo(project_analyzer, llm_manager, folder_name, parent_dir, save_history, conversation_history, conversation_file)
            elif user_input.startswith("error "):
                error_text = user_input[6:].strip()
                analyze_error(llm_manager, error_text, project_path, save_history, conversation_history, conversation_file)
            elif user_input.startswith("generate "):
                prompt = user_input[9:].strip()
                generate_code(code_generator, prompt, project_path, save_history, conversation_history, conversation_file)
            elif user_input.startswith("save_history "):
                if not save_history:
                    console.print("[bold yellow]Enabling conversation history saving...[/bold yellow]")
                    save_history = True
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    history_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "history")
                    os.makedirs(history_folder, exist_ok=True)
                    conversation_file = os.path.join(history_folder, f"conversation_{timestamp}.md")
                    console.print(f"[bold]Saving conversation to: {conversation_file}[/bold]")
                    
                    # Write header to the file
                    with open(conversation_file, 'w') as f:
                        f.write(f"# Offline Code Assistant Conversation - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                        f.write(f"Model: {llm_manager.model_name}\n")
                        f.write(f"Project: {os.path.basename(os.path.abspath(project_path))}\n\n")
                        f.write("---\n\n")
                else:
                    new_filename = user_input[13:].strip()
                    if new_filename:
                        history_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "history")
                        new_file = os.path.join(history_folder, f"{new_filename}.md")
                        conversation_file = new_file
                        console.print(f"[bold]Now saving conversation to: {conversation_file}[/bold]")
                        
                        # Write existing history to the new file
                        with open(conversation_file, 'w') as f:
                            f.write(f"# Offline Code Assistant Conversation - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                            f.write(f"Model: {llm_manager.model_name}\n")
                            f.write(f"Project: {os.path.basename(os.path.abspath(project_path))}\n\n")
                            f.write("---\n\n")
                            save_conversation(conversation_file, conversation_history)
            else:
                # Default: Send to LLM
                response = llm_manager.query(user_input)
                console.print(Panel(response, border_style="green"))
                
                # Save response to conversation history
                if save_history:
                    conversation_history.append(("assistant", response))
                    save_conversation(conversation_file, conversation_history)
                
        except KeyboardInterrupt:
            console.print("\n[bold]Interrupted. Press Ctrl+C again to exit.[/bold]")
            try:
                input()
            except KeyboardInterrupt:
                console.print("[bold]Exiting Offline Code Assistant. Goodbye![/bold]")
                break
        except Exception as e:
            console.print(f"[bold red]Error: {str(e)}[/bold red]")

def save_conversation(file_path, conversation_history):
    """Save the conversation history to a file"""
    try:
        # Write header and conversation content to the file
        with open(file_path, 'w') as f:
            f.write(f"# Offline Code Assistant Conversation - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Write each message in the conversation history
            for role, content in conversation_history:
                if role == "user":
                    f.write(f"## User\n\n```\n{content}\n```\n\n")
                else:
                    f.write(f"## Assistant\n\n{content}\n\n")
    except Exception as e:
        console.print(f"[bold red]Error saving conversation: {str(e)}[/bold red]")

def analyze_file(project_analyzer, llm_manager, file_path, project_path, save_history=False, conversation_history=None, conversation_file=None):
    """Analyze a specific file"""
    try:
        full_path = os.path.join(project_path, file_path)
        if not os.path.exists(full_path):
            console.print(f"[bold red]File not found: {file_path}[/bold red]")
            return
        
        file_content = project_analyzer.read_file(full_path)
        file_info = project_analyzer.analyze_file(full_path, file_content)
        
        console.print(Panel(
            f"[bold]File Analysis: {file_path}[/bold]\n\n"
            f"Type: {file_info['type']}\n"
            f"Lines: {file_info['lines']}\n"
            f"Functions/Classes: {len(file_info.get('functions', []))}\n",
            border_style="blue"
        ))
        
        ext = file_info['type']
        if ext in ('py', 'js', 'c', 'cpp', 'h', 'md', 'txt', 'json', 'yaml', 'yml'):
            syntax = Syntax(file_content, ext, line_numbers=True)
            console.print(syntax)
            
            # Ask LLM to analyze the file
            prompt = f"""
Analyze this file: {os.path.basename(file_path)}

File type: {ext}
Lines: {file_info['lines']}

Content (first 100 lines or less):
{file_content[:10000] if len(file_content) > 10000 else file_content}

Provide a concise analysis of the file's purpose and structure.
"""
            response = llm_manager.query(prompt)
            console.print(Panel(response, border_style="green", title="File Analysis"))
            
            # Save the response to the conversation history if enabled
            if save_history and conversation_history is not None and conversation_file is not None:
                conversation_history.append(("assistant", response))
                save_conversation(conversation_file, conversation_history)
    except Exception as e:
        console.print(f"[bold red]Error analyzing file: {str(e)}[/bold red]")

def analyze_repo(project_analyzer, llm_manager, folder_name, parent_dir, save_history=False, conversation_history=None, conversation_file=None):
    """Analyze a repository in the parent directory"""
    if not parent_dir:
        console.print("[bold red]Parent directory context is not enabled. Use --parent-context flag.[/bold red]")
        return
    
    try:
        folder_path = os.path.join(parent_dir, folder_name)
        if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            console.print(f"[bold red]Folder not found: {folder_name}[/bold red]")
            console.print("Available folders:")
            for item in os.listdir(parent_dir):
                item_path = os.path.join(parent_dir, item)
                if os.path.isdir(item_path):
                    console.print(f"  - {item}")
            return
        
        console.print(f"[bold]Analyzing folder: {folder_name}[/bold]")
        project_summary = project_analyzer.get_project_summary(folder_path)
        console.print(Panel(
            f"[bold]Project Summary: {folder_name}[/bold]\n\n"
            f"Files: {project_summary['file_count']}\n"
            f"Directories: {project_summary['directory_count']}\n"
            f"File Types: {', '.join([f'{ext} ({count})' for ext, count in project_summary['file_types'].items()])}\n\n"
            f"Important Files:\n" + '\n'.join([f"- {f}" for f in project_summary['important_files']]),
            border_style="blue",
            title="Analysis"
        ))
        
        # Generate more in-depth analysis with LLM
        prompt = f"""
Analyze the following project structure for a high-level overview:

Project: {folder_name}
Files: {project_summary['file_count']}
Directories: {project_summary['directory_count']}
Important Files: {', '.join(project_summary['important_files'])}

Provide a concise project description and assessment.
"""
        response = llm_manager.query(prompt)
        console.print(Panel(response, border_style="green", title="AI Analysis"))
        
        # Save the response to the conversation history if enabled
        if save_history and conversation_history is not None and conversation_file is not None:
            conversation_history.append(("assistant", response))
            save_conversation(conversation_file, conversation_history)
    except Exception as e:
        console.print(f"[bold red]Error analyzing repository: {str(e)}[/bold red]")

def analyze_error(llm_manager, error_text, project_path, save_history=False, conversation_history=None, conversation_file=None):
    """Analyze a specific error message"""
    console.print(Panel(f"[bold]Analyzing Error:[/bold]\n\n{error_text}", border_style="yellow"))
    
    prompt = f"""
Analyze this error in the context of a software project:

Error: {error_text}

The project is located at: {project_path}

Provide:
1. A likely cause of this error
2. Potential solutions
3. Debugging steps to locate the issue
"""
    response = llm_manager.query(prompt)
    console.print(Panel(response, border_style="green", title="Error Analysis"))
    
    # Save the response to the conversation history if enabled
    if save_history and conversation_history is not None and conversation_file is not None:
        conversation_history.append(("assistant", response))
        save_conversation(conversation_file, conversation_history)

def generate_code(code_generator, prompt, project_path, save_history=False, conversation_history=None, conversation_file=None):
    """Generate code based on prompt"""
    try:
        code = code_generator.generate(prompt, project_path)
        console.print(Panel(code, border_style="green", title="Generated Code"))
        
        # Save the response to the conversation history if enabled
        if save_history and conversation_history is not None and conversation_file is not None:
            conversation_history.append(("assistant", code))
            save_conversation(conversation_file, conversation_history)
    except Exception as e:
        console.print(f"[bold red]Error generating code: {str(e)}[/bold red]")

def show_help():
    """Show help information"""
    help_text = """
    [bold]Offline Code Assistant Commands:[/bold]
    
    analyze <file>  - Analyze a specific file in the current project
    repo <folder>   - Analyze a folder from the parent directory
    error <text>    - Analyze an error message
    generate <desc> - Generate code based on description
    save_history [name] - Enable saving conversation history or change filename
    help            - Show this help message
    exit/quit       - Exit the application
    
    [bold]Tips:[/bold]
    
    - For any other input, the agent will treat it as a direct query to the LLM
    - Use project and parent folder context for better responses
    - The agent has access to all folders in the parent directory
    - Start the agent with --save-history to automatically save all conversations
    - Conversation history is saved in Markdown format in the history folder
    """
    console.print(Panel(help_text, border_style="blue", title="Help"))

if __name__ == "__main__":
    app() 