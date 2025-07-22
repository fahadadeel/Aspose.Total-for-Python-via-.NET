# docling/frontend/cli/utils/file_handler.py

import os
import glob
from pathlib import Path
from typing import List, Tuple, Optional
from ..config import CLIConfig

class FileHandler:
    """Handles file operations for the CLI"""
    
    def __init__(self):
        self.config = CLIConfig()
    
    def validate_input_file(self, file_path: str) -> Tuple[bool, str]:
        """
        Validate input file exists and is supported
        Returns: (is_valid, error_message)
        """
        path = Path(file_path)
        
        # Check if file exists
        if not path.exists():
            return False, f"File not found: {file_path}"
        
        # Check if it's a file (not directory)
        if not path.is_file():
            return False, f"Path is not a file: {file_path}"
        
        # Check file size
        file_size_mb = path.stat().st_size / (1024 * 1024)
        if file_size_mb > self.config.MAX_FILE_SIZE_MB:
            return False, f"File too large: {file_size_mb:.1f}MB (max: {self.config.MAX_FILE_SIZE_MB}MB)"
        
        # Check if supported
        if not self.config.is_supported_file(file_path):
            supported_exts = ', '.join(self.config.get_all_supported_extensions())
            return False, f"Unsupported file type. Supported: {supported_exts}"
        
        return True, ""
    
    def find_files_in_directory(self, directory: str, recursive: bool = False) -> List[str]:
        """
        Find all supported files in a directory
        """
        supported_files = []
        search_path = Path(directory)
        
        if not search_path.exists() or not search_path.is_dir():
            return []
        
        # Get all supported extensions
        extensions = self.config.get_all_supported_extensions()
        
        for ext in extensions:
            if recursive:
                pattern = str(search_path / "**" / f"*{ext}")
                files = glob.glob(pattern, recursive=True)
            else:
                pattern = str(search_path / f"*{ext}")
                files = glob.glob(pattern)
            
            supported_files.extend(files)
        
        return sorted(supported_files)
    
    def create_output_path(self, input_file: str, output_dir: str, output_format: str) -> str:
        """
        Create output file path based on input file and format
        """
        input_path = Path(input_file)
        output_path = Path(output_dir)
        
        # Create output directory if it doesn't exist
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Generate output filename
        base_name = input_path.stem
        
        if output_format == 'markdown':
            ext = '.md'
        elif output_format == 'html':
            ext = '.html'
        elif output_format == 'json':
            ext = '.json'
        else:
            ext = '.txt'
        
        output_file = output_path / f"{base_name}{ext}"
        
        # Handle duplicate names by adding numbers
        counter = 1
        original_output_file = output_file
        while output_file.exists():
            output_file = output_path / f"{base_name}_{counter}{ext}"
            counter += 1
        
        return str(output_file)
    
    def save_output(self, content: str, output_path: str) -> bool:
        """
        Save converted content to output file
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            return False
    
    def get_file_info(self, file_path: str) -> dict:
        """
        Get information about a file
        """
        path = Path(file_path)
        
        if not path.exists():
            return {}
        
        stat = path.stat()
        
        return {
            'name': path.name,
            'size_bytes': stat.st_size,
            'size_mb': stat.st_size / (1024 * 1024),
            'type': self.config.detect_document_type(file_path),
            'extension': path.suffix.lower(),
            'absolute_path': str(path.absolute())
        }