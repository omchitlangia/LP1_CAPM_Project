"""
Data loading and cleaning module for CAPM analysis.

Loads from Excel or CSV, parses dates, cleans column names,
sorts by date, and returns a clean DataFrame ready for analysis.
"""

import pandas as pd
from pathlib import Path
import importlib
import sys

# Handle imports - support both module and direct execution
src_path = Path(__file__).parent.absolute()
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

try:
    config = importlib.import_module('00_config')
    EXCEL_PATH = config.EXCEL_PATH
    CSV_PATH = config.CSV_PATH
except (ImportError, ModuleNotFoundError):
    # Fallback - define paths relative to this file
    src_path = Path(__file__).parent.parent
    EXCEL_PATH = src_path / "data" / "capm_data.xlsx"
    CSV_PATH = src_path / "data" / "findat.csv"


def load_excel(filepath: Path) -> pd.DataFrame:
    """
    Load data from Excel file.
    
    Args:
        filepath: Path to Excel file
        
    Returns:
        DataFrame with data loaded
    """
    df = pd.read_excel(filepath)
    return df


def load_csv(filepath: Path) -> pd.DataFrame:
    """
    Load data from CSV file.
    
    Args:
        filepath: Path to CSV file
        
    Returns:
        DataFrame with data loaded
    """
    df = pd.read_csv(filepath)
    return df


def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove spaces and standardize column names.
    Handle prefixes like "Close-" in findat.csv.
    
    Args:
        df: Input DataFrame
        
    Returns:
        DataFrame with cleaned column names
    """
    # Remove spaces (for xlsx format)
    df.columns = df.columns.str.replace(" ", "", regex=False)
    
    # Handle "Close-ticker" format (from findat.csv)
    df.columns = df.columns.str.replace("Close-", "", regex=False)
    
    # Standardize casing
    df.columns = df.columns.str.capitalize()
    
    # Handle aliases for case-sensitive matching
    col_mapping = {
        'Sp500': 'SP500',
        'Tbill': 'Tbill',
        'Msft': 'Msft',
        'Ge': 'GE', 
        'Ford': 'Ford'
    }
    
    # Rename if matches
    for old, new in col_mapping.items():
        if old in df.columns:
            df = df.rename(columns={old: new})
    
    return df


def parse_dates(df: pd.DataFrame, date_col: str = "Date") -> pd.DataFrame:
    """
    Parse date column to datetime.
    
    Args:
        df: Input DataFrame
        date_col: Name of date column (default: "Date")
        
    Returns:
        DataFrame with parsed dates
    """
    if date_col in df.columns:
        df[date_col] = pd.to_datetime(df[date_col])
    return df


def sort_by_date(df: pd.DataFrame, date_col: str = "Date") -> pd.DataFrame:
    """
    Sort DataFrame by date column.
    
    Args:
        df: Input DataFrame
        date_col: Name of date column (default: "Date")
        
    Returns:
        Sorted DataFrame
    """
    if date_col in df.columns:
        df = df.sort_values(by=date_col).reset_index(drop=True)
    return df


def drop_na_safe(df: pd.DataFrame, how: str = "any") -> pd.DataFrame:
    """
    Drop rows with missing values.
    
    Args:
        df: Input DataFrame
        how: 'any' or 'all' (default: 'any')
        
    Returns:
        DataFrame with NAs removed
    """
    return df.dropna(how=how).reset_index(drop=True)


def load_and_clean(source: str = "csv") -> pd.DataFrame:
    """
    Main function: load and clean data from specified source.
    
    Args:
        source: 'csv' (default) or 'excel'
        
    Returns:
        Clean DataFrame ready for analysis
    """
    if source.lower() == "csv":
        filepath = CSV_PATH
        df = load_csv(filepath)
    elif source.lower() == "excel":
        filepath = EXCEL_PATH
        df = load_excel(filepath)
    else:
        raise ValueError(f"Unknown source: {source}")
    
    print(f"Loaded data from {filepath}")
    print(f"Shape before cleaning: {df.shape}")
    
    df = clean_column_names(df)
    df = parse_dates(df)
    df = sort_by_date(df)
    df = drop_na_safe(df)
    
    print(f"Shape after cleaning: {df.shape}")
    return df


def main():
    """Run load and clean pipeline."""
    df = load_and_clean(source="csv")
    print("\n=== Data Info ===")
    print(df.head())
    print(df.info())
    return df


if __name__ == "__main__":
    main()
