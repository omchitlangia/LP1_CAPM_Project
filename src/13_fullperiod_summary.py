"""
Full-period (whole sample, no subperiods) CAPM regression summary.

This module ensures that explicit full-period regression outputs are available
in the pipeline for clear, unambiguous reporting. It aliases or copies the 
full-sample regression results into clearly-named fullperiod files.

Formula: R_i_excess = alpha + beta * R_m_excess + error
Period: Full sample (1993-2003), no breaks
"""

import pandas as pd
from pathlib import Path
import importlib
import sys

# Handle imports - support both module and direct execution
src_path = Path(__file__).parent.absolute()
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

try:
    config = importlib.import_module('00_config')
    TABLE_DIR = config.TABLE_DIR
    SIGNIFICANCE_LEVEL = config.SIGNIFICANCE_LEVEL
    should_generate = config.should_generate
except (ImportError, ModuleNotFoundError):
    # Fallback defaults
    TABLE_DIR = Path(__file__).parent.parent / "report" / "tables"
    SIGNIFICANCE_LEVEL = 0.05
    
    def should_generate(output_path: Path, force: bool = None) -> bool:
        return not Path(output_path).exists()

try:
    utils_io = importlib.import_module('utils_io')
    ensure_alias_output = utils_io.ensure_alias_output
except (ImportError, ModuleNotFoundError):
    # Fallback: simple copy function
    import shutil
    
    def ensure_alias_output(src_path: Path, dst_path: Path, force: bool = None) -> bool:
        src_path = Path(src_path)
        dst_path = Path(dst_path)
        if not src_path.exists():
            raise FileNotFoundError(f"Source file not found: {src_path}")
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        if force or not dst_path.exists():
            shutil.copy2(src_path, dst_path)
            return True
        return False


def ensure_fullperiod_regression_files(force: bool = None) -> tuple:
    """
    Ensure full-period regression result files exist.
    
    If capm_fullperiod_results_*.csv don't exist, copy them from the
    general capm_regression_results_*.csv files. This provides an
    explicit, clearly-labeled full-period output set.
    
    Args:
        force: If True, always regenerate. If None, uses config FORCE_REBUILD.
        
    Returns:
        Tuple of (OLS output path, HAC output path)
    """
    # Source: existing full-sample regression results
    src_ols = TABLE_DIR / "capm_regression_results_ols.csv"
    src_hac = TABLE_DIR / "capm_regression_results_hac.csv"
    
    # Destination: explicit full-period results
    dst_ols = TABLE_DIR / "capm_fullperiod_results_ols.csv"
    dst_hac = TABLE_DIR / "capm_fullperiod_results_hac.csv"
    
    # Ensure source files exist
    if not src_hac.exists():
        raise FileNotFoundError(f"Source regression file not found: {src_hac}")
    if not src_ols.exists():
        raise FileNotFoundError(f"Source regression file not found: {src_ols}")
    
    # Alias (copy) if destination doesn't exist
    try:
        ensure_alias_output(src_hac, dst_hac, force=force)
        ensure_alias_output(src_ols, dst_ols, force=force)
        print(f"\n✓ Full-period regression files ensured:")
        print(f"  {dst_ols}")
        print(f"  {dst_hac}")
    except Exception as e:
        print(f"✗ Error ensuring full-period files: {e}")
        raise
    
    return dst_ols, dst_hac


def build_fullperiod_summary(hac_results_df: pd.DataFrame = None) -> pd.DataFrame:
    """
    Build full-period interpretation summary.
    
    Creates a summary table with columns:
    - Asset
    - Alpha_HAC
    - Alpha_p_HAC
    - Beta_HAC
    - R2
    - Key_Interpretation
    
    The Key_Interpretation field 1) checks if alpha is significant at 5% level using HAC p-values
    2) Provides a one-sentence statement about CAPM validity
    
    Args:
        hac_results_df: DataFrame with HAC regression results. If None, loads from disc.
        
    Returns:
        DataFrame with full-period summary
    """
    # Load HAC results if not provided
    if hac_results_df is None:
        hac_file = TABLE_DIR / "capm_regression_results_hac.csv"
        if not hac_file.exists():
            raise FileNotFoundError(f"HAC results file not found: {hac_file}")
        hac_results_df = pd.read_csv(hac_file)
    
    summary_rows = []
    
    for _, row in hac_results_df.iterrows():
        asset = row['Asset']
        alpha = row['Alpha']
        alpha_p = row['Alpha_pvalue']
        beta = row['Beta']
        r2 = row['R_Squared']
        
        # Determine interpretation based on HAC p-value
        if alpha_p >= SIGNIFICANCE_LEVEL:
            interpretation = (
                "Alpha not significant → CAPM not rejected in alpha-test sense over full period. "
                "HAC used due to daily data diagnostics."
            )
        else:
            interpretation = (
                "Alpha significant → CAPM rejected in alpha-test sense over full period. "
                "HAC used due to daily data diagnostics."
            )
        
        summary_rows.append({
            'Asset': asset,
            'Alpha_HAC': alpha,
            'Alpha_p_HAC': alpha_p,
            'Beta_HAC': beta,
            'R2': r2,
            'Key_Interpretation': interpretation
        })
    
    return pd.DataFrame(summary_rows)


def save_fullperiod_summary(summary_df: pd.DataFrame, 
                           output_file: Path = None) -> Path:
    """
    Save full-period summary to CSV.
    
    Args:
        summary_df: Summary DataFrame to save
        output_file: Path to output file (default: report/tables/capm_fullperiod_summary.csv)
        
    Returns:
        Path to saved file
    """
    if output_file is None:
        output_file = TABLE_DIR / "capm_fullperiod_summary.csv"
    
    output_file.parent.mkdir(parents=True, exist_ok=True)
    summary_df.to_csv(output_file, index=False)
    
    return output_file


def main():
    """
    Main entry point: ensure full-period outputs and create summary.
    
    Returns:
        Summary DataFrame
    """
    print("\n=== FULL-PERIOD CAPM REGRESSION SUMMARY ===\n")
    
    # Ensure explicit full-period regression files exist (alias from general results)
    print("[Step 1] Ensuring full-period regression output files...")
    dst_ols, dst_hac = ensure_fullperiod_regression_files()
    
    # Load HAC results and build summary
    print("[Step 2] Building full-period interpretation summary...")
    hac_results_df = pd.read_csv(dst_hac)
    
    summary_df = build_fullperiod_summary(hac_results_df)
    
    # Save summary
    print("[Step 3] Saving full-period summary table...")
    summary_file = save_fullperiod_summary(summary_df)
    print(f"  ✓ Summary saved to: {summary_file}")
    
    print("\n[FULL-PERIOD SUMMARY]")
    print(summary_df.to_string(index=False))
    
    return summary_df


if __name__ == "__main__":
    summary_df = main()
