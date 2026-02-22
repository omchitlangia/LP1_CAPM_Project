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

# Asset names (match column names from data)
ASSETS = ["Msft", "GE", "Ford"]
MARKET_TICKER = "SP500"
RISK_FREE_TICKER = "Tbill"

# Column name patterns
CLOSE_PREFIX = "Close"
EXCESS_SUFFIX = "Excess"


def ensure_dirs():
    """Ensure all required directories exist."""
    for path in [FIG_DIR, TABLE_DIR]:
        path.mkdir(parents=True, exist_ok=True)
