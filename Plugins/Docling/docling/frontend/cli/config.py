# docling/frontend/cli/config.py

from dataclasses import dataclass
from typing import Dict, List
from pathlib import Path

@dataclass
class CLIConfig:
    """Configuration settings for Docling CLI"""
    
    # Supported file extensions
    SUPPORTED_EXTENSIONS = {
        'excel': ['.xlsx', '.xls'],
        'word': ['.docx', '.doc'],
        'powerpoint': ['.pptx', '.ppt']
    }
    
    # Output formats
    OUTPUT_FORMATS = ['markdown', 'html', 'json']
    
    # Default settings
    DEFAULT_OUTPUT_FORMAT = 'markdown'
    DEFAULT_OUTPUT_DIR = './output'
    MAX_FILE_SIZE_MB = 100
    
    # Post-processing options
    POST_PROCESSING_OPTIONS = [
        'remove-images',
        'encode-images-base64', 
        'ocr-images',
        'convert-math-to-latex'
    ]
    
    # CLI styling
    SUCCESS_COLOR = 'green'
    ERROR_COLOR = 'red'
    WARNING_COLOR = 'yellow'
    INFO_COLOR = 'blue'
    
    @classmethod
    def get_all_supported_extensions(cls) -> List[str]:
        """Get all supported file extensions as a flat list"""
        extensions = []
        for doc_type, exts in cls.SUPPORTED_EXTENSIONS.items():
            extensions.extend(exts)
        return extensions
    
    @classmethod
    def detect_document_type(cls, file_path: str) -> str:
        """Detect document type from file extension"""
        file_ext = Path(file_path).suffix.lower()
        
        for doc_type, extensions in cls.SUPPORTED_EXTENSIONS.items():
            if file_ext in extensions:
                return doc_type
        
        return 'unknown'
    
    @classmethod
    def is_supported_file(cls, file_path: str) -> bool:
        """Check if file is supported"""
        return Path(file_path).suffix.lower() in cls.get_all_supported_extensions()