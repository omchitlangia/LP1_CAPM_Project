"""
Robustness tests and sensitivity analysis for CAPM model.

Implements:
- Subperiod CAPM regressions to test parameter stability
- Rolling-window beta estimation to track systematic risk changes
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
from pathlib import Path
from datetime import datetime
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
    FIG_DIR = config.FIG_DIR
    TABLE_DIR = config.TABLE_DIR
except (ImportError, ModuleNotFoundError):
    ASSETS = ["MSFT", "GE", "FORD"]
    MARKET_TICKER = "SP500"
    FIG_DIR = Path(__file__).parent.parent / "report" / "figures"
    TABLE_DIR = Path(__file__).parent.parent / "report" / "tables"


def run_subperiod_regression(df: pd.DataFrame, 
                              start_date: str, 
                              end_date: str,
                              asset: str,
                              market: str = MARKET_TICKER) -> dict:
    """
    Run CAPM regression for a specific time period.
    
    Args:
        df: DataFrame with excess returns and dates
        start_date: Start date (YYYY-MM-DD format)
        end_date: End date (YYYY-MM-DD format)
        asset: Asset ticker
        market: Market ticker
        
    Returns:
        Dictionary with regression results
    """
    # Filter by date range
    mask = (df['Date'] >= start_date) & (df['Date'] <= end_date)
    df_period = df[mask].copy().reset_index(drop=True)
    
    if len(df_period) < 30:
        # Not enough data for regression
        return {
            'Asset': asset,
            'Period': f"{start_date} to {end_date}",
            'Alpha': np.nan,
            'Alpha_pvalue': np.nan,
            'Beta': np.nan,
            'Beta_pvalue': np.nan,
            'R2': np.nan,
            'N_obs': len(df_period)
        }
    
    # Run OLS regression
    y = df_period[f'{asset}_Excess'].values
    X_market = df_period[f'{market}_Excess'].values
    X = np.column_stack([np.ones(len(y)), X_market])
    
    try:
        model = sm.OLS(y, X).fit()
        
        return {
            'Asset': asset,
            'Period': f"{start_date} to {end_date}",
            'Alpha': model.params[0],
            'Alpha_pvalue': model.pvalues[0],
            'Beta': model.params[1],
            'Beta_pvalue': model.pvalues[1],
            'R2': model.rsquared,
            'N_obs': len(df_period)
        }
    except Exception as e:
        return {
            'Asset': asset,
            'Period': f"{start_date} to {end_date}",
            'Alpha': np.nan,
            'Alpha_pvalue': np.nan,
            'Beta': np.nan,
            'Beta_pvalue': np.nan,
            'R2': np.nan,
            'N_obs': len(df_period)
        }


def run_all_subperiods(df: pd.DataFrame, 
                       assets: list = ASSETS,
                       market: str = MARKET_TICKER) -> pd.DataFrame:
    """
    Run CAPM regressions for predefined subperiods.
    
    Periods:
    - 1993-01-01 to 1997-12-31  (Pre-crash)
    - 1998-01-01 to 2000-12-31  (Dot-com bubble era)
    - 2001-01-01 to 2003-12-31  (Post-crash recovery)
    
    Args:
        df: DataFrame with excess returns and dates
        assets: List of asset tickers
        market: Market ticker
        
    Returns:
        DataFrame with subperiod regression results
    """
    periods = [
        ('1993-01-01', '1997-12-31'),
        ('1998-01-01', '2000-12-31'),
        ('2001-01-01', '2003-12-31'),
    ]
    
    results = []
    
    print("\n=== SUBPERIOD CAPM REGRESSIONS ===\n")
    
    for asset in assets:
        print(f"{asset.upper()}")
        print("-" * 60)
        
        for start_date, end_date in periods:
            result = run_subperiod_regression(df, start_date, end_date, asset, market)
            results.append(result)
            
            print(f"Period {start_date} to {end_date}:")
            print(f"  Beta: {result['Beta']:.4f} (p={result['Beta_pvalue']:.4f})")
            print(f"  Alpha: {result['Alpha']:.6f} (p={result['Alpha_pvalue']:.4f})")
            print(f"  R²: {result['R2']:.4f}, N={result['N_obs']}")
        
        print()
    
    results_df = pd.DataFrame(results)
    
    return results_df


def compute_rolling_beta(df: pd.DataFrame,
                         asset: str,
                         market: str = MARKET_TICKER,
                         window: int = 252) -> pd.Series:
    """
    Compute rolling-window CAPM beta for an asset.
    
    Args:
        df: DataFrame with excess returns and dates
        asset: Asset ticker
        market: Market ticker
        window: Window size in trading days (default: 252 = 1 year)
        
    Returns:
        Series with rolling beta values and dates
    """
    rolling_betas = []
    rolling_dates = []
    
    y = df[f'{asset}_Excess'].values
    X = df[f'{market}_Excess'].values
    dates = df['Date'].values
    
    for i in range(window, len(y)):
        # Extract window data
        y_window = y[i-window:i]
        X_window = X[i-window:i]
        
        # Add constant for intercept
        X_const = np.column_stack([np.ones(window), X_window])
        
        try:
            # Fit OLS
            model = sm.OLS(y_window, X_const).fit()
            beta = model.params[1]
            rolling_betas.append(beta)
            rolling_dates.append(dates[i])
        except Exception:
            rolling_betas.append(np.nan)
            rolling_dates.append(dates[i])
    
    return pd.Series(rolling_betas, index=pd.DatetimeIndex(rolling_dates))


def plot_rolling_beta(rolling_beta: pd.Series,
                      asset: str,
                      output_path: Path = None) -> Path:
    """
    Plot rolling beta series.
    
    Args:
        rolling_beta: Series with rolling beta values
        asset: Asset name
        output_path: Path to save PNG
        
    Returns:
        Path to saved figure
    """
    if output_path is None:
        output_path = FIG_DIR / f"{asset}_rolling_beta.png"
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Plot rolling beta
    ax.plot(rolling_beta.index, rolling_beta.values, linewidth=1.5, color='steelblue', label='Rolling Beta')
    
    # Add reference line at beta=1 (market beta)
    ax.axhline(y=1.0, color='red', linestyle='--', linewidth=1.0, label='Market Beta (β=1.0)', alpha=0.7)
    
    # Labels and formatting
    ax.set_xlabel('Date', fontsize=11)
    ax.set_ylabel(f'{asset} Beta', fontsize=11)
    ax.set_title(f'Rolling 252-Day CAPM Beta - {asset}', fontsize=12, fontweight='bold')
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)
    
    # Rotate x-axis labels
    plt.xticks(rotation=45, ha='right')
    
    # Save figure
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Saved plot: {output_path}")
    
    return output_path


def compute_all_rolling_betas(df: pd.DataFrame,
                              assets: list = ASSETS,
                              market: str = MARKET_TICKER) -> dict:
    """
    Compute rolling betas for all assets and create plots.
    
    Args:
        df: DataFrame with excess returns and dates
        assets: List of asset tickers
        market: Market ticker
        
    Returns:
        Dictionary of rolling beta Series by asset
    """
    rolling_betas = {}
    saved_plots = []
    
    print("\n=== ROLLING BETA ESTIMATION (252-day window) ===\n")
    
    for asset in assets:
        rolling_beta = compute_rolling_beta(df, asset, market, window=252)
        rolling_betas[asset] = rolling_beta
        
        # Plot
        plot_path = plot_rolling_beta(rolling_beta, asset)
        saved_plots.append(plot_path)
    
    return rolling_betas, saved_plots


def save_subperiod_results(subperiod_df: pd.DataFrame, output_file: Path = None) -> Path:
    """
    Save subperiod regression results to CSV.
    
    Args:
        subperiod_df: DataFrame with subperiod results
        output_file: Path to save (default: report/tables/capm_subperiod_results.csv)
        
    Returns:
        Path to saved file
    """
    if output_file is None:
        output_file = TABLE_DIR / "capm_subperiod_results.csv"
    
    output_file.parent.mkdir(parents=True, exist_ok=True)
    subperiod_df.to_csv(output_file, index=False)
    print(f"✓ Subperiod results saved to: {output_file}")
    
    return output_file


def main():
    """Run robustness tests pipeline."""
    from load_and_clean import load_and_clean
    from returns_and_excess import compute_returns_and_excess
    
    df = load_and_clean(source="csv")
    df = compute_returns_and_excess(df)
    
    # Subperiod analysis
    subperiod_df = run_all_subperiods(df)
    save_subperiod_results(subperiod_df)
    
    print("\n=== Subperiod Summary ===")
    print(subperiod_df)
    
    # Rolling beta analysis
    rolling_betas, plots = compute_all_rolling_betas(df)
    
    print(f"\n=== Rolling Beta Summary ===")
    print(f"Generated {len(plots)} rolling beta plots")
    
    return subperiod_df, rolling_betas, plots


if __name__ == "__main__":
    main()
