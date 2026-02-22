"""
Master pipeline script for CAPM LP1 analysis.

Runs the complete analysis pipeline in order:
1. Load and clean data
2. Compute returns and excess returns
3. Run CAPM regressions
4. Generate plots and save outputs

Can be executed as:
  python -m src.run_all
  python src/run_all.py
"""

import sys
import importlib
from pathlib import Path

# Ensure src directory is in path for imports (numbered module names)
src_path = Path(__file__).parent.absolute()
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Import modules using importlib (handles numbered filenames like 00_config.py)
config = importlib.import_module('00_config')
load_clean = importlib.import_module('01_load_and_clean')
returns = importlib.import_module('02_returns_and_excess')
regressions = importlib.import_module('03_regressions')
plots = importlib.import_module('06_plots')

# Extract what we need
ensure_dirs = config.ensure_dirs
DATA_DIR = config.DATA_DIR
REPORT_DIR = config.REPORT_DIR
FIG_DIR = config.FIG_DIR
TABLE_DIR = config.TABLE_DIR

load_and_clean = load_clean.load_and_clean
compute_returns_and_excess = returns.compute_returns_and_excess
capm_regression_all_assets = regressions.capm_regression_all_assets
save_regression_results = regressions.save_regression_results
create_all_scatter_plots = plots.create_all_scatter_plots


def run_pipeline():
    """Execute the complete CAPM analysis pipeline."""
    
    print("=" * 70)
    print("CAPM LP1 ANALYSIS - MASTER PIPELINE")
    print("=" * 70)
    
    # Ensure output directories exist
    print("\n[STEP 0] Creating output directories...")
    ensure_dirs()
    print(f"  ✓ Report dir: {REPORT_DIR}")
    print(f"  ✓ Figures dir: {FIG_DIR}")
    print(f"  ✓ Tables dir: {TABLE_DIR}")
    
    # Step 1: Load and clean data
    print("\n[STEP 1] Loading and cleaning data...")
    try:
        df = load_and_clean(source="csv")
        print(f"  ✓ Loaded data shape: {df.shape}")
    except Exception as e:
        print(f"  ✗ Error loading data: {e}")
        return False
    
    # Step 2: Compute returns and excess returns
    print("\n[STEP 2] Computing log returns and excess returns...")
    try:
        df = compute_returns_and_excess(df)
        print(f"  ✓ Computed returns and excess returns")
    except Exception as e:
        print(f"  ✗ Error computing returns: {e}")
        return False
    
    # Step 3: Run CAPM regressions
    print("\n[STEP 3] Running CAPM OLS regressions...")
    try:
        results_df, models = capm_regression_all_assets(df)
        save_regression_results(results_df)
        print(f"  ✓ Completed regressions for {len(models)} assets")
    except Exception as e:
        print(f"  ✗ Error running regressions: {e}")
        return False
    
    # Step 4: Generate plots
    print("\n[STEP 4] Generating scatter plots with fit lines...")
    try:
        saved_plots = create_all_scatter_plots(df, models)
        print(f"  ✓ Generated {len(saved_plots)} plots")
    except Exception as e:
        print(f"  ✗ Error generating plots: {e}")
        return False
    
    # Summary
    print("\n" + "=" * 70)
    print("PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 70)
    
    print("\n[OUTPUT SUMMARY]")
    print(f"\nRegression Results Table:")
    print(f"  {TABLE_DIR / 'capm_regression_results.csv'}")
    print(f"\nScatter Plots (PNG):")
    for plot_path in saved_plots:
        print(f"  {plot_path}")
    
    print(f"\nData shape: {df.shape}")
    print(f"Number of assets analyzed: {len(models)}")
    print(f"Analysis period: {df['Date'].min().date()} to {df['Date'].max().date()}")
    
    print("\n" + "=" * 70)
    
    return True


if __name__ == "__main__":
    success = run_pipeline()
    sys.exit(0 if success else 1)
