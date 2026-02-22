"""
Compute log returns and excess returns for CAPM analysis.

Implements the core CAPM formulas:
- Daily log returns: R_t = ln(P_t / P_{t-1})
- Daily risk-free: Rf_daily = (Tbill/100)/252
- Excess returns: R_excess = R - Rf_daily
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
except (ImportError, ModuleNotFoundError):
    # Fallback defaults
    ASSETS = ["Msft", "GE", "Ford"]
    MARKET_TICKER = "SP500"
    RISK_FREE_TICKER = "Tbill"
    TRADING_DAYS = 252


def compute_log_returns(df: pd.DataFrame, price_cols: list) -> pd.DataFrame:
    """
    Compute daily log returns for given columns.
    
    Formula: R_t = ln(P_t / P_{t-1})
    
    Args:
        df: Input DataFrame with price columns
        price_cols: List of price column names
        
    Returns:
        DataFrame with log returns columns added
    """
    df = df.copy()
    for col in price_cols:
        if col in df.columns:
            df[f"{col}_Return"] = np.log(df[col] / df[col].shift(1))
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


def compute_excess_returns(df: pd.DataFrame, return_cols: list, rf_col: str = 'Rf_daily') -> pd.DataFrame:
    """
    Compute excess returns for given return columns.
    
    Formula: R_excess = R_asset - Rf_daily
    
    Args:
        df: Input DataFrame with return columns and risk-free rate
        return_cols: List of return column names
        rf_col: Name of risk-free rate column
        
    Returns:
        DataFrame with excess return columns added
    """
    df = df.copy()
    if rf_col not in df.columns:
        raise ValueError(f"Risk-free rate column '{rf_col}' not found")
    
    for col in return_cols:
        if col in df.columns:
            excess_col = col.replace('_Return', '_Excess')
            df[excess_col] = df[col] - df[rf_col]
    
    return df


def compute_returns_and_excess(df: pd.DataFrame, 
                               assets: list = ASSETS,
                               market: str = MARKET_TICKER,
                               risk_free: str = RISK_FREE_TICKER) -> pd.DataFrame:
    """
    Main function: compute all returns and excess returns.
    
    Args:
        df: Input DataFrame with prices and T-bill rate
        assets: List of asset tickers
        market: Market ticker
        risk_free: Risk-free rate ticker (T-bill)
        
    Returns:
        DataFrame with returns and excess returns added
    """
    df = df.copy()
    
    # All price columns to process
    all_prices = [market] + assets
    
    # Compute log returns for all prices
    print("Computing log returns...")
    df = compute_log_returns(df, all_prices)
    
    # Compute daily risk-free rate
    print("Computing daily risk-free rate...")
    df = compute_daily_risk_free_rate(df, risk_free, TRADING_DAYS)
    
    # Compute excess returns (skip the first row which has NaN return)
    print("Computing excess returns...")
    return_cols = [f"{ticker}_Return" for ticker in all_prices]
    df = compute_excess_returns(df, return_cols, 'Rf_daily')
    
    # Drop first row (NaN from shift)
    df = df.iloc[1:].reset_index(drop=True)
    
    print(f"Data shape after returns computation: {df.shape}")
    return df


def main():
    """Run returns computation pipeline."""
    # Import here to avoid circular dependency
    from load_and_clean import load_and_clean
    
    df = load_and_clean(source="csv")
    df = compute_returns_and_excess(df)
    
    print("\n=== Computed Returns ===")
    print(df[['Date', 'Msft_Return', 'SP500_Return', 'Rf_daily', 'Msft_Excess', 'SP500_Excess']].head(10))
    
    return df


if __name__ == "__main__":
    main()
