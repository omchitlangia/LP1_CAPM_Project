"""
CAPM validation summary for all assets (log and simple returns).

Combines regression, diagnostics, stability, and normality tests into a 
comprehensive validation table for each asset and return type.

For SIMPLE returns, computes HAC regression results internally if not existing.
"""

import pandas as pd
import numpy as np
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
    TABLE_DIR = config.TABLE_DIR
    HAC_LAGS = config.HAC_LAGS
    SIGNIFICANCE_LEVEL = config.SIGNIFICANCE_LEVEL
    should_generate = config.should_generate
except (ImportError, ModuleNotFoundError):
    ASSETS = ["MSFT", "GE", "FORD"]
    MARKET_TICKER = "SP500"
    TABLE_DIR = Path(__file__).parent.parent / "report" / "tables"
    HAC_LAGS = 10
    SIGNIFICANCE_LEVEL = 0.05
    
    def should_generate(path, force=False):
        return force or not path.exists()


def load_hac_results_log() -> pd.DataFrame:
    """Load existing HAC regression results for log returns."""
    hac_path = TABLE_DIR / 'capm_regression_results_hac.csv'
    if hac_path.exists():
        df = pd.read_csv(hac_path)
        # Standardize asset names to uppercase if needed
        if 'Asset' in df.columns:
            df['Asset'] = df['Asset'].str.upper()
        return df
    else:
        print(f"  ⚠ Warning: HAC results file not found: {hac_path}")
        return pd.DataFrame()


def compute_hac_results_simple(df: pd.DataFrame, 
                              assets: list = ASSETS,
                              market: str = MARKET_TICKER) -> pd.DataFrame:
    """
    Compute HAC regression results for simple returns.
    
    Args:
        df: DataFrame with simple excess returns
        assets: List of asset tickers
        market: Market ticker
        
    Returns:
        DataFrame with HAC results for simple returns
    """
    results = []
    market_col = f'{market}_Excess_SIMPLE'
    
    print("\n=== Computing HAC Results for SIMPLE Returns ===\n")
    
    for asset in assets:
        asset_col = f'{asset}_Excess_SIMPLE'
        
        if asset_col not in df.columns or market_col not in df.columns:
            print(f"  ⚠ Skipping {asset} (missing simple excess returns)")
            continue
        
        # Prepare data
        y = df[asset_col].values
        X = sm.add_constant(df[market_col].values)
        
        try:
            # Fit OLS
            model = sm.OLS(y, X).fit()
            
            # Get HAC robust results
            hac_results = model.get_robustcov_results(cov_type="HAC", maxlags=HAC_LAGS)
            
            # Extract results
            alpha = model.params[0]
            beta = model.params[1]
            alpha_pvalue_hac = hac_results.pvalues[0]
            beta_pvalue_hac = hac_results.pvalues[1]
            r_squared = model.rsquared
            adj_r_squared = model.rsquared_adj
            
            result_row = {
                'Asset': asset,
                'Alpha': alpha,
                'Alpha_pvalue': alpha_pvalue_hac,
                'Beta': beta,
                'Beta_pvalue': beta_pvalue_hac,
                'R_Squared': r_squared,
                'Adj_R_Squared': adj_r_squared,
                'N_Obs': len(y)
            }
            results.append(result_row)
            
            print(f"✓ {asset}: Alpha={alpha:.6f} (p={alpha_pvalue_hac:.4f}), " +
                  f"Beta={beta:.4f}, R²={r_squared:.4f}")
            
        except Exception as e:
            print(f"✗ Error for {asset}: {e}")
            continue
    
    return pd.DataFrame(results)


def load_diagnostics() -> pd.DataFrame:
    """Load diagnostic test results (BP test, Ljung-Box test)."""
    diag_path = TABLE_DIR / 'capm_diagnostics.csv'
    if diag_path.exists():
        df = pd.read_csv(diag_path)
        # Standardize asset names
        if 'Asset' in df.columns:
            df['Asset'] = df['Asset'].str.upper()
        return df
    else:
        print(f"  ⚠ Warning: Diagnostics file not found: {diag_path}")
        return pd.DataFrame()


def load_subperiod_results() -> pd.DataFrame:
    """Load subperiod robustness results (beta stability)."""
    subperiod_path = TABLE_DIR / 'capm_subperiod_results.csv'
    if subperiod_path.exists():
        df = pd.read_csv(subperiod_path)
        # Standardize asset names
        if 'Asset' in df.columns:
            df['Asset'] = df['Asset'].str.upper()
        return df
    else:
        print(f"  ⚠ Warning: Subperiod results file not found: {subperiod_path}")
        return pd.DataFrame()


def load_distribution_tests() -> pd.DataFrame:
    """Load residual distribution test results."""
    dist_path = TABLE_DIR / 'residual_distribution_tests.csv'
    if dist_path.exists():
        df = pd.read_csv(dist_path)
        # Standardize asset names
        if 'Asset' in df.columns:
            df['Asset'] = df['Asset'].str.upper()
        return df
    else:
        print(f"  ⚠ Warning: Distribution tests file not found: {dist_path}")
        return pd.DataFrame()


def build_validation_summary(hac_log_df: pd.DataFrame,
                            hac_simple_df: pd.DataFrame,
                            diag_df: pd.DataFrame,
                            subperiod_df: pd.DataFrame,
                            dist_df: pd.DataFrame,
                            assets: list = ASSETS) -> pd.DataFrame:
    """
    Build comprehensive validation summary table.
    
    Args:
        hac_log_df: HAC results for log returns
        hac_simple_df: HAC results for simple returns
        diag_df: Diagnostic test results
        subperiod_df: Subperiod robustness results
        dist_df: Distribution test results
        assets: List of asset tickers
        
    Returns:
        DataFrame with combined validation summary
    """
    summary_rows = []
    
    # Process each return type
    for return_type, hac_df in [('LOG', hac_log_df), ('SIMPLE', hac_simple_df)]:
        
        if hac_df.empty:
            print(f"  ⚠ No HAC results for {return_type} returns")
            continue
        
        for asset in assets:
            # Get HAC regression results
            hac_row = hac_df[hac_df['Asset'] == asset]
            if hac_row.empty:
                continue
            
            alpha_hac = hac_row['Alpha'].values[0]
            alpha_p_hac = hac_row['Alpha_pvalue'].values[0]
            beta_hac = hac_row['Beta'].values[0]
            r_squared = hac_row['R_Squared'].values[0]
            
            # Get diagnostics
            het_flag = False
            autocorr_flag = False
            
            if not diag_df.empty:
                diag_row = diag_df[diag_df['Asset'] == asset]
                if not diag_row.empty:
                    bp_pvalue = diag_row.get('BP_PValue', pd.Series([np.nan])).values[0]
                    lb_pvalue = diag_row.get('LB_PValue_Lag10', pd.Series([np.nan])).values[0]
                    
                    het_flag = pd.notna(bp_pvalue) and bp_pvalue < SIGNIFICANCE_LEVEL
                    autocorr_flag = pd.notna(lb_pvalue) and lb_pvalue < SIGNIFICANCE_LEVEL
            
            # Get beta stability range
            beta_range = 0.0
            if not subperiod_df.empty:
                subperiod_rows = subperiod_df[subperiod_df['Asset'] == asset]
                if not subperiod_rows.empty:
                    beta_col = 'Beta' if 'Beta' in subperiod_rows.columns else None
                    if beta_col:
                        betas = subperiod_rows[beta_col].dropna()
                        if len(betas) > 0:
                            beta_range = float(betas.max() - betas.min())
            
            # Get normality test result
            normality_reject = False
            if not dist_df.empty:
                dist_row = dist_df[
                    (dist_df['Return_Type'] == return_type) &
                    (dist_df['Asset'] == asset)
                ]
                if not dist_row.empty:
                    jb_pvalue = dist_row['JB_pvalue'].values[0]
                    normality_reject = pd.notna(jb_pvalue) and jb_pvalue < SIGNIFICANCE_LEVEL
            
            # Build validation statement
            validation_parts = []
            
            # Alpha significance test
            if alpha_p_hac >= SIGNIFICANCE_LEVEL:
                validation_parts.append(
                    "Alpha not significant → no strong evidence against CAPM in alpha-test sense."
                )
            else:
                validation_parts.append(
                    "Alpha significant → CAPM rejected in alpha-test sense (abnormal return)."
                )
            
            # Diagnostic concerns
            if het_flag or autocorr_flag:
                validation_parts.append(
                    "Diagnostics suggest robust inference required."
                )
            
            # Beta stability concern
            if beta_range > 0.20:
                validation_parts.append(
                    "Beta varies across regimes → stability concern."
                )
            
            validation_statement = " ".join(validation_parts)
            
            # Create summary row
            summary_row = {
                'Return_Type': return_type,
                'Asset': asset,
                'Alpha_HAC': alpha_hac,
                'Alpha_p_HAC': alpha_p_hac,
                'Beta_HAC': beta_hac,
                'R2': r_squared,
                'Heteroskedasticity_flag': het_flag,
                'Autocorr_flag': autocorr_flag,
                'Normality_reject': normality_reject,
                'Beta_stability_range': beta_range,
                'CAPM_validated_statement': validation_statement
            }
            summary_rows.append(summary_row)
    
    return pd.DataFrame(summary_rows)


def save_validation_summary(summary_df: pd.DataFrame) -> Path:
    """
    Save validation summary to CSV.
    
    Args:
        summary_df: Validation summary DataFrame
        
    Returns:
        Path to saved file
    """
    output_path = TABLE_DIR / 'capm_validation_summary.csv'
    summary_df.to_csv(output_path, index=False)
    print(f"\n✓ Saved validation summary: {output_path}")
    return output_path


def main():
    """Run CAPM validation summary pipeline."""
    from importlib import import_module
    
    print("=" * 70)
    print("CAPM VALIDATION SUMMARY BUILDER")
    print("=" * 70)
    
    # Load data if needed for simple returns HAC computation
    load_and_clean = import_module('01_load_and_clean').load_and_clean
    compute_returns = import_module('02_returns_and_excess').compute_returns_and_excess
    
    df = load_and_clean(source="csv")
    df = compute_returns(df)
    
    # Load existing results
    print("\n[STEP 1] Loading existing results...")
    hac_log_df = load_hac_results_log()
    diag_df = load_diagnostics()
    subperiod_df = load_subperiod_results()
    dist_df = load_distribution_tests()
    
    # Compute HAC for simple returns if needed
    print("\n[STEP 2] Computing HAC results for simple returns...")
    hac_simple_df = compute_hac_results_simple(df)
    
    # Build summary
    print("\n[STEP 3] Building validation summary...")
    summary_df = build_validation_summary(hac_log_df, hac_simple_df, diag_df, subperiod_df, dist_df)
    
    # Save
    print("\n[STEP 4] Saving results...")
    save_validation_summary(summary_df)
    
    print("\n=== CAPM Validation Summary ===")
    print(summary_df.to_string())


if __name__ == "__main__":
    main()
