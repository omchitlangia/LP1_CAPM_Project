"""
Generate and save CAPM scatter plots and characteristic lines.

Creates Security Characteristic Line plots (excess returns vs market excess)
with fitted regression line for each asset.
"""

import pandas as pd
import matplotlib.pyplot as plt
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
    FIG_DIR = config.FIG_DIR
except (ImportError, ModuleNotFoundError):
    # Fallback defaults
    ASSETS = ["Msft", "GE", "Ford"]
    MARKET_TICKER = "SP500"
    FIG_DIR = Path(__file__).parent.parent / "report" / "figures"


def create_scatter_plot_with_fit(df: pd.DataFrame,
                                  asset: str,
                                  market: str,
                                  model,
                                  title: str = None,
                                  figsize: tuple = (8, 6),
                                  output_path: Path = None) -> Path:
    """
    Create and save a scatter plot with fitted regression line.
    
    Args:
        df: DataFrame with excess returns
        asset: Asset ticker
        market: Market ticker
        model: Fitted OLS model
        title: Plot title (default: "Security Characteristic Line - {Asset}")
        figsize: Figure size tuple
        output_path: Path to save PNG (default: report/figures/{asset}_scatter.png)
        
    Returns:
        Path to saved figure
    """
    if title is None:
        title = f"Security Characteristic Line - {asset}"
    
    if output_path is None:
        output_path = FIG_DIR / f"{asset}_scatter.png"
    
    # Create figure
    fig, ax = plt.subplots(figsize=figsize)
    
    x = df[f'{market}_Excess']
    y = df[f'{asset}_Excess']
    
    # Scatter plot
    ax.scatter(x, y, alpha=0.3, s=20, color='blue', label='Observed')
    
    # Fitted line
    x_line = np.array([[x.min()], [x.max()]]).ravel()
    X_line = np.column_stack([np.ones_like(x_line), x_line])
    y_fit = model.predict(X_line)
    ax.plot(x_line, y_fit, color='red', linewidth=2, label='Fitted Line')
    
    # Labels and title
    ax.set_xlabel("Market Excess Return", fontsize=11)
    ax.set_ylabel(f"{asset} Excess Return", fontsize=11)
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)
    
    # Save figure
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Saved plot: {output_path}")
    
    return output_path


def create_all_scatter_plots(df: pd.DataFrame,
                             models: dict,
                             assets: list = ASSETS,
                             market: str = MARKET_TICKER) -> list:
    """
    Create scatter plots for all assets.
    
    Args:
        df: DataFrame with excess returns
        models: Dictionary of fitted models {asset: model}
        assets: List of asset tickers
        market: Market ticker
        
    Returns:
        List of paths to saved figures
    """
    saved_plots = []
    
    print("\n=== Creating Scatter Plots ===\n")
    
    for asset in assets:
        if asset in models:
            model = models[asset]
            output_path = FIG_DIR / f"{asset}_scatter.png"
            path = create_scatter_plot_with_fit(df, asset, market, model, 
                                                output_path=output_path)
            saved_plots.append(path)
    
    return saved_plots


def main():
    """Run plot generation pipeline."""
    from load_and_clean import load_and_clean
    from returns_and_excess import compute_returns_and_excess
    from regressions import capm_regression_all_assets
    
    df = load_and_clean(source="csv")
    df = compute_returns_and_excess(df)
    results_df, models = capm_regression_all_assets(df)
    
    saved_plots = create_all_scatter_plots(df, models)
    
    print(f"\n=== Summary ===")
    print(f"Created {len(saved_plots)} scatter plots:")
    for path in saved_plots:
        print(f"  - {path}")
    
    return saved_plots


if __name__ == "__main__":
    main()
