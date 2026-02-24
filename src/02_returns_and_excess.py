"""
Compute log returns, simple returns, and excess returns for CAPM analysis.

Implements the core CAPM formulas for both return types:

LOG RETURNS:
- Daily log returns: R_log,t = ln(P_t / P_{t-1})
- Daily risk-free: Rf_daily = (Tbill/100)/252
- Excess: R*_t = R_t − Rf_daily
- CAPM: R*_i = alpha + beta * R*_m + error

SIMPLE RETURNS:
- Daily simple returns: R_simple,t = (P_t / P_{t-1}) − 1
- Excess simple: R_simple* = R_simple − Rf_daily (same rf)
- CAPM_simple: R_simple,i* = alpha + beta * R_simple,m* + error
"""

import pandas as pd
import numpy as np
from pathlib import Path
import importlib
import sys

# Handle imports - support both module and direct execution
src_path = Path(__file__).parent.absolute()
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

try:
    config = importlib.import_module('00_config')
    ASSETS = config.ASSETS
    MARKET_TICKER = config.MARKET_TICKER
    RISK_FREE_TICKER = config.RISK_FREE_TICKER
    TRADING_DAYS = config.TRADING_DAYS
    TABLE_DIR = config.TABLE_DIR
    should_generate = config.should_generate
except (ImportError, ModuleNotFoundError):
    # Fallback defaults
    ASSETS = ["MSFT", "GE", "FORD"]
    MARKET_TICKER = "SP500"
    RISK_FREE_TICKER = "Tbill"
    TRADING_DAYS = 252
    TABLE_DIR = Path(__file__).parent.parent / "report" / "tables"
    
    def should_generate(path, force=False):
        return force or not path.exists()


def compute_log_returns(df: pd.DataFrame, price_cols: list) -> pd.DataFrame:
    """
    Compute daily log returns for given columns.
    
    Formula: R_log,t = ln(P_t / P_{t-1})
    
    Args:
        df: Input DataFrame with price columns
        price_cols: List of price column names
        
    Returns:
        DataFrame with log return columns added (column names: {col}_Return_LOG)
    """
    df = df.copy()
    for col in price_cols:
        if col in df.columns:
            df[f"{col}_Return_LOG"] = np.log(df[col] / df[col].shift(1))
    return df


def compute_simple_returns(df: pd.DataFrame, price_cols: list) -> pd.DataFrame:
    """
    Compute daily simple returns for given columns.
    
    Formula: R_simple,t = (P_t / P_{t-1}) − 1
    
    Args:
        df: Input DataFrame with price columns
        price_cols: List of price column names
        
    Returns:
        DataFrame with simple return columns added (column names: {col}_Return_SIMPLE)
    """
    df = df.copy()
    for col in price_cols:
        if col in df.columns:
            df[f"{col}_Return_SIMPLE"] = (df[col] / df[col].shift(1)) - 1
    return df


def compute_daily_risk_free_rate(df: pd.DataFrame, rf_col: str, trading_days: int = 252) -> pd.DataFrame:
    """
    Compute daily risk-free rate from annualized T-bill rate.
    
    Formula: Rf_daily = (Tbill/100) / trading_days
    
    Args:
        df: Input DataFrame
        rf_col: Name of T-bill rate column (annualized percentage)
        trading_days: Number of trading days per year
        
    Returns:
        DataFrame with daily risk-free rate column added
    """
    df = df.copy()
    if rf_col in df.columns:
        df['Rf_daily'] = (df[rf_col] / 100) / trading_days
    return df


def compute_excess_returns(df: pd.DataFrame, return_cols: list, rf_col: str = 'Rf_daily', 
                          return_type: str = 'LOG') -> pd.DataFrame:
    """
    Compute excess returns for given return columns.
    
    Formula: R_excess = R_asset - Rf_daily
    
    Args:
        df: Input DataFrame with return columns and risk-free rate
        return_cols: List of return column names (can be _LOG or _SIMPLE suffixed)
        rf_col: Name of risk-free rate column
        return_type: 'LOG' or 'SIMPLE' indicating the return type
        
    Returns:
        DataFrame with excess return columns added
    """
    df = df.copy()
    if rf_col not in df.columns:
        raise ValueError(f"Risk-free rate column '{rf_col}' not found")
    
    for col in return_cols:
        if col in df.columns:
            # Clean up the column name to get the base asset name
            base_name = col.replace('_Return_LOG', '').replace('_Return_SIMPLE', '')
            
            # Create excess return column names based on return type
            if return_type.upper() == 'LOG':
                # For log returns, use simple name for backward compatibility
                excess_col = f"{base_name}_Excess"
            else:  # SIMPLE
                # For simple returns, use distinctive name
                excess_col = f"{base_name}_Excess_SIMPLE"
            
            df[excess_col] = df[col] - df[rf_col]
    
    return df


def compute_returns_and_excess(df: pd.DataFrame, 
                               assets: list = ASSETS,
                               market: str = MARKET_TICKER,
                               risk_free: str = RISK_FREE_TICKER,
                               save_intermediate: bool = True) -> pd.DataFrame:
    """
    Main function: compute all returns (log and simple) and excess returns.
    
    Returns naming scheme:
    - Log returns: {ASSET}_Return_LOG -> {ASSET}_Excess (backward compatible)
    - Simple returns: {ASSET}_Return_SIMPLE -> {ASSET}_Excess_SIMPLE
    
    Args:
        df: Input DataFrame with prices and T-bill rate
        assets: List of asset tickers
        market: Market ticker
        risk_free: Risk-free rate ticker (T-bill)
        save_intermediate: If True, save intermediate excess returns CSVs
        
    Returns:
        DataFrame with all returns and excess returns added
    """
    df = df.copy()
    
    # All price columns to process
    all_prices = [market] + assets
    
    # Compute daily risk-free rate (shared by both return types)
    print("Computing daily risk-free rate...")
    df = compute_daily_risk_free_rate(df, risk_free, TRADING_DAYS)
    
    # === LOG RETURNS ===
    print("Computing log returns...")
    df = compute_log_returns(df, all_prices)
    
    # Compute excess log returns (keep backward-compatible column names)
    print("Computing excess log returns...")
    return_cols_log = [f"{ticker}_Return_LOG" for ticker in all_prices]
    df = compute_excess_returns(df, return_cols_log, 'Rf_daily', return_type='LOG')
    
    # === SIMPLE RETURNS ===
    print("Computing simple returns...")
    df = compute_simple_returns(df, all_prices)
    
    # Compute excess simple returns (use _SIMPLE suffix in column names)
    print("Computing excess simple returns...")
    return_cols_simple = [f"{ticker}_Return_SIMPLE" for ticker in all_prices]
    df = compute_excess_returns(df, return_cols_simple, 'Rf_daily', return_type='SIMPLE')
    
    # Drop first row (NaN from shift)
    df = df.iloc[1:].reset_index(drop=True)
    
    # Save intermediate excess returns CSVs if requested
    if save_intermediate:
        # Extract and save excess log returns
        excess_cols_log = [col for col in df.columns if col.endswith('_Excess') and not col.endswith('_Excess_SIMPLE')]
        if excess_cols_log:
            excess_log_path = TABLE_DIR / 'capm_excess_log.csv'
            if should_generate(excess_log_path):
                cols_to_save = ['Date'] + excess_cols_log
                df[cols_to_save].to_csv(excess_log_path, index=False)
                print(f"  ✓ Saved: {excess_log_path}")
        
        # Extract and save excess simple returns
        excess_cols_simple = [col for col in df.columns if col.endswith('_Excess_SIMPLE')]
        if excess_cols_simple:
            excess_simple_path = TABLE_DIR / 'capm_excess_simple.csv'
            if should_generate(excess_simple_path):
                cols_to_save = ['Date'] + excess_cols_simple
                df[cols_to_save].to_csv(excess_simple_path, index=False)
                print(f"  ✓ Saved: {excess_simple_path}")
    
    print(f"Data shape after returns computation: {df.shape}")
    return df


def main():
    """Run returns computation pipeline."""
    from importlib import import_module
    load_and_clean = import_module('01_load_and_clean').load_and_clean
    
    df = load_and_clean(source="csv")
    df = compute_returns_and_excess(df)
    
    print("\n=== Computed Returns ===")
    display_cols = ['Date', 'MSFT_Return_LOG', 'SP500_Return_LOG', 'Rf_daily', 
                    'MSFT_Excess', 'SP500_Excess', 'MSFT_Excess_SIMPLE', 'SP500_Excess_SIMPLE']
    available_cols = [c for c in display_cols if c in df.columns]
    print(df[available_cols].head(10))
    
    return df


if __name__ == "__main__":
    main()

