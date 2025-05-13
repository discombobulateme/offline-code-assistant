#!/usr/bin/env python3

import os
import re
import fnmatch
from rich.console import Console

console = Console()

class ProjectAnalyzer:
    """
    Analyzes project structure and files for context
    """
    
    def __init__(self, config):
        self.config = config
        self.ignored_dirs = config['project'].get('ignored_directories', [])
        self.code_extensions = config['project'].get('code_extensions', [])
        self.file_cache = {}  # Cache for file contents
    
    def analyze_project(self, project_path):
        """
        Analyze project structure and return information
        """
        if not os.path.exists(project_path):
            raise FileNotFoundError(f"Project path does not exist: {project_path}")
        
        project_info = {
            'path': project_path,
            'files': [],
            'file_count': 0,
            'directories': [],
            'directory_count': 0,
            'file_types': {},
        }
        
        for root, dirs, files in os.walk(project_path):
            # Skip ignored directories
            dirs[:] = [d for d in dirs if not self._is_ignored_dir(d)]
            
            rel_root = os.path.relpath(root, project_path)
            if rel_root != '.':
                project_info['directories'].append(rel_root)
                project_info['directory_count'] += 1
            
            for file in files:
                file_path = os.path.join(rel_root, file)
                if rel_root == '.':
                    file_path = file
                
                project_info['files'].append(file_path)
                project_info['file_count'] += 1
                
                # Track file types
                ext = os.path.splitext(file)[1].lower()
                if ext:
                    project_info['file_types'][ext] = project_info['file_types'].get(ext, 0) + 1
        
        return project_info
    
    def analyze_file(self, file_path, content=None):
        """
        Analyze a single file and return information
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File does not exist: {file_path}")
        
        if content is None:
            content = self.read_file(file_path)
        
        ext = os.path.splitext(file_path)[1].lower().lstrip('.')
        
        file_info = {
            'path': file_path,
            'type': ext,
            'lines': content.count('\n') + 1,
            'size': len(content),
        }
        
        # Analyze file based on type
        if ext in ('py', 'js', 'c', 'cpp', 'h'):
            # Add language-specific analysis
            if ext == 'py':
                file_info.update(self._analyze_python(content))
            elif ext in ('c', 'cpp', 'h'):
                file_info.update(self._analyze_c_cpp(content))
            elif ext == 'js':
                file_info.update(self._analyze_javascript(content))
        
        return file_info
    
    def read_file(self, file_path):
        """
        Read file contents, with caching
        """
        if file_path in self.file_cache:
            return self.file_cache[file_path]
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
                self.file_cache[file_path] = content
                return content
        except Exception as e:
            console.print(f"[bold red]Error reading file {file_path}: {str(e)}[/bold red]")
            return ""
    
    def get_project_summary(self, project_path):
        """
        Generate a summary of the project
        """
        project_info = self.analyze_project(project_path)
        
        summary = {
            'path': project_info['path'],
            'file_count': project_info['file_count'],
            'directory_count': project_info['directory_count'],
            'file_types': project_info['file_types'],
            'important_files': [],
        }
        
        # Identify important files
        for file in project_info['files']:
            lower_file = file.lower()
            if any(pattern in lower_file for pattern in ('main', 'index', 'app', 'config')):
                summary['important_files'].append(file)
        
        return summary
    
    def get_file_context(self, file_path, line_number=None, context_lines=5):
        """
        Get file content with optional context around a specific line
        """
        content = self.read_file(file_path)
        lines = content.splitlines()
        
        if line_number is None:
            return content
        
        start = max(0, line_number - context_lines - 1)
        end = min(len(lines), line_number + context_lines)
        
        return '\n'.join(lines[start:end])
    
    def _is_ignored_dir(self, dir_name):
        """Check if directory should be ignored"""
        return any(fnmatch.fnmatch(dir_name, pattern) for pattern in self.ignored_dirs)
    
    def _analyze_python(self, content):
        """Analyze Python file"""
        info = {
            'imports': [],
            'functions': [],
            'classes': [],
        }
        
        # Simple regex-based analysis
        import_pattern = re.compile(r'^(?:from\s+(\S+)\s+)?import\s+(.+)$', re.MULTILINE)
        function_pattern = re.compile(r'^def\s+([^\s(]+)', re.MULTILINE)
        class_pattern = re.compile(r'^class\s+([^\s:(]+)', re.MULTILINE)
        
        # Extract imports
        for match in import_pattern.finditer(content):
            if match.group(1):  # from X import Y
                module = match.group(1)
                for item in match.group(2).split(','):
                    info['imports'].append(f"{module}.{item.strip()}")
            else:  # import X
                for item in match.group(2).split(','):
                    info['imports'].append(item.strip())
        
        # Extract functions and classes
        info['functions'] = [match.group(1) for match in function_pattern.finditer(content)]
        info['classes'] = [match.group(1) for match in class_pattern.finditer(content)]
        
        return info
    
    def _analyze_c_cpp(self, content):
        """Analyze C/C++ file"""
        info = {
            'includes': [],
            'functions': [],
            'structs': [],
        }
        
        # Simple regex-based analysis
        include_pattern = re.compile(r'#include\s+[<"]([^>"]+)[>"]', re.MULTILINE)
        function_pattern = re.compile(r'(\w+)\s+(\w+)\s*\([^)]*\)\s*{', re.MULTILINE)
        struct_pattern = re.compile(r'(struct|class|enum)\s+(\w+)', re.MULTILINE)
        
        # Extract includes, functions, and structs
        info['includes'] = [match.group(1) for match in include_pattern.finditer(content)]
        
        for match in function_pattern.finditer(content):
            if match.group(1) not in ('if', 'for', 'while', 'switch'):
                info['functions'].append(match.group(2))
        
        for match in struct_pattern.finditer(content):
            info['structs'].append(f"{match.group(1)} {match.group(2)}")
        
        return info
    
    def _analyze_javascript(self, content):
        """Analyze JavaScript file"""
        info = {
            'imports': [],
            'functions': [],
            'classes': [],
        }
        
        # Simple regex-based analysis
        import_pattern = re.compile(r'(import|require)\s+.+?[\'"]([^\'"]+)[\'"]', re.MULTILINE)
        function_pattern = re.compile(r'function\s+(\w+)|(\w+)\s*=\s*function', re.MULTILINE)
        class_pattern = re.compile(r'class\s+(\w+)', re.MULTILINE)
        
        # Extract imports, functions, and classes
        info['imports'] = [match.group(2) for match in import_pattern.finditer(content)]
        
        for match in function_pattern.finditer(content):
            func_name = match.group(1) or match.group(2)
            if func_name:
                info['functions'].append(func_name)
        
        info['classes'] = [match.group(1) for match in class_pattern.finditer(content)]
        
        return info 