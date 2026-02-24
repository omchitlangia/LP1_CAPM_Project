"""
Residual histogram plots for CAPM validation.

Generates residual distribution histograms for each asset and return type:
- 50 bins per histogram
- Vertical line at zero (mean residual)
- Optional normal distribution overlay
- Saves to report/figures/{ASSET}_residual_hist_{RETURN_TYPE}.png
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from scipy import stats
import statsmodels.api as sm
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
    should_generate = config.should_generate
except (ImportError, ModuleNotFoundError):
    ASSETS = ["MSFT", "GE", "FORD"]
    MARKET_TICKER = "SP500"
    FIG_DIR = Path(__file__).parent.parent / "report" / "figures"
    
    def should_generate(path, force=False):
        return force or not path.exists()


def create_residual_histogram(residuals: np.ndarray, asset: str, return_type: str,
                             overlay_normal: bool = True) -> plt.Figure:
    """
    Create histogram of residuals with optional normal distribution overlay.
    
    Args:
        residuals: Array of residuals from CAPM regression
        asset: Asset name (e.g., 'MSFT')
        return_type: 'LOG' or 'SIMPLE'
        overlay_normal: If True, overlay normal distribution PDF
        
    Returns:
        Matplotlib figure object
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Create histogram
    ax.hist(residuals, bins=50, density=False, alpha=0.7, color='steelblue', edgecolor='black')
    
    # Add vertical line at zero
    ax.axvline(x=0, color='red', linestyle='--', linewidth=2, label='Zero')
    
    # Overlay normal distribution (optional)
    if overlay_normal:
        mu, sigma = np.mean(residuals), np.std(residuals)
        x = np.linspace(mu - 4*sigma, mu + 4*sigma, 100)
        # Scale the normal PDF to match histogram counts
        n_samples = len(residuals)
        bin_width = (residuals.max() - residuals.min()) / 50
        y = (n_samples * bin_width) * stats.norm.pdf(x, mu, sigma)
        ax.plot(x, y, 'darkred', linewidth=2, label='Normal PDF')
        ax.legend()
    
    # Labels and title
    ax.set_xlabel('Residual', fontsize=11)
    ax.set_ylabel('Frequency', fontsize=11)
    ax.set_title(f'{asset} — CAPM Residual Histogram ({return_type})', fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig


def capm_regression_get_residuals(df: pd.DataFrame, asset: str, market_col: str) -> np.ndarray:
    """
    Run CAPM OLS regression and return residuals.
    
    Args:
        df: DataFrame with excess returns
        asset: Asset name
        market_col: Market column name
        
    Returns:
        Array of residuals
    """
    y = df[f'{asset}_Excess'].values
    X = sm.add_constant(df[market_col].values)
    
    try:
        model = sm.OLS(y, X).fit()
        return model.resid
    except Exception as e:
        print(f"  Error fitting CAPM for {asset}: {e}")
        return np.full(len(y), np.nan)


def capm_regression_get_residuals_simple(df: pd.DataFrame, asset: str, market_col: str) -> np.ndarray:
    """
    Run CAPM OLS regression for simple returns and return residuals.
    
    Args:
        df: DataFrame with excess returns
        asset: Asset name
        market_col: Market column name (simple returns)
        
    Returns:
        Array of residuals
    """
    y = df[f'{asset}_Excess_SIMPLE'].values
    X = sm.add_constant(df[market_col].values)
    
    try:
        model = sm.OLS(y, X).fit()
        return model.resid
    except Exception as e:
        print(f"  Error fitting CAPM for {asset} (simple): {e}")
        return np.full(len(y), np.nan)


def create_all_residual_histograms(df: pd.DataFrame, 
                                  assets: list = ASSETS,
                                  market: str = MARKET_TICKER) -> list:
    """
    Create residual histogram plots for all assets and both return types.
    
    Args:
        df: DataFrame with returns and excess returns
        assets: List of asset tickers
        market: Market ticker
        
    Returns:
        List of paths to saved PNG files
    """
    saved_plots = []
    
    # === LOG RETURNS ===
    print("\n=== Creating Residual Histograms: LOG RETURNS ===\n")
    
    market_col_log = f'{market}_Excess'
    
    for asset in assets:
        if f'{asset}_Excess' not in df.columns:
            print(f"  ⚠ Skipping {asset} histogram (no log excess returns)")
            continue
        
        output_path = FIG_DIR / f'{asset}_residual_hist_LOG.png'
        
        if not should_generate(output_path):
            print(f"  ℹ Skipping {asset}_residual_hist_LOG.png (already exists)")
            continue
        
        print(f"Creating histogram for {asset} (LOG)...")
        
        # Get residuals
        residuals = capm_regression_get_residuals(df, asset, market_col_log)
        
        if np.all(np.isnan(residuals)):
            print(f"  ✗ Cannot create histogram (residuals are NaN)")
            continue
        
        # Create and save figure
        fig = create_residual_histogram(residuals, asset, 'LOG')
        fig.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
        
        saved_plots.append(output_path)
        print(f"  ✓ Saved: {output_path}")
    
    # === SIMPLE RETURNS ===
    print("\n=== Creating Residual Histograms: SIMPLE RETURNS ===\n")
    
    market_col_simple = f'{market}_Excess_SIMPLE'
    
    for asset in assets:
        if f'{asset}_Excess_SIMPLE' not in df.columns:
            print(f"  ⚠ Skipping {asset} histogram (no simple excess returns)")
            continue
        
        output_path = FIG_DIR / f'{asset}_residual_hist_SIMPLE.png'
        
        if not should_generate(output_path):
            print(f"  ℹ Skipping {asset}_residual_hist_SIMPLE.png (already exists)")
            continue
        
        print(f"Creating histogram for {asset} (SIMPLE)...")
        
        # Get residuals
        residuals = capm_regression_get_residuals_simple(df, asset, market_col_simple)
        
        if np.all(np.isnan(residuals)):
            print(f"  ✗ Cannot create histogram (residuals are NaN)")
            continue
        
        # Create and save figure
        fig = create_residual_histogram(residuals, asset, 'SIMPLE')
        fig.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
        
        saved_plots.append(output_path)
        print(f"  ✓ Saved: {output_path}")
    
    return saved_plots


def main():
    """Run residual histogram creation pipeline."""
    from importlib import import_module
    
    load_and_clean = import_module('01_load_and_clean').load_and_clean
    compute_returns = import_module('02_returns_and_excess').compute_returns_and_excess
    
    # Load and prepare data
    df = load_and_clean(source="csv")
    df = compute_returns(df)
    
    # Create histograms
    saved_plots = create_all_residual_histograms(df)
    
    print(f"\n=== Created {len(saved_plots)} residual histogram plots ===")


if __name__ == "__main__":
    main()
