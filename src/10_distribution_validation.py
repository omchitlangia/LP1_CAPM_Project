"""
Distribution validation for CAPM residuals.

Analyzes residual distribution properties (log and simple returns):
- Fits OLS CAPM model for each return type and asset
- Computes residual statistics: skewness, kurtosis, excess kurtosis
- Performs normality tests: Jarque-Bera (required), Shapiro-Wilk (optional)
- Saves comprehensive results table with interpretation
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
from scipy import stats
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
    should_generate = config.should_generate
except (ImportError, ModuleNotFoundError):
    ASSETS = ["MSFT", "GE", "FORD"]
    MARKET_TICKER = "SP500"
    TABLE_DIR = Path(__file__).parent.parent / "report" / "tables"
    SIGNIFICANCE_LEVEL = 0.05
    
    def should_generate(path, force=False):
        return force or not path.exists()


def compute_residual_stats(residuals: np.ndarray) -> dict:
    """
    Compute statistical metrics for residuals.
    
    Args:
        residuals: Array of residuals from CAPM regression
        
    Returns:
        Dictionary with skew, kurtosis, and excess kurtosis
    """
    skew = stats.skew(residuals)
    kurtosis = stats.kurtosis(residuals, fisher=False)  # Pearson's kurtosis (excess = fisher, raw = not fisher)
    excess_kurtosis = kurtosis - 3  # Excess kurtosis for normal distribution
    
    return {
        'Skew': skew,
        'Kurtosis': kurtosis,
        'Excess_Kurtosis': excess_kurtosis
    }


def jarque_bera_test(residuals: np.ndarray) -> dict:
    """
    Perform Jarque-Bera test for normality.
    
    H0: Data is normally distributed
    H1: Data is not normally distributed
    
    Args:
        residuals: Array of residuals
        
    Returns:
        Dictionary with test statistic and p-value
    """
    try:
        jb_stat, jb_pvalue = stats.jarque_bera(residuals)
        return {
            'JB_stat': jb_stat,
            'JB_pvalue': jb_pvalue
        }
    except Exception as e:
        print(f"  Error in Jarque-Bera test: {e}")
        return {
            'JB_stat': np.nan,
            'JB_pvalue': np.nan
        }


def shapiro_wilk_test(residuals: np.ndarray, max_n: int = 5000) -> dict:
    """
    Perform Shapiro-Wilk test for normality (only if N <= max_n due to computational cost).
    
    H0: Data is normally distributed
    H1: Data is not normally distributed
    
    Args:
        residuals: Array of residuals
        max_n: Maximum sample size to compute test (default 5000)
        
    Returns:
        Dictionary with test statistic and p-value (NaN if N > max_n)
    """
    n_obs = len(residuals)
    
    # Skip if sample size too large
    if n_obs > max_n:
        return {
            'Shapiro_stat': np.nan,
            'Shapiro_pvalue': np.nan
        }
    
    try:
        shapiro_stat, shapiro_pvalue = stats.shapiro(residuals)
        return {
            'Shapiro_stat': shapiro_stat,
            'Shapiro_pvalue': shapiro_pvalue
        }
    except Exception as e:
        print(f"  Error in Shapiro-Wilk test: {e}")
        return {
            'Shapiro_stat': np.nan,
            'Shapiro_pvalue': np.nan
        }


def capm_regression_get_residuals(df: pd.DataFrame, asset: str, market_col: str) -> np.ndarray:
    """
    Run CAPM OLS regression and return residuals.
    
    Formula: asset_excess = alpha + beta * market_excess + error
    
    Args:
        df: DataFrame with excess returns
        asset: Asset name (e.g., 'MSFT')
        market_col: Market column name (e.g., 'SP500_Excess')
        
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
    
    Formula: asset_excess_simple = alpha + beta * market_excess_simple + error
    
    Args:
        df: DataFrame with excess returns
        asset: Asset name (e.g., 'MSFT')
        market_col: Market column name (e.g., 'SP500_Excess_SIMPLE')
        
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


def interpret_distribution(skew: float, kurtosis: float, jb_pvalue: float) -> str:
    """
    Create interpretation statement for residual distribution.
    
    Args:
        skew: Skewness of residuals
        kurtosis: Kurtosis of residuals
        jb_pvalue: P-value from Jarque-Bera test
        
    Returns:
        Interpretation string
    """
    parts = []
    
    # Tail behavior
    if kurtosis > 3:
        parts.append("fat tails")
    
    # Skewness
    if skew > 0.1:
        parts.append("right-skew")
    elif skew < -0.1:
        parts.append("left-skew")
    else:
        parts.append("near-symmetric")
    
    # Normality
    if jb_pvalue < SIGNIFICANCE_LEVEL:
        parts.append("reject normality")
    else:
        parts.append("fail to reject normality")
    
    return "; ".join(parts)


def run_distribution_validation(df: pd.DataFrame, 
                               assets: list = ASSETS,
                               market: str = MARKET_TICKER) -> pd.DataFrame:
    """
    Run distribution validation for all assets and both return types.
    
    Args:
        df: DataFrame with returns and excess returns
        assets: List of asset tickers
        market: Market ticker
        
    Returns:
        DataFrame with residual distribution tests
    """
    results = []
    
    # === LOG RETURNS ===
    print("\n=== Distribution Validation: LOG RETURNS ===\n")
    
    market_col_log = f'{market}_Excess'
    
    for asset in assets:
        if f'{asset}_Excess' not in df.columns:
            print(f"  ⚠ Skipping {asset} (no log excess returns)")
            continue
        
        print(f"Processing {asset} (LOG)...")
        
        # Get residuals from CAPM regression
        residuals = capm_regression_get_residuals(df, asset, market_col_log)
        
        # Skip if NaN residuals
        if np.all(np.isnan(residuals)):
            print(f"  ✗ Failed to compute residuals for {asset}")
            continue
        
        # Compute statistics
        stats_dict = compute_residual_stats(residuals)
        jb_dict = jarque_bera_test(residuals)
        sw_dict = shapiro_wilk_test(residuals)
        
        # Combine results
        row = {
            'Return_Type': 'LOG',
            'Asset': asset,
            'Skew': stats_dict['Skew'],
            'Kurtosis': stats_dict['Kurtosis'],
            'Excess_Kurtosis': stats_dict['Excess_Kurtosis'],
            'JB_stat': jb_dict['JB_stat'],
            'JB_pvalue': jb_dict['JB_pvalue'],
            'Shapiro_stat': sw_dict['Shapiro_stat'],
            'Shapiro_pvalue': sw_dict['Shapiro_pvalue'],
            'N_obs': len(residuals),
            'Interpretation': interpret_distribution(
                stats_dict['Skew'], 
                stats_dict['Kurtosis'], 
                jb_dict['JB_pvalue']
            )
        }
        results.append(row)
        print(f"  ✓ {asset}: N={len(residuals)}, Skew={stats_dict['Skew']:.4f}, " +
              f"Kurt={stats_dict['Kurtosis']:.4f}, JB_p={jb_dict['JB_pvalue']:.4f}")
    
    # === SIMPLE RETURNS ===
    print("\n=== Distribution Validation: SIMPLE RETURNS ===\n")
    
    market_col_simple = f'{market}_Excess_SIMPLE'
    
    for asset in assets:
        if f'{asset}_Excess_SIMPLE' not in df.columns:
            print(f"  ⚠ Skipping {asset} (no simple excess returns)")
            continue
        
        print(f"Processing {asset} (SIMPLE)...")
        
        # Get residuals from CAPM regression
        residuals = capm_regression_get_residuals_simple(df, asset, market_col_simple)
        
        # Skip if NaN residuals
        if np.all(np.isnan(residuals)):
            print(f"  ✗ Failed to compute residuals for {asset}")
            continue
        
        # Compute statistics
        stats_dict = compute_residual_stats(residuals)
        jb_dict = jarque_bera_test(residuals)
        sw_dict = shapiro_wilk_test(residuals)
        
        # Combine results
        row = {
            'Return_Type': 'SIMPLE',
            'Asset': asset,
            'Skew': stats_dict['Skew'],
            'Kurtosis': stats_dict['Kurtosis'],
            'Excess_Kurtosis': stats_dict['Excess_Kurtosis'],
            'JB_stat': jb_dict['JB_stat'],
            'JB_pvalue': jb_dict['JB_pvalue'],
            'Shapiro_stat': sw_dict['Shapiro_stat'],
            'Shapiro_pvalue': sw_dict['Shapiro_pvalue'],
            'N_obs': len(residuals),
            'Interpretation': interpret_distribution(
                stats_dict['Skew'], 
                stats_dict['Kurtosis'], 
                jb_dict['JB_pvalue']
            )
        }
        results.append(row)
        print(f"  ✓ {asset}: N={len(residuals)}, Skew={stats_dict['Skew']:.4f}, " +
              f"Kurt={stats_dict['Kurtosis']:.4f}, JB_p={jb_dict['JB_pvalue']:.4f}")
    
    return pd.DataFrame(results)


def save_distribution_tests(results_df: pd.DataFrame) -> Path:
    """
    Save residual distribution tests to CSV.
    
    Handles appending if file exists with missing return type/asset combos.
    
    Args:
        results_df: DataFrame with test results
        
    Returns:
        Path to saved file
    """
    output_path = TABLE_DIR / 'residual_distribution_tests.csv'
    
    if output_path.exists():
        # Load existing results
        existing_df = pd.read_csv(output_path)
        
        # Find new rows (not in existing data)
        new_rows = []
        for _, row in results_df.iterrows():
            # Check if this combination exists
            match = existing_df[
                (existing_df['Return_Type'] == row['Return_Type']) &
                (existing_df['Asset'] == row['Asset'])
            ]
            if match.empty:
                new_rows.append(row)
        
        if new_rows:
            # Append new rows
            new_df = pd.DataFrame(new_rows)
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            combined_df.to_csv(output_path, index=False)
            print(f"✓ Appended {len(new_rows)} new rows to {output_path}")
        else:
            print(f"ℹ No new rows to add to {output_path}")
    else:
        # Create new file
        results_df.to_csv(output_path, index=False)
        print(f"✓ Created {output_path}")
    
    return output_path


def main():
    """Run distribution validation pipeline."""
    from importlib import import_module
    
    load_and_clean = import_module('01_load_and_clean').load_and_clean
    compute_returns = import_module('02_returns_and_excess').compute_returns_and_excess
    
    # Load and prepare data
    df = load_and_clean(source="csv")
    df = compute_returns(df)
    
    # Run validation
    results_df = run_distribution_validation(df)
    
    # Save results
    save_distribution_tests(results_df)
    
    print("\n=== Distribution Validation Results ===")
    print(results_df.to_string())


if __name__ == "__main__":
    main()
