"""
Master pipeline script for CAPM LP1 analysis.

Runs the complete analysis pipeline in order:
1. Load and clean data
2. Compute log and simple returns and excess returns
3. Run CAPM regressions
4. Generate plots and save outputs
5. Distribution validation (log + simple)
6. Residual histograms (log + simple)
7. CAPM validation summary

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

# Extract what we need from config
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

# Import diagnostics, robustness, descriptive stats, master summary, and residual plots
diagnostics = importlib.import_module('04_diagnostics')
robustness = importlib.import_module('05_robustness')
desc_stats = importlib.import_module('07_descriptive_stats')
master_summary = importlib.import_module('08_master_summary')
residual_plots = importlib.import_module('09_residual_plots')

run_all_diagnostics = diagnostics.run_all_diagnostics
save_diagnostics = diagnostics.save_diagnostics
run_all_subperiods = robustness.run_all_subperiods
save_subperiod_results = robustness.save_subperiod_results
compute_all_rolling_betas = robustness.compute_all_rolling_betas
compute_all_descriptive_stats = desc_stats.compute_all_descriptive_stats
save_descriptive_stats = desc_stats.save_descriptive_stats
build_master_summary = master_summary.build_master_summary
load_all_results = master_summary.load_all_results
sanity_check = master_summary.sanity_check
save_master_summary = master_summary.save_master_summary
create_all_residual_plots = residual_plots.create_all_residual_plots

# Import new validation modules
dist_validation = importlib.import_module('10_distribution_validation')
residual_hists = importlib.import_module('11_residual_histograms')
capm_validation = importlib.import_module('12_capm_validation_summary')

run_distribution_validation = dist_validation.run_distribution_validation
save_distribution_tests = dist_validation.save_distribution_tests
create_all_residual_histograms = residual_hists.create_all_residual_histograms


def run_pipeline():
    """Execute the complete CAPM analysis pipeline."""
    
    print("=" * 70)
    print("CAPM LP1 ANALYSIS - MASTER PIPELINE (with distribution & validation)")
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
    
    # Step 2: Compute returns and excess returns (LOG and SIMPLE)
    print("\n[STEP 2] Computing log returns + simple returns and excess returns...")
    try:
        df = compute_returns_and_excess(df)
        print(f"  ✓ Computed all return types and excess returns")
    except Exception as e:
        print(f"  ✗ Error computing returns: {e}")
        return False
    
    # Step 3: Run CAPM regressions (OLS and HAC) - uses log returns (existing)
    print("\n[STEP 3] Running CAPM OLS regressions (with HAC robust inference)...")
    try:
        results_ols_df, results_hac_df, models = capm_regression_all_assets(df)
        ols_file, hac_file = save_regression_results(results_ols_df, results_hac_df)
        print(f"  ✓ Completed regressions for {len(models)} assets (LOG returns)")
    except Exception as e:
        print(f"  ✗ Error running regressions: {e}")
        return False
    
    # Step 3.5: Compute descriptive statistics
    print("\n[STEP 3.5] Computing descriptive statistics...")
    try:
        stats_df = compute_all_descriptive_stats(df)
        stats_file = save_descriptive_stats(stats_df)
        print(f"  ✓ Completed descriptive statistics")
    except Exception as e:
        print(f"  ✗ Error computing descriptive statistics: {e}")
        return False
    
    # Step 4: Generate plots
    print("\n[STEP 4] Generating scatter plots with fit lines...")
    try:
        saved_plots = create_all_scatter_plots(df, models)
        print(f"  ✓ Generated {len(saved_plots)} scatter plots")
    except Exception as e:
        print(f"  ✗ Error generating plots: {e}")
        return False
    
    # Step 5: Run diagnostic tests
    print("\n[STEP 5] Running diagnostic tests...")
    try:
        diagnostics_df = run_all_diagnostics(df, models)
        save_diagnostics(diagnostics_df)
        print(f"  ✓ Completed diagnostics for {len(models)} assets")
    except Exception as e:
        print(f"  ✗ Error running diagnostics: {e}")
        return False
    
    # Step 6: Run robustness tests
    print("\n[STEP 6] Running robustness tests...")
    try:
        # Subperiod analysis
        subperiod_df = run_all_subperiods(df)
        save_subperiod_results(subperiod_df)
        
        # Rolling beta analysis
        rolling_betas, rolling_plots = compute_all_rolling_betas(df)
        print(f"  ✓ Completed robustness checks ({len(rolling_plots)} rolling beta plots)")
    except Exception as e:
        print(f"  ✗ Error running robustness tests: {e}")
        return False
    
    # Step 7: Build master summary table
    print("\n[STEP 7] Building master summary table...")
    try:
        hac_df, diag_df, subperiod_df, desc_df = load_all_results()
        master_df = build_master_summary(hac_df, diag_df, subperiod_df, desc_df)
        sanity_check(master_df, hac_df)
        master_file = save_master_summary(master_df)
        print(f"  ✓ Completed master summary")
    except Exception as e:
        print(f"  ✗ Error building master summary: {e}")
        return False
    
    # Step 8: Generate residual diagnostic plots
    print("\n[STEP 8] Generating residual diagnostic plots...")
    try:
        residual_plot_paths = create_all_residual_plots(df)
        print(f"  ✓ Generated {len(residual_plot_paths)} residual diagnostic plots")
    except Exception as e:
        print(f"  ✗ Error generating residual plots: {e}")
        return False
    
    # Step 9: Distribution validation (LOG + SIMPLE returns)
    print("\n[STEP 9] Running distribution validation (LOG + SIMPLE returns)...")
    try:
        dist_results_df = run_distribution_validation(df)
        dist_file = save_distribution_tests(dist_results_df)
        print(f"  ✓ Completed distribution validation for all assets")
    except Exception as e:
        print(f"  ✗ Error running distribution validation: {e}")
        return False
    
    # Step 10: Create residual histograms (LOG + SIMPLE returns)
    print("\n[STEP 10] Creating residual histograms (LOG + SIMPLE returns)...")
    try:
        histogram_paths = create_all_residual_histograms(df)
        print(f"  ✓ Generated {len(histogram_paths)} residual histogram plots")
    except Exception as e:
        print(f"  ✗ Error creating histograms: {e}")
        return False
    
    # Step 11: Build CAPM validation summary
    print("\n[STEP 11] Building CAPM validation summary (LOG + SIMPLE)...")
    try:
        validation_results = capm_validation.main.__wrapped__() if hasattr(capm_validation.main, '__wrapped__') else None
        if validation_results is None:
            # Call the main function which handles everything
            import types
            
            # Capture the output by importing functions directly
            hac_log_df = capm_validation.load_hac_results_log()
            hac_simple_df = capm_validation.compute_hac_results_simple(df)
            diag_df = capm_validation.load_diagnostics()
            subperiod_df = capm_validation.load_subperiod_results()
            dist_df = capm_validation.load_distribution_tests()
            
            validation_summary_df = capm_validation.build_validation_summary(
                hac_log_df, hac_simple_df, diag_df, subperiod_df, dist_df
            )
            validation_file = capm_validation.save_validation_summary(validation_summary_df)
            print(f"  ✓ Completed CAPM validation summary")
    except Exception as e:
        print(f"  ✗ Error building validation summary: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Summary
    print("\n" + "=" * 70)
    print("PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 70)
    
    print("\n[OUTPUT SUMMARY]")
    print(f"\nRegression & Analysis Tables (Existing):")
    print(f"  {ols_file}")
    print(f"  {hac_file}")
    print(f"  {stats_file}")
    print(f"  {TABLE_DIR / 'capm_diagnostics.csv'}")
    print(f"  {TABLE_DIR / 'capm_subperiod_results.csv'}")
    print(f"  {master_file} *** MASTER SUMMARY ***")
    
    print(f"\nNew: Distribution & Validation Tables:")
    print(f"  {TABLE_DIR / 'residual_distribution_tests.csv'}")
    print(f"  {TABLE_DIR / 'capm_validation_summary.csv'}")
    print(f"  {TABLE_DIR / 'capm_excess_log.csv'} (intermediate)")
    print(f"  {TABLE_DIR / 'capm_excess_simple.csv'} (intermediate)")
    
    print(f"\nCharacteristic Line Scatter Plots (PNG):")
    for plot_path in saved_plots:
        print(f"  {plot_path}")
    
    print(f"\nRolling Beta Plots (PNG):")
    for plot_path in rolling_plots:
        print(f"  {plot_path}")
    
    print(f"\nResidual Diagnostic Plots (PNG):")
    for plot_path in residual_plot_paths:
        print(f"  {plot_path}")
    
    print(f"\nNew: Residual Histograms (LOG + SIMPLE) (PNG):")
    for plot_path in histogram_paths:
        print(f"  {plot_path}")
    
    print(f"\nData shape: {df.shape}")
    print(f"Analysis period: {df['Date'].min().date()} to {df['Date'].max().date()}")
    
    print("\n[FIRST ROWS OF NEW OUTPUTS]")
    
    print("\nResidual Distribution Tests (first 4 rows):")
    try:
        dist_summary = pd.read_csv(TABLE_DIR / 'residual_distribution_tests.csv')
        print(dist_summary.head(4).to_string(index=False))
    except Exception as e:
        print(f"  (Could not load: {e})")
    
    print("\nCAP Validation Summary (first 4 rows):")
    try:
        val_summary = pd.read_csv(TABLE_DIR / 'capm_validation_summary.csv')
        print(val_summary.head(4).to_string(index=False))
    except Exception as e:
        print(f"  (Could not load: {e})")
    
    print("\n" + "=" * 70)
    
    return True


if __name__ == "__main__":
    # Import pandas for summary output
    import pandas as pd
    success = run_pipeline()
    sys.exit(0 if success else 1)
