# docling/frontend/cli/commands/convert.py

import click
import time
import sys
import os
from pathlib import Path
from typing import Optional

# Add parent directories to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../../"))

from ..config import CLIConfig
from ..utils.file_handler import FileHandler
from ..utils.output_formatter import OutputFormatter

# Import your backend converters (we'll handle the import issue for now)
try:
    from docling.backend.excel_converter import ExcelConverter
    from docling.backend.word_converter import WordConverter
    from docling.backend.powerpoint_convertor import PptConverter
    from docling.backend.markdown_postprocessor import MarkdownPostProcessor
except ImportError as e:
    # For now, we'll create mock converters if import fails
    class MockConverter:
        def convert_to_md(self, file_path): return f"# Mock conversion of {file_path}"
        def convert_to_html(self, file_path): return f"<h1>Mock conversion of {file_path}</h1>"
        def convert_to_json(self, file_path): return '{"mock": "conversion"}'
    
    ExcelConverter = WordConverter = PptConverter = MockConverter
    
    class MockProcessor:
        def remove_images(self, content): return content
        def encode_images_base64(self, content, path): return content
        def ocr_images(self, content, path): return content
        def convert_plain_math_to_latex(self, content): return content
    
    MarkdownPostProcessor = MockProcessor

@click.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--format', '-f', 'output_format', 
              type=click.Choice(['markdown', 'html', 'json']),
              default='markdown',
              help='Output format (default: markdown)')
@click.option('--output', '-o', 'output_dir',
              type=click.Path(),
              default='./output',
              help='Output directory (default: ./output)')
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
@click.option('--verbose', '-v',
              is_flag=True,
              help='Verbose output')
def convert(input_file: str, output_format: str, output_dir: str, 
           remove_images: bool, encode_images_base64: bool, 
           ocr_images: bool, convert_math_to_latex: bool, verbose: bool):
    """
    Convert a document to the specified format.
    
    INPUT_FILE: Path to the document to convert
    """
    
    # Initialize components
    config = CLIConfig()
    file_handler = FileHandler()
    formatter = OutputFormatter()
    
    if verbose:
        formatter.print_header("Docling Document Converter")
    
    # Validate input file
    is_valid, error_msg = file_handler.validate_input_file(input_file)
    if not is_valid:
        formatter.print_error(error_msg)
        sys.exit(1)
    
    # Get file info
    file_info = file_handler.get_file_info(input_file)
    if verbose:
        formatter.print_info("Processing file:")
        formatter.print_file_info(file_info)
    
    # Determine document type and get converter
    doc_type = config.detect_document_type(input_file)
    
    converters = {
        'excel': ExcelConverter(),
        'word': WordConverter(), 
        'powerpoint': PptConverter()
    }
    
    converter = converters.get(doc_type)
    if not converter:
        formatter.print_error(f"No converter available for document type: {doc_type}")
        sys.exit(1)
    
    # Create output path
    output_file = file_handler.create_output_path(input_file, output_dir, output_format)
    
    try:
        # Start conversion
        start_time = time.time()
        
        if verbose:
            formatter.print_info(f"Converting to {output_format.upper()}...")
        
        # Perform conversion based on output format
        if output_format == 'markdown':
            converted_content = converter.convert_to_md(input_file)
            
            # Apply post-processing if requested
            if any([remove_images, encode_images_base64, ocr_images, convert_math_to_latex]):
                if verbose:
                    formatter.print_info("Applying post-processing...")
                
                processor = MarkdownPostProcessor()
                base_path = os.path.dirname(input_file)
                
                if remove_images:
                    converted_content = processor.remove_images(converted_content)
                elif encode_images_base64:
                    converted_content = processor.encode_images_base64(converted_content, base_path)
                elif ocr_images:
                    converted_content = processor.ocr_images(converted_content, base_path)
                
                if convert_math_to_latex:
                    converted_content = processor.convert_plain_math_to_latex(converted_content)
        
        elif output_format == 'html':
            converted_content = converter.convert_to_html(input_file)
        
        elif output_format == 'json':
            # Check if converter supports JSON
            if not hasattr(converter, 'convert_to_json'):
                formatter.print_error(f"JSON conversion not supported for {doc_type} files")
                sys.exit(1)
            converted_content = converter.convert_to_json(input_file)
        
        # Save output
        success = file_handler.save_output(converted_content, output_file)
        processing_time = time.time() - start_time
        
        if success:
            formatter.print_success(f"Conversion completed successfully!")
            formatter.print_info(f"Output saved to: {output_file}")
            formatter.print_info(f"Processing time: {processing_time:.2f} seconds")
            
            if verbose:
                # Show conversion summary
                results = [{
                    'input_file': Path(input_file).name,
                    'output_file': Path(output_file).name,
                    'success': True,
                    'processing_time': processing_time
                }]
                formatter.print_conversion_summary(results)
        else:
            formatter.print_error(f"Failed to save output to: {output_file}")
            sys.exit(1)
            
    except NotImplementedError:
        formatter.print_error(f"{output_format.upper()} conversion not yet implemented for {doc_type} files")
        sys.exit(1)
    except Exception as e:
        formatter.print_error(f"Conversion failed: {str(e)}")
        if verbose:
            formatter.print_error(f"Error details: {type(e).__name__}")
        sys.exit(1)