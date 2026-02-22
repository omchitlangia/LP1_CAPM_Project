#!/usr/bin/env python3
"""
Submission packager script for LP1 CAPM project.

Creates a zip file containing all project files and folders for submission.
Excludes: venv/, __pycache__/, .ipynb_checkpoints/, .DS_Store
"""

import os
import zipfile
from pathlib import Path
from typing import List, Tuple

# Root directory (where this script is located)
ROOT_DIR = Path(__file__).parent.absolute()

# Files and folders to include
INCLUDE_ITEMS = [
    'report',
    'src',
    'data',
    'notebooks',
    'README.md',
    'requirements.txt',
    '.gitignore',
]

# Patterns to exclude
EXCLUDE_PATTERNS = [
    'venv',
    '__pycache__',
    '.ipynb_checkpoints',
    '.DS_Store',
    '*.pyc',
    '.git',
]

# Output zip file
ZIP_FILENAME = 'LP1_submission.zip'


def should_exclude(path: Path) -> bool:
    """Check if a path should be excluded from the zip."""
    path_str = str(path)
    
    # Check against exclude patterns
    for pattern in EXCLUDE_PATTERNS:
        if pattern in path_str or path.name == pattern:
            return True
    
    return False


def collect_files(root: Path, include_items: List[str]) -> List[Tuple[Path, str]]:
    """
    Recursively collect files to include in the zip.
    
    Args:
        root: Root directory
        include_items: List of items (files/folders) to include
        
    Returns:
        List of (file_path, arcname) tuples for zip
    """
    files = []
    
    for item_name in include_items:
        item_path = root / item_name
        
        if not item_path.exists():
            print(f"⚠ Warning: {item_name} not found, skipping")
            continue
        
        if item_path.is_file():
            # Single file
            if not should_exclude(item_path):
                arcname = str(item_path.relative_to(root))
                files.append((item_path, arcname))
        
        elif item_path.is_dir():
            # Directory - recursively add files
            for file_path in item_path.rglob('*'):
                if file_path.is_file() and not should_exclude(file_path):
                    arcname = str(file_path.relative_to(root))
                    files.append((file_path, arcname))
    
    return files


def create_submission_zip(root: Path, include_items: List[str], 
                         zip_filename: str) -> Tuple[Path, int, float]:
    """
    Create a zip file with specified contents.
    
    Args:
        root: Root directory
        include_items: List of items to include
        zip_filename: Name of the zip file to create
        
    Returns:
        Tuple of (zip_path, file_count, zip_size_mb)
    """
    zip_path = root / zip_filename
    
    # Check if zip already exists and remove it
    if zip_path.exists():
        print(f"Removing existing {zip_filename}...")
        zip_path.unlink()
    
    # Collect files
    print(f"Scanning files to include...")
    files = collect_files(root, include_items)
    
    if not files:
        raise ValueError("No files found to include in zip")
    
    # Create zip
    print(f"Creating {zip_filename}...")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path, arcname in files:
            zf.write(file_path, arcname=arcname)
    
    # Calculate size
    zip_size_bytes = zip_path.stat().st_size
    zip_size_mb = zip_size_bytes / (1024 * 1024)
    
    return zip_path, len(files), zip_size_mb


def main():
    """Main execution."""
    print("=" * 80)
    print("LP1 CAPM PROJECT - SUBMISSION PACKAGER")
    print("=" * 80)
    
    try:
        # Create zip
        zip_path, file_count, zip_size_mb = create_submission_zip(
            ROOT_DIR, 
            INCLUDE_ITEMS, 
            ZIP_FILENAME
        )
        
        # Print summary
        print("\n" + "=" * 80)
        print("SUBMISSION PACKAGE CREATED SUCCESSFULLY")
        print("=" * 80)
        
        print(f"\nZip File Path: {zip_path}")
        print(f"Total Files Included: {file_count}")
        print(f"Zip File Size: {zip_size_mb:.2f} MB ({zip_path.stat().st_size:,} bytes)")
        
        print("\nIncluded Items:")
        for item in INCLUDE_ITEMS:
            item_path = ROOT_DIR / item
            if item_path.exists():
                print(f"  ✓ {item}")
            else:
                print(f"  ✗ {item} (not found)")
        
        print("\nExcluded Patterns:")
        for pattern in EXCLUDE_PATTERNS:
            print(f"  • {pattern}")
        
        print("\n" + "=" * 80)
        print("Ready for submission!")
        print("=" * 80 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
