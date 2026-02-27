"""
Utilities for file I/O operations.

Provides helper functions for managing output files, aliasing, and caching.
"""

import shutil
from pathlib import Path
import importlib
import sys

# Import config utilities
src_path = Path(__file__).parent.absolute()
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

try:
    config = importlib.import_module('00_config')
    FORCE_REBUILD = config.FORCE_REBUILD
except (ImportError, ModuleNotFoundError):
    FORCE_REBUILD = False


def ensure_alias_output(src_path: Path, dst_path: Path, force: bool = None) -> bool:
    """
    Copy source file to destination if destination doesn't exist.
    
    Useful for aliasing outputs (e.g., copying full-period results from
    general regression results when full-period file doesn't exist).
    
    Args:
        src_path: Source file path
        dst_path: Destination file path
        force: If True, always copy even if destination exists. 
               If None, uses FORCE_REBUILD from config.
        
    Returns:
        True if file was copied, False if destination already existed
        
    Raises:
        FileNotFoundError: If source file doesn't exist
    """
    src_path = Path(src_path)
    dst_path = Path(dst_path)
    
    if force is None:
        force = FORCE_REBUILD
    
    # Check if source exists
    if not src_path.exists():
        raise FileNotFoundError(f"Source file not found: {src_path}")
    
    # Ensure destination directory exists
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Copy if destination doesn't exist or force=True
    if force or not dst_path.exists():
        shutil.copy2(src_path, dst_path)
        return True
    
    return False


def file_exists(path: Path) -> bool:
    """
    Check if a file exists and is a file (not a directory).
    
    Args:
        path: Path to check
        
    Returns:
        True if path exists and is a file
    """
    p = Path(path)
    return p.exists() and p.is_file()


def should_generate(output_path: Path, force: bool = None) -> bool:
    """
    Determine whether an output file should be generated.
    
    Args:
        output_path: Path to output file
        force: Override FORCE_REBUILD flag (if None, uses config value)
        
    Returns:
        True if file should be generated, False if it already exists
    """
    if force is None:
        force = FORCE_REBUILD
    
    # Always generate if force flag is True
    if force:
        return True
    
    # Generate if file doesn't exist
    return not file_exists(output_path)
