# docling/frontend/cli/main.py

import click
import sys
import os
from pathlib import Path

# Add parent directories to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../"))

from .commands.convert import convert
from .commands.batch import batch
from .commands.info import info, version, scan
from .utils.output_formatter import OutputFormatter

class DoclingCLI(click.Group):
    """Custom CLI group with enhanced help and error handling"""
    
    def format_help(self, ctx, formatter):
        """Custom help formatting"""
        # Print banner first
        output_formatter = OutputFormatter()
        output_formatter.print_banner()
        
        # Then show regular help
        super().format_help(ctx, formatter)
        
        # Add footer with examples
        formatter.write_paragraph()
        formatter.write_usage(ctx.get_usage(), "Examples", prefix="")
        formatter.write_paragraph()
        formatter.write(
            "  docling convert document.xlsx                    # Convert to markdown\n"
            "  docling convert file.docx -f html -o ./output   # Convert to HTML\n"
            "  docling batch ./docs --recursive                # Batch convert directory\n"
            "  docling info --formats                          # Show supported formats\n"
            "  docling scan ./documents                        # Scan directory for files"
        )

@click.group(cls=DoclingCLI, invoke_without_command=True)
@click.option('--version', is_flag=True, help='Show version information')
@click.pass_context
def cli(ctx, version):
    """
    Docling CLI - Document Conversion Tool
    
    Convert Excel, Word, and PowerPoint documents to various formats including
    Markdown, HTML, and JSON with optional post-processing capabilities.
    """
    # Handle version flag
    if version:
        formatter = OutputFormatter()
        formatter.print_info("Docling CLI v1.0.0")
        formatter.print_info("Document conversion tool compatible with IBM Docling")
        return
    
    # If no command is provided, show help
    if ctx.invoked_subcommand is None:
        formatter = OutputFormatter()
        formatter.print_banner()
        formatter.print_info("Use 'docling --help' to see available commands")
        formatter.print_info("Use 'docling info --examples' to see usage examples")

# Add commands to the CLI group
cli.add_command(convert)
cli.add_command(batch) 
cli.add_command(info)
cli.add_command(scan)
# Note: Removed version command to avoid conflict with --version flag

# Error handling
@cli.result_callback()
def process_result(result, **kwargs):
    """Process the result of CLI commands"""
    pass

def handle_exception(exc_type, exc_value, exc_traceback):
    """Global exception handler for the CLI"""
    if exc_type is KeyboardInterrupt:
        formatter = OutputFormatter()
        formatter.print_warning("\n⚠️  Operation cancelled by user")
        sys.exit(1)
    else:
        # For other exceptions, show error and exit
        formatter = OutputFormatter()
        formatter.print_error(f"Unexpected error: {exc_value}")
        formatter.print_info("Use --verbose for more details")
        sys.exit(1)

# Set global exception handler
sys.excepthook = handle_exception

if __name__ == '__main__':
    cli()