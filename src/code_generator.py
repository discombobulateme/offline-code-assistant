#!/usr/bin/env python3

import os
from rich.console import Console

console = Console()

class CodeGenerator:
    """
    Handles code generation using the LLM
    """
    
    def __init__(self, llm_manager):
        self.llm_manager = llm_manager
    
    def generate(self, prompt, project_path=None, context=None):
        """
        Generate code based on prompt and optional context
        """
        # Add a system prompt for code generation
        system_prompt = """
You are an expert programmer. You generate high-quality, functional code based on requirements.
Make sure the code is:
- Well-documented with minimal comments
- Follows best practices for the language
- Complete and ready to use without additional changes
- Written in a clean, maintainable style
"""
        
        formatted_prompt = prompt
        
        # Add context if provided
        if context:
            formatted_prompt = f"""
Context:
{context}

Generate the following code:
{prompt}
"""
        
        # Call the LLM
        response = self.llm_manager.query(
            formatted_prompt,
            system_prompt=system_prompt,
            temperature=0.2  # Lower temperature for more deterministic code generation
        )
        
        # Extract code blocks from response
        code = self._extract_code(response)
        return code
    
    def generate_function(self, function_description, language, context=None):
        """
        Generate a specific function based on description
        """
        prompt = f"""
Generate a function in {language} that does the following:
{function_description}

Only give me the function code without explanations.
"""
        return self.generate(prompt, context=context)
    
    def complete_code(self, partial_code, language):
        """
        Complete partial code
        """
        prompt = f"""
Complete the following {language} code:

```{language}
{partial_code}
```

Only provide the completed code without explanations.
"""
        return self.generate(prompt)
    
    def fix_code(self, broken_code, error_message, language):
        """
        Fix broken code based on error message
        """
        prompt = f"""
Fix the following {language} code that is producing this error:

Error: {error_message}

Code:
```{language}
{broken_code}
```

Only provide the fixed code without explanations.
"""
        return self.generate(prompt)
    
    def generate_file(self, file_description, filename, language, project_path=None):
        """
        Generate a complete file based on description
        """
        ext = os.path.splitext(filename)[1].lstrip('.')
        if not ext and language:
            # Map language name to extension
            ext_map = {
                'python': 'py',
                'javascript': 'js',
                'typescript': 'ts',
                'html': 'html',
                'css': 'css',
                'c': 'c',
                'cpp': 'cpp',
                'c++': 'cpp',
                'java': 'java',
                'go': 'go',
                'rust': 'rs',
            }
            ext = ext_map.get(language.lower(), '')
            filename = f"{filename}.{ext}"
        
        prompt = f"""
Generate a complete {language} file named '{filename}' that:
{file_description}

Only provide the code for the file without explanations.
"""
        code = self.generate(prompt)
        
        if project_path:
            file_path = os.path.join(project_path, filename)
            try:
                # Create directories if needed
                os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
                
                # Write the file
                with open(file_path, 'w') as f:
                    f.write(code)
                console.print(f"[bold green]Generated file: {filename}[/bold green]")
            except Exception as e:
                console.print(f"[bold red]Error writing file {filename}: {str(e)}[/bold red]")
        
        return code
    
    def _extract_code(self, response):
        """
        Extract code blocks from text response
        """
        import re
        
        # Look for code blocks with triple backticks
        code_blocks = re.findall(r'```(?:\w+)?\n(.*?)```', response, re.DOTALL)
        
        if code_blocks:
            # Return the first code block found
            return code_blocks[0].strip()
        
        # If no code blocks, return the entire response
        return response.strip() 