"""
Master summary table combining all CAPM analysis results.

Merges results from:
- Regression results (HAC preferred)
- Diagnostic tests
- Subperiod analysis
- Descriptive statistics
"""

import pandas as pd
import numpy as np
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
except (ImportError, ModuleNotFoundError):
    ASSETS = ["Msft", "GE", "Ford"]
    MARKET_TICKER = "SP500"
    TABLE_DIR = Path(__file__).parent.parent / "report" / "tables"


def load_all_results() -> tuple:
    """
    Load all required result CSVs from report/tables.
    
    Returns:
        Tuple of (hac_df, diag_df, subperiod_df, desc_df)
    """
    hac_file = TABLE_DIR / "capm_regression_results_hac.csv"
    diag_file = TABLE_DIR / "capm_diagnostics.csv"
    subperiod_file = TABLE_DIR / "capm_subperiod_results.csv"
    desc_file = TABLE_DIR / "descriptive_stats.csv"
    
    # Check all files exist
    required_files = [hac_file, diag_file, subperiod_file, desc_file]
    for file in required_files:
        if not file.exists():
            raise FileNotFoundError(f"Required file missing: {file}")
    
    # Load files
    hac_df = pd.read_csv(hac_file)
    diag_df = pd.read_csv(diag_file)
    subperiod_df = pd.read_csv(subperiod_file)
    desc_df = pd.read_csv(desc_file)
    
    return hac_df, diag_df, subperiod_df, desc_df


def compute_subperiod_beta_ranges(subperiod_df: pd.DataFrame) -> dict:
    """
    Compute beta min/max/range from subperiod analysis.
    
    Args:
        subperiod_df: DataFrame with subperiod regression results
        
    Returns:
        Dictionary mapping asset name (uppercase) to (beta_min, beta_max, beta_range)
    """
    beta_ranges = {}
    
    for asset in ASSETS:
        # Try both original case and uppercase
        asset_data = subperiod_df[subperiod_df['Asset'] == asset]
        
        if len(asset_data) == 0:
            # Try uppercase
            asset_data = subperiod_df[subperiod_df['Asset'] == asset.upper()]
        
        if len(asset_data) == 0:
            raise ValueError(f"No subperiod data found for {asset} or {asset.upper()}")
        
        beta_values = asset_data['Beta'].values
        beta_min = beta_values.min()
        beta_max = beta_values.max()
        beta_range = beta_max - beta_min
        
        # Store with uppercase key for consistency with master table
        beta_ranges[asset.upper()] = {
            'Beta_subperiod_min': beta_min,
            'Beta_subperiod_max': beta_max,
            'Beta_subperiod_range': beta_range,
        }
    
    return beta_ranges


def build_master_summary(hac_df: pd.DataFrame,
                        diag_df: pd.DataFrame,
                        subperiod_df: pd.DataFrame,
                        desc_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build comprehensive master summary table for all assets.
    
    Args:
        hac_df: HAC regression results
        diag_df: Diagnostic test results
        subperiod_df: Subperiod regression results
        desc_df: Descriptive statistics
        
    Returns:
        Master summary DataFrame
    """
    # Start with HAC regression results
    master = hac_df[['Asset', 'Alpha', 'Alpha_pvalue', 'Beta', 'Beta_pvalue', 
                     'R_Squared', 'Adj_R_Squared', 'N_Obs']].copy()
    master.columns = ['Asset', 'Alpha_HAC', 'Alpha_p_HAC', 'Beta_HAC', 
                      'Beta_p_HAC', 'R2', 'Adj_R2', 'N']
    
    # Add diagnostic test results
    diag_df_subset = diag_df[['Asset', 'BP_pvalue', 'DW_stat', 
                              'LB_pvalue_lag5', 'LB_pvalue_lag10']].copy()
    diag_df_subset.columns = ['Asset', 'BP_pvalue', 'DW_stat', 
                             'LB_p_lag5', 'LB_p_lag10']
    master = master.merge(diag_df_subset, on='Asset', how='left')
    
    # Add descriptive statistics (asset and market)
    desc_asset_data = []
    desc_market = None
    
    for _, row in desc_df.iterrows():
        if row['Series'] == 'SP500':
            desc_market = {
                'Mean_mkt': row['Mean'],
                'Std_mkt': row['Std'],
            }
        else:
            # Map to asset names (upper case in desc_df)
            desc_asset_data.append({
                'Asset': row['Series'],
                'Mean_asset': row['Mean'],
                'Std_asset': row['Std'],
            })
    
    desc_asset_df = pd.DataFrame(desc_asset_data)
    master = master.merge(desc_asset_df, on='Asset', how='left')
    
    # Add market stats to all rows
    if desc_market:
        master['Mean_mkt'] = desc_market['Mean_mkt']
        master['Std_mkt'] = desc_market['Std_mkt']
    else:
        raise ValueError("Market (SP500) statistics not found in descriptive stats")
    
    # Add subperiod beta ranges
    beta_ranges = compute_subperiod_beta_ranges(subperiod_df)
    
    beta_range_data = []
    for asset in master['Asset'].values:
        if asset in beta_ranges:
            beta_range_data.append(beta_ranges[asset])
        else:
            raise ValueError(f"No subperiod data for {asset}")
    
    beta_range_df = pd.DataFrame(beta_range_data)
    master = pd.concat([master.reset_index(drop=True), 
                       beta_range_df.reset_index(drop=True)], axis=1)
    
    return master


def sanity_check(master_df: pd.DataFrame, hac_df: pd.DataFrame) -> None:
    """
    Perform sanity checks on master summary.
    
    Args:
        master_df: Master summary DataFrame
        hac_df: Original HAC results for comparison
    """
    print("\n=== SANITY CHECKS ===\n")
    
    # Check all assets present
    expected_assets = set([a.upper() for a in ASSETS])
    actual_assets = set(master_df['Asset'].values)
    
    if expected_assets != actual_assets:
        missing = expected_assets - actual_assets
        extra = actual_assets - expected_assets
        if missing:
            print(f"⚠ Missing assets: {missing}")
        if extra:
            print(f"⚠ Extra assets: {extra}")
    else:
        print(f"✓ All {len(expected_assets)} expected assets present: {expected_assets}")
    
    # Check N consistency
    n_values = master_df['N'].unique()
    if len(n_values) == 1:
        print(f"✓ N consistent across all assets: {n_values[0]}")
    else:
        print(f"⚠ N varies across assets: {n_values}")
    
    # Check no missing values in key columns
    key_cols = ['Alpha_HAC', 'Beta_HAC', 'R2', 'BP_pvalue', 'DW_stat', 
                'Mean_asset', 'Std_asset', 'Mean_mkt', 'Std_mkt',
                'Beta_subperiod_min', 'Beta_subperiod_max']
    
    missing_counts = master_df[key_cols].isna().sum()
    if missing_counts.sum() == 0:
        print(f"✓ No missing values in {len(key_cols)} key columns")
    else:
        missing_cols = missing_counts[missing_counts > 0]
        print(f"⚠ Missing values in {len(missing_cols)} column(s):")
        for col, count in missing_cols.items():
            print(f"  {col}: {count} missing")
        # If diagnostics fields are missing, raise error
        diag_cols = ['BP_pvalue', 'DW_stat', 'LB_p_lag5', 'LB_p_lag10']
        diag_missing = [c for c in diag_cols if c in missing_cols.index and missing_cols[c] > 0]
        if diag_missing:
            raise ValueError(f"Diagnostics columns missing from all assets. This suggests merge failed. Missing: {diag_missing}")
    
    # Check HAC beta matches
    hac_betas = set(hac_df['Beta'].values)
    master_betas = set(master_df['Beta_HAC'].values)
    if hac_betas == master_betas:
        print(f"✓ Beta values match between HAC and master summary")
    else:
        print(f"⚠ Beta mismatch detected")
    
    print()


def save_master_summary(master_df: pd.DataFrame, 
                       output_file: Path = None) -> Path:
    """
    Save master summary to CSV file.
    
    Args:
        master_df: Master summary DataFrame
        output_file: Path to save CSV (default: report/tables/capm_master_summary.csv)
        
    Returns:
        Path to saved file
    """
    if output_file is None:
        output_file = TABLE_DIR / "capm_master_summary.csv"
    
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Round numerics for readability in CSV
    rounded_df = master_df.copy()
    numeric_cols = rounded_df.select_dtypes(include=['float64', 'float32']).columns
    rounded_df[numeric_cols] = rounded_df[numeric_cols].round(6)
    
    rounded_df.to_csv(output_file, index=False)
    print(f"✓ Master summary saved to: {output_file}")
    
    return output_file


def main():
    """Run master summary pipeline."""
    print("\n=== BUILDING MASTER SUMMARY TABLE ===\n")
    
    # Load all results
    hac_df, diag_df, subperiod_df, desc_df = load_all_results()
    print("✓ All required input files loaded")
    
    # Build master summary
    master_df = build_master_summary(hac_df, diag_df, subperiod_df, desc_df)
    print("✓ Master summary table built")
    
    # Sanity checks
    sanity_check(master_df, hac_df)
    
    # Save to CSV
    output_file = save_master_summary(master_df)
    
    # Print summary
    print("\nMaster Summary Preview:")
    print(master_df.to_string(index=False))
    
    return master_df, output_file


if __name__ == "__main__":
    main()
