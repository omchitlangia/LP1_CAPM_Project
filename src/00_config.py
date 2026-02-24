"""
Configuration and constants for CAPM LP1 analysis.

Defines paths, asset names, and key parameters.
"""

from pathlib import Path

# Root directory (parent of src/)
ROOT_DIR = Path(__file__).parent.parent

# Data directory
DATA_DIR = ROOT_DIR / "data"

# Report directory
REPORT_DIR = ROOT_DIR / "report"
FIG_DIR = REPORT_DIR / "figures"
TABLE_DIR = REPORT_DIR / "tables"

# Data sources
EXCEL_PATH = DATA_DIR / "capm_data.xlsx"
CSV_PATH = DATA_DIR / "findat.csv"

# Analysis constants
TRADING_DAYS = 252
SIGNIFICANCE_LEVEL = 0.05
HAC_LAGS = 10  # Newey-West HAC lag length

# Asset names (standardized to uppercase)
ASSETS = ["MSFT", "GE", "FORD"]
MARKET_TICKER = "SP500"
RISK_FREE_TICKER = "Tbill"

# Column name patterns
CLOSE_PREFIX = "Close"
EXCESS_SUFFIX = "Excess"

# Build control flag (set to True to force regeneration of all outputs)
FORCE_REBUILD = False


def ensure_dirs():
    """Ensure all required directories exist."""
    for path in [FIG_DIR, TABLE_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def file_exists(path: Path) -> bool:
    """
    Check if a file exists.
    
    Args:
        path: Path to file
        
    Returns:
        True if file exists, False otherwise
    """
    return Path(path).exists() and Path(path).is_file()


def should_generate(output_path: Path, force: bool = None) -> bool:
    """
    Determine whether an output should be generated.
    
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
