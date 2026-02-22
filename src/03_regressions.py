"""
CAPM regression analysis using OLS.

Runs the CAPM model: R_i_excess = alpha + beta * R_m_excess + error
Hypothesis test: H0: alpha = 0 (correctly priced), H1: alpha != 0 (mispriced)
Significance level: 5%
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
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
    TABLE_DIR = config.TABLE_DIR
    SIGNIFICANCE_LEVEL = config.SIGNIFICANCE_LEVEL
except (ImportError, ModuleNotFoundError):
    # Fallback defaults
    ASSETS = ["Msft", "GE", "Ford"]
    MARKET_TICKER = "SP500"
    TABLE_DIR = Path(__file__).parent.parent / "report" / "tables"
    SIGNIFICANCE_LEVEL = 0.05


def run_capm_regression(y: pd.Series, X: pd.DataFrame, asset_name: str) -> dict:
    """
    Run CAPM OLS regression for a single asset.
    
    Formula: R_i_excess = alpha + beta * R_m_excess + error
    
    Args:
        y: Excess return of asset
        X: Market excess return (will have constant added)
        asset_name: Name of asset for labeling
        
    Returns:
        Dictionary with regression results
    """
    # Add constant for intercept (alpha)
    X_with_const = sm.add_constant(X)
    
    # Fit OLS model
    model = sm.OLS(y, X_with_const).fit()
    
    # Extract key results - use iloc for position-based indexing
    alpha = model.params.iloc[0]
    beta = model.params.iloc[1]
    alpha_pvalue = model.pvalues.iloc[0]
    beta_pvalue = model.pvalues.iloc[1]
    r_squared = model.rsquared
    adj_r_squared = model.rsquared_adj
    
    # Check if alpha is significantly different from 0 at 5% level
    alpha_significant = (alpha_pvalue < SIGNIFICANCE_LEVEL)
    
    results_dict = {
        'Asset': asset_name,
        'Alpha': alpha,
        'Alpha_PValue': alpha_pvalue,
        'Alpha_Significant': alpha_significant,
        'Beta': beta,
        'Beta_PValue': beta_pvalue,
        'R_Squared': r_squared,
        'Adj_R_Squared': adj_r_squared,
        'N_Obs': len(y),
        'Model': model
    }
    
    return results_dict


def capm_regression_all_assets(df: pd.DataFrame, 
                                assets: list = ASSETS,
                                market: str = MARKET_TICKER) -> pd.DataFrame:
    """
    Run CAPM regression for all assets.
    
    Args:
        df: DataFrame with excess returns
        assets: List of asset tickers
        market: Market ticker
        
    Returns:
        DataFrame with regression summary (without model object)
    """
    results = []
    models = {}
    
    market_excess = df[f'{market}_Excess']
    
    print("\n=== CAPM REGRESSION RESULTS ===\n")
    
    for asset in assets:
        asset_excess = df[f'{asset}_Excess']
        
        result_dict = run_capm_regression(asset_excess, market_excess, asset)
        models[asset] = result_dict.pop('Model')
        
        results.append(result_dict)
        
        # Print summary for each asset
        print(f"\n{asset.upper()}")
        print("-" * 60)
        print(f"Alpha (intercept):        {result_dict['Alpha']:.6f}")
        print(f"  p-value:                {result_dict['Alpha_PValue']:.4f}")
        print(f"  Significant at 5%?      {result_dict['Alpha_Significant']}")
        print(f"Beta (slope):             {result_dict['Beta']:.6f}")
        print(f"  p-value:                {result_dict['Beta_PValue']:.4f}")
        print(f"R-squared:                {result_dict['R_Squared']:.4f}")
        print(f"Adj R-squared:            {result_dict['Adj_R_Squared']:.4f}")
        print(f"Observations:             {result_dict['N_Obs']}")
    
    results_df = pd.DataFrame(results)
    
    return results_df, models


def save_regression_results(results_df: pd.DataFrame, output_file: Path = None) -> Path:
    """
    Save regression results to CSV file.
    
    Args:
        results_df: DataFrame with regression results
        output_file: Path to save CSV (default: report/tables/capm_regression_results.csv)
        
    Returns:
        Path to saved file
    """
    if output_file is None:
        output_file = TABLE_DIR / "capm_regression_results.csv"
    
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    results_df.to_csv(output_file, index=False)
    print(f"\n✓ Regression results saved to: {output_file}")
    
    return output_file


def main():
    """Run CAPM regression pipeline."""
    from load_and_clean import load_and_clean
    from returns_and_excess import compute_returns_and_excess
    
    df = load_and_clean(source="csv")
    df = compute_returns_and_excess(df)
    
    results_df, models = capm_regression_all_assets(df)
    save_regression_results(results_df)
    
    print("\n=== Summary ===")
    print(results_df[['Asset', 'Alpha', 'Alpha_PValue', 'Beta', 'R_Squared']])
    
    return results_df, models


if __name__ == "__main__":
    main()
