# docling/frontend/cli/utils/output_formatter.py

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.text import Text
from typing import List, Dict, Any
import time

class OutputFormatter:
    """Handles formatted output for the CLI using Rich library"""
    
    def __init__(self):
        self.console = Console()
    
    def print_success(self, message: str):
        """Print success message in green"""
        self.console.print(f"✅ {message}", style="bold green")
    
    def print_error(self, message: str):
        """Print error message in red"""
        self.console.print(f"❌ {message}", style="bold red")
    
    def print_warning(self, message: str):
        """Print warning message in yellow"""
        self.console.print(f"⚠️  {message}", style="bold yellow")
    
    def print_info(self, message: str):
        """Print info message in blue"""
        self.console.print(f"ℹ️  {message}", style="bold blue")
    
    def print_header(self, title: str):
        """Print formatted header"""
        panel = Panel(
            Text(title, justify="center", style="bold white"),
            border_style="blue",
            padding=(1, 2)
        )
        self.console.print(panel)
    
    def print_file_info(self, file_info: Dict[str, Any]):
        """Print file information in a formatted table"""
        table = Table(show_header=True, header_style="bold blue")
        table.add_column("Property")
        table.add_column("Value")
        
        table.add_row("File Name", file_info.get('name', 'Unknown'))
        table.add_row("Size", f"{file_info.get('size_mb', 0):.2f} MB")
        table.add_row("Type", file_info.get('type', 'Unknown').title())
        table.add_row("Extension", file_info.get('extension', 'Unknown'))
        
        self.console.print(table)
    
    def print_conversion_summary(self, results: List[Dict[str, Any]]):
        """Print summary of conversion results"""
        
        # Create summary table
        table = Table(show_header=True, header_style="bold blue")
        table.add_column("File", style="cyan")
        table.add_column("Status", justify="center")
        table.add_column("Output", style="green")
        table.add_column("Time (s)", justify="right")
        
        successful = 0
        failed = 0
        
        for result in results:
            # Determine status style and icon
            if result.get('success', False):
                status = "✅ Success"
                status_style = "green"
                successful += 1
            else:
                status = "❌ Failed"
                status_style = "red"
                failed += 1
            
            table.add_row(
                result.get('input_file', 'Unknown'),
                Text(status, style=status_style),
                result.get('output_file', 'N/A'),
                f"{result.get('processing_time', 0):.2f}"
            )
        
        self.console.print(table)
        
        # Print summary stats
        total = len(results)
        self.console.print(f"\n📊 Summary: {successful}/{total} successful, {failed}/{total} failed")
    
    def print_supported_formats(self):
        """Print supported formats information"""
        
        # Input formats table
        input_table = Table(title="Supported Input Formats", show_header=True, header_style="bold blue")
        input_table.add_column("Document Type", style="cyan")
        input_table.add_column("Extensions", style="green")
        
        input_table.add_row("Excel", ".xlsx, .xls")
        input_table.add_row("Word", ".docx, .doc")
        input_table.add_row("PowerPoint", ".pptx, .ppt")
        
        self.console.print(input_table)
        
        # Output formats table
        output_table = Table(title="Supported Output Formats", show_header=True, header_style="bold blue")
        output_table.add_column("Format", style="cyan")
        output_table.add_column("Description", style="green")
        
        output_table.add_row("markdown", "Markdown format with optional post-processing")
        output_table.add_row("html", "HTML format")
        output_table.add_row("json", "JSON format (Excel only)")
        
        self.console.print(output_table)
        
        # Post-processing options
        processing_table = Table(title="Post-Processing Options (Markdown only)", 
                               show_header=True, header_style="bold blue")
        processing_table.add_column("Option", style="cyan")
        processing_table.add_column("Description", style="green")
        
        processing_table.add_row("--remove-images", "Remove all images from output")
        processing_table.add_row("--encode-images-base64", "Encode images as base64")
        processing_table.add_row("--ocr-images", "Extract text from images using OCR")
        processing_table.add_row("--convert-math-to-latex", "Convert plain math to LaTeX")
        
        self.console.print(processing_table)
    
    def create_progress_context(self, description: str = "Processing"):
        """Create a progress context for long operations"""
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=self.console
        )
    
    def print_banner(self):
        """Print application banner"""
        banner = """
╔══════════════════════════════════════╗
║            Docling CLI               ║
║     Document Conversion Tool         ║
╚══════════════════════════════════════╝
        """
        self.console.print(Text(banner, style="bold blue"))
    
    def print_usage_examples(self):
        """Print usage examples"""
        examples_text = """
[bold blue]Usage Examples:[/bold blue]

[green]# Convert single file to markdown[/green]
docling convert document.xlsx

[green]# Convert to HTML with custom output directory[/green] 
docling convert document.docx --format html --output ./converted

[green]# Batch convert all files in directory[/green]
docling batch ./documents --format markdown --recursive

[green]# Convert with post-processing[/green]
docling convert presentation.pptx --format markdown --remove-images --convert-math-to-latex

[green]# Get help[/green]
docling --help
docling convert --help
        """
        
        panel = Panel(examples_text, title="Examples", border_style="green")
        self.console.print(panel)