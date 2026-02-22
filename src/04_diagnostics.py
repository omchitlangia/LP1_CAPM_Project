"""
Diagnostic tests for CAPM regression model.

Implements tests for:
- Heteroskedasticity (Breusch-Pagan test)
- Autocorrelation (Durbin-Watson statistic, Ljung-Box test)
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.stats.diagnostic import het_breuschpagan, acorr_ljungbox
from statsmodels.stats.stattools import durbin_watson
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
    SIGNIFICANCE_LEVEL = config.SIGNIFICANCE_LEVEL
except (ImportError, ModuleNotFoundError):
    ASSETS = ["Msft", "GE", "Ford"]
    MARKET_TICKER = "SP500"
    TABLE_DIR = Path(__file__).parent.parent / "report" / "tables"
    SIGNIFICANCE_LEVEL = 0.05


def compute_breusch_pagan(residuals: np.ndarray, X: np.ndarray) -> float:
    """
    Breusch-Pagan test for heteroskedasticity.
    
    H0: Homoskedastic (constant variance)
    H1: Heteroskedastic (non-constant variance)
    
    Args:
        residuals: Model residuals
        X: Design matrix (with intercept)
        
    Returns:
        p-value from the test
    """
    try:
        _, pvalue, _, _ = het_breuschpagan(residuals, X)
        return pvalue
    except Exception:
        return np.nan


def compute_durbin_watson(residuals: np.ndarray) -> float:
    """
    Durbin-Watson statistic for autocorrelation.
    
    Values near 2 suggest no autocorrelation.
    Values < 2 suggest positive autocorrelation.
    Values > 2 suggest negative autocorrelation.
    
    Args:
        residuals: Model residuals
        
    Returns:
        Durbin-Watson statistic
    """
    try:
        dw = durbin_watson(residuals)
        return dw
    except Exception:
        return np.nan


def compute_ljung_box_pvalue(residuals: np.ndarray, lags: int = 5) -> float:
    """
    Ljung-Box test for autocorrelation.
    
    H0: No autocorrelation at specified lag
    H1: Autocorrelation exists at specified lag
    
    Args:
        residuals: Model residuals
        lags: Lag order to test (default: 5)
        
    Returns:
        p-value from the test
    """
    try:
        lb_result = acorr_ljungbox(residuals, lags=lags, return_df=True)
        # Return the p-value for the specified lag
        pvalue = lb_result['lb_pvalue'].iloc[-1]
        return pvalue
    except Exception:
        return np.nan


def run_diagnostics(y: pd.Series, X: np.ndarray, residuals: np.ndarray, asset_name: str) -> dict:
    """
    Run all diagnostic tests for a single asset regression.
    
    Args:
        y: Dependent variable (excess return)
        X: Design matrix with intercept
        residuals: Model residuals
        asset_name: Name of asset
        
    Returns:
        Dictionary with diagnostic statistics
    """
    results_dict = {
        'Asset': asset_name,
        'BP_pvalue': compute_breusch_pagan(residuals, X),
        'DW_stat': compute_durbin_watson(residuals),
        'LB_pvalue_lag5': compute_ljung_box_pvalue(residuals, lags=5),
        'LB_pvalue_lag10': compute_ljung_box_pvalue(residuals, lags=10),
        'N_obs': len(y)
    }
    return results_dict


def run_all_diagnostics(df: pd.DataFrame,
                        models: dict,
                        assets: list = ASSETS,
                        market: str = MARKET_TICKER) -> pd.DataFrame:
    """
    Run diagnostics for all asset regressions.
    
    Args:
        df: DataFrame with excess returns
        models: Dictionary of fitted OLS models {asset: model}
        assets: List of asset tickers
        market: Market ticker
        
    Returns:
        DataFrame with diagnostic results
    """
    results = []
    
    print("\n=== DIAGNOSTIC TESTS ===\n")
    
    market_excess = df[f'{market}_Excess']
    X = sm.add_constant(market_excess)
    
    for asset in assets:
        if asset in models:
            model = models[asset]
            asset_excess = df[f'{asset}_Excess']
            residuals = model.resid
            
            result_dict = run_diagnostics(asset_excess, X, residuals, asset)
            results.append(result_dict)
            
            # Print summary
            print(f"{asset.upper()}")
            print("-" * 60)
            print(f"Breusch-Pagan p-value:        {result_dict['BP_pvalue']:.4f}")
            print(f"  Heteroskedastic (5%)?       {result_dict['BP_pvalue'] < 0.05}")
            print(f"Durbin-Watson statistic:      {result_dict['DW_stat']:.4f}")
            print(f"Ljung-Box p-value (lag 5):    {result_dict['LB_pvalue_lag5']:.4f}")
            print(f"Ljung-Box p-value (lag 10):   {result_dict['LB_pvalue_lag10']:.4f}")
            print(f"Observations:                 {result_dict['N_obs']}")
            print()
    
    results_df = pd.DataFrame(results)
    
    return results_df


def save_diagnostics(diagnostics_df: pd.DataFrame, output_file: Path = None) -> Path:
    """
    Save diagnostic results to CSV.
    
    Args:
        diagnostics_df: DataFrame with diagnostic results
        output_file: Path to save (default: report/tables/capm_diagnostics.csv)
        
    Returns:
        Path to saved file
    """
    if output_file is None:
        output_file = TABLE_DIR / "capm_diagnostics.csv"
    
    output_file.parent.mkdir(parents=True, exist_ok=True)
    diagnostics_df.to_csv(output_file, index=False)
    print(f"✓ Diagnostic results saved to: {output_file}")
    
    return output_file


def main():
    """Run diagnostic tests pipeline."""
    from load_and_clean import load_and_clean
    from returns_and_excess import compute_returns_and_excess
    from regressions import capm_regression_all_assets
    
    df = load_and_clean(source="csv")
    df = compute_returns_and_excess(df)
    results_df, models = capm_regression_all_assets(df)
    
    diagnostics_df = run_all_diagnostics(df, models)
    save_diagnostics(diagnostics_df)
    
    print("\n=== Diagnostics Summary ===")
    print(diagnostics_df)
    
    return diagnostics_df


if __name__ == "__main__":
    main()
