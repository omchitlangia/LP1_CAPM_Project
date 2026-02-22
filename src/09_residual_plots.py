"""
Residual diagnostic plots for CAPM regression analysis.

Generates four types of plots for each asset:
1. Residuals over time
2. Residuals vs fitted values
3. Q-Q plot for normality
4. ACF plot for autocorrelation
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
from statsmodels.graphics.gofplots import qqplot
from statsmodels.graphics.tsaplots import plot_acf
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
    FIG_DIR = config.FIG_DIR
except (ImportError, ModuleNotFoundError):
    ASSETS = ["Msft", "GE", "Ford"]
    MARKET_TICKER = "SP500"
    FIG_DIR = Path(__file__).parent.parent / "report" / "figures"


def create_residuals_timeseries_plot(df: pd.DataFrame, asset: str, 
                                     market: str, output_path: Path) -> Path:
    """
    Create residuals vs time plot.
    
    Args:
        df: DataFrame with returns and date
        asset: Asset name
        market: Market ticker
        output_path: Path to save plot
        
    Returns:
        Path to saved plot
    """
    y = df[f'{asset}_Excess']
    X = sm.add_constant(df[f'{market}_Excess'])
    model = sm.OLS(y, X).fit()
    residuals = model.resid
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df.index, residuals, linewidth=0.8, color='steelblue', alpha=0.7)
    ax.axhline(y=0, color='red', linestyle='--', linewidth=1)
    ax.set_xlabel('Time', fontsize=10)
    ax.set_ylabel('Residuals', fontsize=10)
    ax.set_title(f'{asset.upper()} - Residuals Over Time', fontsize=11, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    return output_path


def create_residuals_vs_fitted_plot(df: pd.DataFrame, asset: str, 
                                    market: str, output_path: Path) -> Path:
    """
    Create residuals vs fitted values plot.
    
    Args:
        df: DataFrame with returns
        asset: Asset name
        market: Market ticker
        output_path: Path to save plot
        
    Returns:
        Path to saved plot
    """
    y = df[f'{asset}_Excess']
    X = sm.add_constant(df[f'{market}_Excess'])
    model = sm.OLS(y, X).fit()
    residuals = model.resid
    fitted = model.fittedvalues
    
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.scatter(fitted, residuals, alpha=0.5, s=20, color='steelblue')
    ax.axhline(y=0, color='red', linestyle='--', linewidth=1.5)
    ax.set_xlabel('Fitted Values', fontsize=10)
    ax.set_ylabel('Residuals', fontsize=10)
    ax.set_title(f'{asset.upper()} - Residuals vs Fitted Values', fontsize=11, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    return output_path


def create_qqplot(df: pd.DataFrame, asset: str, 
                  market: str, output_path: Path) -> Path:
    """
    Create Q-Q plot for normality assessment.
    
    Args:
        df: DataFrame with returns
        asset: Asset name
        market: Market ticker
        output_path: Path to save plot
        
    Returns:
        Path to saved plot
    """
    y = df[f'{asset}_Excess']
    X = sm.add_constant(df[f'{market}_Excess'])
    model = sm.OLS(y, X).fit()
    residuals = model.resid
    
    fig, ax = plt.subplots(figsize=(8, 6))
    qqplot(residuals, line='45', ax=ax, markersize=4)
    ax.set_title(f'{asset.upper()} - Q-Q Plot', fontsize=11, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    return output_path


def create_acf_plot(df: pd.DataFrame, asset: str, 
                    market: str, output_path: Path, nlags: int = 30) -> Path:
    """
    Create autocorrelation function plot.
    
    Args:
        df: DataFrame with returns
        asset: Asset name
        market: Market ticker
        output_path: Path to save plot
        nlags: Number of lags to display (default: 30)
        
    Returns:
        Path to saved plot
    """
    y = df[f'{asset}_Excess']
    X = sm.add_constant(df[f'{market}_Excess'])
    model = sm.OLS(y, X).fit()
    residuals = model.resid
    
    fig, ax = plt.subplots(figsize=(10, 5))
    plot_acf(residuals, lags=nlags, ax=ax, alpha=0.05)
    ax.set_title(f'{asset.upper()} - Autocorrelation Function (ACF)', fontsize=11, fontweight='bold')
    ax.set_xlabel('Lag', fontsize=10)
    ax.set_ylabel('ACF', fontsize=10)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    return output_path


def create_all_residual_plots(df: pd.DataFrame, 
                             assets: list = ASSETS,
                             market: str = MARKET_TICKER,
                             fig_dir: Path = FIG_DIR) -> list:
    """
    Create all residual diagnostic plots for all assets.
    
    Args:
        df: DataFrame with returns and excess returns
        assets: List of asset tickers
        market: Market ticker
        fig_dir: Directory to save plots
        
    Returns:
        List of saved plot paths
    """
    plot_paths = []
    
    print("\n=== RESIDUAL DIAGNOSTIC PLOTS ===\n")
    
    for asset in assets:
        print(f"{asset.upper()}")
        
        # Time series plot
        ts_path = fig_dir / f"{asset.upper()}_residuals_timeseries.png"
        create_residuals_timeseries_plot(df, asset, market, ts_path)
        plot_paths.append(ts_path)
        print(f"  ✓ Saved: {ts_path.name}")
        
        # Residuals vs fitted plot
        fit_path = fig_dir / f"{asset.upper()}_residuals_vs_fitted.png"
        create_residuals_vs_fitted_plot(df, asset, market, fit_path)
        plot_paths.append(fit_path)
        print(f"  ✓ Saved: {fit_path.name}")
        
        # Q-Q plot
        qq_path = fig_dir / f"{asset.upper()}_qqplot.png"
        create_qqplot(df, asset, market, qq_path)
        plot_paths.append(qq_path)
        print(f"  ✓ Saved: {qq_path.name}")
        
        # ACF plot
        acf_path = fig_dir / f"{asset.upper()}_residuals_acf.png"
        create_acf_plot(df, asset, market, acf_path, nlags=30)
        plot_paths.append(acf_path)
        print(f"  ✓ Saved: {acf_path.name}")
    
    return plot_paths


def main():
    """Run residual plots pipeline."""
    from load_and_clean import load_and_clean
    from returns_and_excess import compute_returns_and_excess
    
    df = load_and_clean(source="csv")
    df = compute_returns_and_excess(df)
    
    plot_paths = create_all_residual_plots(df)
    
    print(f"\n✓ Generated {len(plot_paths)} residual diagnostic plots")
    
    return plot_paths


if __name__ == "__main__":
    main()
