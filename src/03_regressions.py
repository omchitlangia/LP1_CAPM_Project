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
    HAC_LAGS = config.HAC_LAGS
except (ImportError, ModuleNotFoundError):
    # Fallback defaults
    ASSETS = ["MSFT", "GE", "FORD"]
    MARKET_TICKER = "SP500"
    TABLE_DIR = Path(__file__).parent.parent / "report" / "tables"
    SIGNIFICANCE_LEVEL = 0.05
    HAC_LAGS = 10


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


def extract_hac_results(model, asset_name: str, maxlags: int = None) -> dict:
    """
    Extract HAC (Newey-West) robust standard errors and p-values from fitted OLS model.
    
    Args:
        model: Fitted OLS model from statsmodels
        asset_name: Name of asset for labeling
        maxlags: Maximum number of lags for Newey-West (default: HAC_LAGS from config)
        
    Returns:
        Dictionary with HAC-robust regression results
    """
    if maxlags is None:
        maxlags = HAC_LAGS
    
    # Get HAC robust covariance matrix results
    hac_results = model.get_robustcov_results(cov_type="HAC", maxlags=maxlags)
    
    # Extract HAC-robust standard errors and p-values
    # Handle both Series and ndarray access patterns
    if hasattr(model.params, 'iloc'):
        alpha = model.params.iloc[0]
        beta = model.params.iloc[1]
    else:
        alpha = model.params[0]
        beta = model.params[1]
    
    if hasattr(hac_results.pvalues, 'iloc'):
        alpha_pvalue = hac_results.pvalues.iloc[0]
        beta_pvalue = hac_results.pvalues.iloc[1]
    else:
        alpha_pvalue = hac_results.pvalues[0]
        beta_pvalue = hac_results.pvalues[1]
    
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
        'N_Obs': len(model.resid),
    }
    
    return results_dict


def capm_regression_all_assets(df: pd.DataFrame, 
                                assets: list = ASSETS,
                                market: str = MARKET_TICKER) -> tuple:
    """
    Run CAPM regression for all assets using OLS.
    
    Args:
        df: DataFrame with excess returns
        assets: List of asset tickers
        market: Market ticker
        
    Returns:
        Tuple: (DataFrame with OLS results, dict of fitted models, dict of HAC results)
    """
    results_ols = []
    results_hac = []
    models = {}
    
    market_excess = df[f'{market}_Excess']
    
    print("\n=== CAPM REGRESSION RESULTS ===\n")
    print(f"Standard errors reported with HAC (Newey-West, maxlags={HAC_LAGS}) correction\n")
    
    for asset in assets:
        asset_excess = df[f'{asset}_Excess']
        
        # Run OLS regression
        result_dict = run_capm_regression(asset_excess, market_excess, asset)
        model = result_dict.pop('Model')
        models[asset] = model
        
        # Normalize asset name to uppercase for output
        result_dict['Asset'] = asset.upper()
        results_ols.append(result_dict)
        
        # Extract HAC-robust results
        hac_dict = extract_hac_results(model, asset.upper())
        results_hac.append(hac_dict)
        
        # Print summary for each asset (using HAC p-values)
        print(f"\n{asset.upper()}")
        print("-" * 60)
        print(f"Alpha (intercept):        {result_dict['Alpha']:.6f}")
        print(f"  p-value (HAC):          {hac_dict['Alpha_PValue']:.4f}")
        print(f"Beta (slope):             {result_dict['Beta']:.6f}")
        print(f"  p-value (HAC):          {hac_dict['Beta_PValue']:.4f}")
        print(f"R-squared:                {result_dict['R_Squared']:.4f}")
        print(f"Adj R-squared:            {result_dict['Adj_R_Squared']:.4f}")
        print(f"Observations:             {result_dict['N_Obs']}")
    
    results_ols_df = pd.DataFrame(results_ols)
    results_hac_df = pd.DataFrame(results_hac)
    
    return results_ols_df, results_hac_df, models


def save_regression_results(results_ols_df: pd.DataFrame, 
                            results_hac_df: pd.DataFrame = None,
                            ols_output_file: Path = None,
                            hac_output_file: Path = None) -> tuple:
    """
    Save regression results (OLS and HAC) to CSV files.
    
    Args:
        results_ols_df: DataFrame with OLS regression results
        results_hac_df: DataFrame with HAC regression results
        ols_output_file: Path to save OLS CSV (default: report/tables/capm_regression_results_ols.csv)
        hac_output_file: Path to save HAC CSV (default: report/tables/capm_regression_results_hac.csv)
        
    Returns:
        Tuple of (OLS file path, HAC file path)
    """
    if ols_output_file is None:
        ols_output_file = TABLE_DIR / "capm_regression_results_ols.csv"
    
    if hac_output_file is None:
        hac_output_file = TABLE_DIR / "capm_regression_results_hac.csv"
    
    ols_output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Save OLS results
    ols_output_df = results_ols_df[['Asset', 'Alpha', 'Alpha_PValue', 'Beta', 'Beta_PValue', 'R_Squared', 'Adj_R_Squared', 'N_Obs']].copy()
    ols_output_df.columns = ['Asset', 'Alpha', 'Alpha_pvalue', 'Beta', 'Beta_pvalue', 'R_Squared', 'Adj_R_Squared', 'N_Obs']
    ols_output_df.to_csv(ols_output_file, index=False)
    print(f"\n✓ OLS results saved to: {ols_output_file}")
    
    # Save HAC results if provided
    if results_hac_df is not None:
        hac_output_df = results_hac_df[['Asset', 'Alpha', 'Alpha_PValue', 'Beta', 'Beta_PValue', 'R_Squared', 'Adj_R_Squared', 'N_Obs']].copy()
        hac_output_df.columns = ['Asset', 'Alpha', 'Alpha_pvalue', 'Beta', 'Beta_pvalue', 'R_Squared', 'Adj_R_Squared', 'N_Obs']
        hac_output_df.to_csv(hac_output_file, index=False)
        print(f"✓ HAC results saved to:  {hac_output_file}")
    
    return ols_output_file, hac_output_file


def main():
    """Run CAPM regression pipeline."""
    from load_and_clean import load_and_clean
    from returns_and_excess import compute_returns_and_excess
    
    df = load_and_clean(source="csv")
    df = compute_returns_and_excess(df)
    
    results_ols_df, results_hac_df, models = capm_regression_all_assets(df)
    save_regression_results(results_ols_df, results_hac_df)
    
    print("\n=== OLS Summary ===")
    print(results_ols_df[['Asset', 'Alpha', 'Alpha_PValue', 'Beta', 'R_Squared']])
    
    print("\n=== HAC Summary ===")
    print(results_hac_df[['Asset', 'Alpha', 'Alpha_PValue', 'Beta', 'R_Squared']])
    
    return results_ols_df, results_hac_df, models


if __name__ == "__main__":
    main()
