#!/usr/bin/env python3
# docling-cli.py - Main entry point for Docling CLI

"""
Docling CLI - Document Conversion Tool

A command-line interface for converting Excel, Word, and PowerPoint documents
to various formats using the Docling backend converters.

Usage:
    python docling-cli.py convert document.xlsx
    python docling-cli.py batch ./documents
    python docling-cli.py info --formats
    python docling-cli.py --help
"""

import sys
import os
from pathlib import Path

# Add the docling directory to Python path
script_dir = Path(__file__).parent
docling_dir = script_dir / "docling"
sys.path.insert(0, str(docling_dir))

def check_dependencies():
    """Check if required dependencies are installed"""
    missing_deps = []
    
    try:
        import click
    except ImportError:
        missing_deps.append("click")
    
    try:
        import rich
    except ImportError:
        missing_deps.append("rich")
    
    if missing_deps:
        print("❌ Missing required dependencies:")
        for dep in missing_deps:
            print(f"   • {dep}")
        print("\nInstall with: pip install " + " ".join(missing_deps))
        sys.exit(1)

def main():
    """Main entry point"""
    # Check dependencies first
    check_dependencies()
    
    # Import and run CLI
    try:
        from frontend.cli.main import cli
        cli()
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running from the correct directory and all files are in place.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()