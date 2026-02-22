"""
Descriptive statistics for excess returns.

Computes summary statistics (mean, std, min, max, skew, kurtosis) for:
- Market excess returns
- Asset excess returns (MSFT, GE, FORD)
"""

import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path
import importlib
import sys

# Handle imports
src_path = Path(__file__).parent.absolute()
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

try:
    config = importlib.import_module('00_config')
    ASSETS = config.ASSETS
    MARKET_TICKER = config.MARKET_TICKER
    TABLE_DIR = config.TABLE_DIR
except (ImportError, ModuleNotFoundError):
    ASSETS = ["Msft", "GE", "Ford"]
    MARKET_TICKER = "SP500"
    TABLE_DIR = Path(__file__).parent.parent / "report" / "tables"


def compute_series_stats(series: pd.Series, series_name: str) -> dict:
    """
    Compute descriptive statistics for a single series.
    
    Args:
        series: Series of returns (excess returns)
        series_name: Label for the series (e.g., "MSFT", "Market")
        
    Returns:
        Dictionary with statistics
    """
    # Remove NaN values
    clean_series = series.dropna()
    
    stats_dict = {
        'Series': series_name,
        'N': len(clean_series),
        'Mean': clean_series.mean(),
        'Std': clean_series.std(),
        'Min': clean_series.min(),
        'Max': clean_series.max(),
        'Skew': clean_series.skew(),
        'Kurtosis': clean_series.kurtosis(),
    }
    
    return stats_dict


def compute_all_descriptive_stats(df: pd.DataFrame, 
                                   assets: list = ASSETS,
                                   market: str = MARKET_TICKER) -> pd.DataFrame:
    """
    Compute descriptive statistics for all assets and market.
    
    Args:
        df: DataFrame with excess returns columns
        assets: List of asset names
        market: Market ticker name
        
    Returns:
        DataFrame with descriptive statistics
    """
    results = []
    
    print("\n=== DESCRIPTIVE STATISTICS ===\n")
    
    # Market excess returns
    market_excess = df[f'{market}_Excess']
    market_stats = compute_series_stats(market_excess, f'{market.upper()}')
    results.append(market_stats)
    
    # Asset excess returns
    for asset in assets:
        asset_excess = df[f'{asset}_Excess']
        asset_stats = compute_series_stats(asset_excess, asset.upper())
        results.append(asset_stats)
    
    stats_df = pd.DataFrame(results)
    
    # Print summary
    print(stats_df.to_string(index=False))
    
    return stats_df


def save_descriptive_stats(stats_df: pd.DataFrame, 
                          output_file: Path = None) -> Path:
    """
    Save descriptive statistics to CSV file.
    
    Args:
        stats_df: DataFrame with descriptive statistics
        output_file: Path to save CSV (default: report/tables/descriptive_stats.csv)
        
    Returns:
        Path to saved file
    """
    if output_file is None:
        output_file = TABLE_DIR / "descriptive_stats.csv"
    
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Select columns for output
    output_df = stats_df[['Series', 'N', 'Mean', 'Std', 'Min', 'Max', 'Skew', 'Kurtosis']].copy()
    output_df.to_csv(output_file, index=False)
    print(f"\n✓ Descriptive statistics saved to: {output_file}")
    
    return output_file


def main():
    """Run descriptive statistics pipeline."""
    from load_and_clean import load_and_clean
    from returns_and_excess import compute_returns_and_excess
    
    df = load_and_clean(source="csv")
    df = compute_returns_and_excess(df)
    
    stats_df = compute_all_descriptive_stats(df)
    save_descriptive_stats(stats_df)
    
    return stats_df


if __name__ == "__main__":
    main()
