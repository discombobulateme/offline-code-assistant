#!/usr/bin/env python3

import os
import json
import subprocess
import tempfile
from rich.console import Console

console = Console()

class LLMManager:
    """
    Manages interactions with local LLMs through Ollama
    """
    
    def __init__(self, config):
        self.config = config
        self.models = {model['name']: model for model in config['models']['available']}
        self.current_model = config['models']['default']
        self.verify_models()
    
    @property
    def model_name(self):
        """Return the current model name"""
        return self.current_model
    
    def verify_models(self):
        """Verify that required models are available in Ollama"""
        try:
            result = subprocess.run(
                ["ollama", "list"], 
                capture_output=True, 
                text=True, 
                check=True
            )
            
            available_models = set()
            for line in result.stdout.splitlines()[1:]:  # Skip header line
                if line.strip():
                    model_name = line.split()[0].split(':')[0]  # Extract base model name
                    available_models.add(model_name)
            
            missing_models = []
            for model_name in self.models:
                if model_name not in available_models:
                    missing_models.append(model_name)
            
            if missing_models:
                console.print(f"[bold yellow]Warning: The following models are not available: {', '.join(missing_models)}[/bold yellow]")
                console.print("[yellow]You can pull them using 'ollama pull <model_name>'[/yellow]")
        except Exception as e:
            console.print(f"[bold red]Error verifying models: {str(e)}[/bold red]")
            console.print("[yellow]Make sure Ollama is installed and running.[/yellow]")
    
    def set_model(self, model_name):
        """Set the current model to use"""
        if model_name in self.models:
            self.current_model = model_name
            return True
        return False
    
    def query(self, prompt, system_prompt=None, temperature=None):
        """
        Send a query to the LLM and get a response
        """
        model_config = self.models[self.current_model]
        system = system_prompt or model_config.get('system_prompt', '')
        temp = temperature or model_config.get('temperature', 0.7)
        max_tokens = model_config.get('max_tokens', 4000)
        
        try:
            # Use the JSON API format which is more reliable
            prompt_with_system = f"{system}\n\n{prompt}" if system else prompt
            
            console.print("[dim]Thinking...[/dim]")
            # According to the latest Ollama documentation, we need to pass the prompt directly
            result = subprocess.run(
                ["ollama", "run", self.current_model, prompt_with_system],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                console.print(f"[bold red]Error querying LLM: {result.stderr}[/bold red]")
                return "Sorry, there was an error with the LLM. Please try again."
                
            return result.stdout.strip()
            
        except Exception as e:
            console.print(f"[bold red]Error querying LLM: {str(e)}[/bold red]")
            return "Sorry, there was an error with the LLM. Please try again."
    
    def generate_with_context(self, prompt, context):
        """
        Generate a response with additional context
        """
        formatted_prompt = f"""
Context information:
{context}

User request:
{prompt}

Please provide a helpful response based on the context above.
"""
        return self.query(formatted_prompt)
    
    def list_available_models(self):
        """
        List available models
        """
        return list(self.models.keys())
    
    def get_current_model_info(self):
        """
        Get information about current model
        """
        return self.models.get(self.current_model, {})