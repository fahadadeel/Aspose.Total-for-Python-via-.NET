# docling/frontend/cli/commands/info.py

import click
import sys
import os
from pathlib import Path

# Add parent directories to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../../"))

from ..config import CLIConfig
from ..utils.file_handler import FileHandler
from ..utils.output_formatter import OutputFormatter

@click.command()
@click.option('--formats', 'show_formats',
              is_flag=True,
              help='Show supported input and output formats')
@click.option('--examples', 'show_examples',
              is_flag=True,
              help='Show usage examples')
@click.option('--file', 'file_path',
              type=click.Path(exists=True),
              help='Show information about a specific file')
def info(show_formats: bool, show_examples: bool, file_path: str):
    """
    Show information about Docling CLI capabilities and supported formats.
    """
    
    formatter = OutputFormatter()
    config = CLIConfig()
    file_handler = FileHandler()
    
    # If no specific option is provided, show general info
    if not any([show_formats, show_examples, file_path]):
        formatter.print_banner()
        formatter.print_info("Docling CLI - Document Conversion Tool")
        formatter.print_info("Convert Excel, Word, and PowerPoint documents to various formats.")
        formatter.print_info("")
        formatter.print_info("Use 'docling info --help' to see available options.")
        formatter.print_info("Use 'docling --help' to see all commands.")
        return
    
    # Show supported formats
    if show_formats:
        formatter.print_header("Supported Formats")
        formatter.print_supported_formats()
        formatter.console.print()
    
    # Show file information
    if file_path:
        formatter.print_header(f"File Information")
        
        # Validate and get file info
        is_valid, error_msg = file_handler.validate_input_file(file_path)
        
        if not is_valid:
            formatter.print_error(error_msg)
            return
        
        file_info = file_handler.get_file_info(file_path)
        formatter.print_file_info(file_info)
        
        # Check if file is supported
        if config.is_supported_file(file_path):
            formatter.print_success("✅ This file type is supported for conversion")
            doc_type = config.detect_document_type(file_path)
            
            # Show available output formats for this document type
            available_formats = ['markdown', 'html']
            if doc_type == 'excel':
                available_formats.append('json')
            
            formatter.print_info(f"Available output formats: {', '.join(available_formats)}")
        else:
            formatter.print_warning("⚠️  This file type is not supported")
            supported_exts = ', '.join(config.get_all_supported_extensions())
            formatter.print_info(f"Supported extensions: {supported_exts}")
        
        formatter.console.print()
    
    # Show usage examples
    if show_examples:
        formatter.print_header("Usage Examples")
        formatter.print_usage_examples()

@click.command()
def version():
    """Show version information."""
    formatter = OutputFormatter()
    formatter.print_info("Docling CLI v1.0.0")
    formatter.print_info("Document conversion tool compatible with IBM Docling")

@click.command()
@click.argument('directory', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option('--recursive', '-r', 'recursive',
              is_flag=True,
              help='Search recursively in subdirectories')
def scan(directory: str, recursive: bool):
    """
    Scan a directory for supported documents.
    
    DIRECTORY: Directory to scan for supported files
    """
    formatter = OutputFormatter()
    file_handler = FileHandler()
    config = CLIConfig()
    
    formatter.print_header(f"Scanning Directory: {directory}")
    
    # Find supported files
    files = file_handler.find_files_in_directory(directory, recursive)
    
    if not files:
        formatter.print_warning("No supported files found")
        formatter.print_info("Supported extensions: " + ", ".join(config.get_all_supported_extensions()))
        return
    
    # Group files by type
    files_by_type = {
        'excel': [],
        'word': [],
        'powerpoint': []
    }
    
    total_size = 0
    
    for file_path in files:
        doc_type = config.detect_document_type(file_path)
        files_by_type[doc_type].append(file_path)
        
        # Get file size
        file_info = file_handler.get_file_info(file_path)
        total_size += file_info.get('size_bytes', 0)
    
    # Display summary
    formatter.print_info(f"Found {len(files)} supported files:")
    formatter.print_info(f"  📊 Excel: {len(files_by_type['excel'])} files")
    formatter.print_info(f"  📄 Word: {len(files_by_type['word'])} files") 
    formatter.print_info(f"  🎞️ PowerPoint: {len(files_by_type['powerpoint'])} files")
    formatter.print_info(f"  💾 Total size: {total_size / (1024*1024):.2f} MB")
    
    # Show detailed list if requested
    formatter.console.print("\n[bold blue]Files found:[/bold blue]")
    
    for doc_type, type_files in files_by_type.items():
        if type_files:
            formatter.console.print(f"\n[bold cyan]{doc_type.title()} Files:[/bold cyan]")
            for file_path in sorted(type_files):
                file_info = file_handler.get_file_info(file_path)
                relative_path = os.path.relpath(file_path, directory)
                formatter.console.print(f"  • {relative_path} ({file_info.get('size_mb', 0):.2f} MB)")
    
    formatter.print_success(f"\nReady to batch convert with: docling batch {directory}")