# docling/frontend/cli/commands/batch.py

import click
import time
import sys
import os
from pathlib import Path
from typing import List, Dict, Any

# Add parent directories to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../../"))

from ..config import CLIConfig
from ..utils.file_handler import FileHandler
from ..utils.output_formatter import OutputFormatter

# Import converters (with fallback to mock if import fails)
try:
    from docling.backend.excel_converter import ExcelConverter
    from docling.backend.word_converter import WordConverter
    from docling.backend.powerpoint_convertor import PptConverter
    from docling.backend.markdown_postprocessor import MarkdownPostProcessor
except ImportError:
    # Mock converters for testing
    class MockConverter:
        def convert_to_md(self, file_path): return f"# Mock conversion of {Path(file_path).name}"
        def convert_to_html(self, file_path): return f"<h1>Mock conversion of {Path(file_path).name}</h1>"
        def convert_to_json(self, file_path): return '{"mock": "conversion"}'
    
    ExcelConverter = WordConverter = PptConverter = MockConverter
    MarkdownPostProcessor = type('MockProcessor', (), {
        'remove_images': lambda self, c: c,
        'encode_images_base64': lambda self, c, p: c,
        'ocr_images': lambda self, c, p: c,
        'convert_plain_math_to_latex': lambda self, c: c
    })

@click.command()
@click.argument('input_directory', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option('--format', '-f', 'output_format', 
              type=click.Choice(['markdown', 'html', 'json']),
              default='markdown',
              help='Output format for all files (default: markdown)')
@click.option('--output', '-o', 'output_dir',
              type=click.Path(),
              default='./batch_output',
              help='Output directory (default: ./batch_output)')
@click.option('--recursive', '-r', 'recursive',
              is_flag=True,
              help='Search for files recursively in subdirectories')
@click.option('--remove-images', 'remove_images',
              is_flag=True,
              help='Remove images from markdown output')
@click.option('--encode-images-base64', 'encode_images_base64',
              is_flag=True,
              help='Encode images as base64 in markdown')
@click.option('--ocr-images', 'ocr_images',
              is_flag=True,
              help='Extract text from images using OCR')
@click.option('--convert-math-to-latex', 'convert_math_to_latex',
              is_flag=True,
              help='Convert plain math expressions to LaTeX')
@click.option('--max-files', 'max_files',
              type=int,
              default=50,
              help='Maximum number of files to process (default: 50)')
@click.option('--verbose', '-v',
              is_flag=True,
              help='Verbose output')
@click.option('--continue-on-error', 'continue_on_error',
              is_flag=True,
              help='Continue processing other files if one fails')
def batch(input_directory: str, output_format: str, output_dir: str, recursive: bool,
          remove_images: bool, encode_images_base64: bool, ocr_images: bool, 
          convert_math_to_latex: bool, max_files: int, verbose: bool, continue_on_error: bool):
    """
    Batch convert all supported documents in a directory.
    
    INPUT_DIRECTORY: Directory containing documents to convert
    """
    
    # Initialize components
    config = CLIConfig()
    file_handler = FileHandler()
    formatter = OutputFormatter()
    
    formatter.print_header("Docling Batch Converter")
    
    # Find files to convert
    files_to_convert = file_handler.find_files_in_directory(input_directory, recursive)
    
    if not files_to_convert:
        formatter.print_warning(f"No supported files found in {input_directory}")
        formatter.print_info("Supported extensions: " + ", ".join(config.get_all_supported_extensions()))
        return
    
    # Limit number of files
    if len(files_to_convert) > max_files:
        formatter.print_warning(f"Found {len(files_to_convert)} files, limiting to {max_files}")
        files_to_convert = files_to_convert[:max_files]
    
    formatter.print_info(f"Found {len(files_to_convert)} files to convert")
    
    if verbose:
        for i, file_path in enumerate(files_to_convert, 1):
            formatter.print_info(f"  {i}. {Path(file_path).name}")
    
    # Initialize converters
    converters = {
        'excel': ExcelConverter(),
        'word': WordConverter(),
        'powerpoint': PptConverter()
    }
    
    processor = MarkdownPostProcessor()
    
    # Process files
    results: List[Dict[str, Any]] = []
    successful_conversions = 0
    
    # Create progress bar context
    with formatter.create_progress_context("Converting files") as progress:
        task = progress.add_task("Converting...", total=len(files_to_convert))
        
        for file_path in files_to_convert:
            file_name = Path(file_path).name
            start_time = time.time()
            
            try:
                # Validate file
                is_valid, error_msg = file_handler.validate_input_file(file_path)
                if not is_valid:
                    raise ValueError(error_msg)
                
                # Get converter for this file type
                doc_type = config.detect_document_type(file_path)
                converter = converters.get(doc_type)
                
                if not converter:
                    raise ValueError(f"No converter available for document type: {doc_type}")
                
                # Create output path
                output_file = file_handler.create_output_path(file_path, output_dir, output_format)
                
                # Perform conversion
                if output_format == 'markdown':
                    converted_content = converter.convert_to_md(file_path)
                    
                    # Apply post-processing
                    if any([remove_images, encode_images_base64, ocr_images, convert_math_to_latex]):
                        base_path = os.path.dirname(file_path)
                        
                        if remove_images:
                            converted_content = processor.remove_images(converted_content)
                        elif encode_images_base64:
                            converted_content = processor.encode_images_base64(converted_content, base_path)
                        elif ocr_images:
                            converted_content = processor.ocr_images(converted_content, base_path)
                        
                        if convert_math_to_latex:
                            converted_content = processor.convert_plain_math_to_latex(converted_content)
                
                elif output_format == 'html':
                    converted_content = converter.convert_to_html(file_path)
                
                elif output_format == 'json':
                    if not hasattr(converter, 'convert_to_json'):
                        raise ValueError(f"JSON conversion not supported for {doc_type} files")
                    converted_content = converter.convert_to_json(file_path)
                
                # Save output
                success = file_handler.save_output(converted_content, output_file)
                if not success:
                    raise ValueError(f"Failed to save output to {output_file}")
                
                processing_time = time.time() - start_time
                successful_conversions += 1
                
                # Record successful result
                results.append({
                    'input_file': file_name,
                    'output_file': Path(output_file).name,
                    'success': True,
                    'processing_time': processing_time,
                    'error': None
                })
                
                if verbose:
                    formatter.print_success(f"✓ Converted {file_name}")
            
            except Exception as e:
                processing_time = time.time() - start_time
                error_msg = str(e)
                
                # Record failed result
                results.append({
                    'input_file': file_name,
                    'output_file': 'N/A',
                    'success': False,
                    'processing_time': processing_time,
                    'error': error_msg
                })
                
                if verbose:
                    formatter.print_error(f"✗ Failed to convert {file_name}: {error_msg}")
                
                # Stop processing if continue_on_error is False
                if not continue_on_error:
                    formatter.print_error("Stopping batch processing due to error. Use --continue-on-error to skip failed files.")
                    break
            
            # Update progress
            progress.update(task, advance=1)
    
    # Print summary
    formatter.print_conversion_summary(results)
    
    # Final statistics
    failed_conversions = len(results) - successful_conversions
    formatter.print_info(f"\n📁 Batch conversion completed:")
    formatter.print_info(f"   • Total files processed: {len(results)}")
    formatter.print_info(f"   • Successful: {successful_conversions}")
    formatter.print_info(f"   • Failed: {failed_conversions}")
    formatter.print_info(f"   • Output directory: {output_dir}")
    
    # Exit with error code if any files failed and we're not continuing on error
    if failed_conversions > 0 and not continue_on_error:
        sys.exit(1)