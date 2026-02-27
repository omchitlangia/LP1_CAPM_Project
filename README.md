# CAPM LP1 Analysis - Reproducible Research Repository

Capital Asset Pricing Model (CAPM) analysis for financial assets (Microsoft, GE, Ford) using daily returns data (1993-2003).

## Project Structure

```
LP1_CAPM_Project/
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── .gitignore                         # Git ignore rules
│
├── data/                              # Raw and processed data
│   ├── findat.csv                     # Daily price and T-bill data
│   └── capm_data.xlsx                 # Alternative Excel format
│
├── src/                               # Modular Python scripts
│   ├── __init__.py                    # Package initialization
│   ├── 00_config.py                   # Configuration, paths, and I/O helpers
│   ├── 01_load_and_clean.py           # Data loading and cleaning
│   ├── 02_returns_and_excess.py       # Log + simple returns computation
│   ├── 03_regressions.py              # CAPM OLS regression analysis
│   ├── 04_diagnostics.py              # Diagnostic tests (heteroskedasticity, autocorr)
│   ├── 05_robustness.py               # Sub-period & rolling beta analysis
│   ├── 06_plots.py                    # Scatter plots and visualization
│   ├── 07_descriptive_stats.py        # Descriptive statistics
│   ├── 08_master_summary.py           # Master summary table builder
│   ├── 09_residual_plots.py           # Residual diagnostic plots
│   ├── 10_distribution_validation.py  # Residual distribution tests (LOG + SIMPLE)
│   ├── 11_residual_histograms.py      # Residual histograms (LOG + SIMPLE)
│   ├── 12_capm_validation_summary.py  # CAPM validation table (LOG + SIMPLE)
│   ├── 13_fullperiod_summary.py       # Full-period (no breaks) regression summary
│   ├── utils_io.py                    # I/O utilities (file aliasing, existence checks)
│   └── run_all.py                     # Master pipeline orchestrator
│
├── notebooks/                         # Jupyter notebooks
│   └── LP1_Jupyter_clean.ipynb        # Cleaned analysis notebook
│
└── report/                            # Analysis outputs
    ├── LP1_CAPM_Report_Scaffold.md    # Report template
    ├── tables/                        # Output tables (CSV)
    │   ├── capm_regression_results.csv
    │   ├── capm_regression_results_ols.csv
    │   ├── capm_regression_results_hac.csv
    │   ├── capm_diagnostics.csv
    │   ├── capm_subperiod_results.csv
    │   ├── descriptive_stats.csv
    │   ├── capm_master_summary.csv
    │   ├── capm_fullperiod_results_ols.csv    # NEW: Full-period OLS regression results
    │   ├── capm_fullperiod_results_hac.csv    # NEW: Full-period HAC regression results
    │   ├── capm_fullperiod_summary.csv        # NEW: Full-period summary with interpretation
    │   ├── capm_excess_log.csv        # Log excess returns
    │   ├── capm_excess_simple.csv     # Simple excess returns
    │   ├── residual_distribution_tests.csv  # Residual distribution statistics
    │   └── capm_validation_summary.csv      # Validation summary (LOG+SIMPLE)
    └── figures/                       # Output figures (PNG)
        ├── MSFT_scatter.png
        ├── GE_scatter.png
        ├── FORD_scatter.png
        ├── MSFT_rolling_beta.png
        ├── GE_rolling_beta.png
        ├── FORD_rolling_beta.png
        ├── MSFT_residuals_*.png, GE_residuals_*.png, FORD_residuals_*.png
        ├── MSFT_residual_hist_LOG.png         # NEW: Residual histograms (LOG)
        ├── GE_residual_hist_LOG.png
        ├── FORD_residual_hist_LOG.png
        ├── MSFT_residual_hist_SIMPLE.png      # NEW: Residual histograms (SIMPLE)
        ├── GE_residual_hist_SIMPLE.png
        └── FORD_residual_hist_SIMPLE.png
```

## Quick Start

### 1. Clone or Download This Repository

```bash
cd LP1_CAPM_Project
```

### 2. Create and Activate Virtual Environment

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Run the Analysis Pipeline

Run the complete analysis from the repo root:

```bash
python -m src.run_all
```

Or alternatively:

```bash
python src/run_all.py
```

### 5. Check Outputs

After running the pipeline, check key outputs:

- **Regression Results (Log Returns):** `report/tables/capm_regression_results_hac.csv`
- **Full-Period Regression Results (NEW):** `report/tables/capm_fullperiod_results_hac.csv`, `capm_fullperiod_summary.csv`
- **Scatter Plots:** `report/figures/MSFT_scatter.png`, `report/figures/GE_scatter.png`, `report/figures/FORD_scatter.png`
- **Distribution Tests:** `report/tables/residual_distribution_tests.csv` (log & simple returns)
- **Validation Summary:** `report/tables/capm_validation_summary.csv` (log & simple returns)
- **Residual Histograms:** `report/figures/{ASSET}_residual_hist_{LOG|SIMPLE}.png` (6 total)

---

## Analysis Overview

### Data
- **Source:** Daily closing prices and T-bill rates (1993-2003)
- **Assets:** Microsoft (MSFT), General Electric (GE), Ford Motor (FORD)
- **Market Index:** S&P 500
- **Trading Days:** 252 per year

### Methodology

The analysis supports **two return types** (LOG and SIMPLE) for comprehensive CAPM validation:

#### LOG RETURNS (Primary, Original Pipeline)
**Daily Log Returns:**
$$R_{\log,t} = \ln\left(\frac{P_t}{P_{t-1}}\right)$$

**Excess Log Returns:**
$$R_{\log}^{\text{excess}} = R_{\log} - R_f^{\text{daily}}$$

**CAPM with Log Returns:**
$$R_{i,\log}^{\text{excess}} = \alpha + \beta \cdot R_{m,\log}^{\text{excess}} + \epsilon$$

#### SIMPLE RETURNS (New, Alternative Specification)
**Daily Simple Returns:**
$$R_{\text{simple},t} = \frac{P_t}{P_{t-1}} - 1$$

**Excess Simple Returns:**
$$R_{\text{simple}}^{\text{excess}} = R_{\text{simple}} - R_f^{\text{daily}}$$

**CAPM with Simple Returns:**
$$R_{i,\text{simple}}^{\text{excess}} = \alpha + \beta \cdot R_{m,\text{simple}}^{\text{excess}} + \epsilon$$

#### Risk-Free Rate (Common to Both)
$$R_f^{\text{daily}} = \frac{\text{T-bill annual rate}}{100} / 252$$

### Hypothesis Test

- **H₀:** α = 0 (Security is correctly priced under CAPM)
- **H₁:** α ≠ 0 (Security is mispriced)
- **Significance Level:** 5%

### Distribution Validation (NEW)

For each asset and return type, the pipeline now validates residual distributions:

1. **Descriptive Statistics:**
   - Skewness
   - Kurtosis (Pearson's definition, raw - 3 = excess kurtosis)

2. **Normality Tests:**
   - Jarque-Bera test (always computed)
   - Shapiro-Wilk test (if N ≤ 5000)

3. **Results Table:** `residual_distribution_tests.csv`
   - Return_Type (LOG/SIMPLE)
   - Asset
   - Skew, Kurtosis, Excess_Kurtosis
   - JB_stat, JB_pvalue, Shapiro_stat, Shapiro_pvalue
   - Interpretation ("fat tails", "right-skew"/"left-skew"/"near-symmetric", "reject/fail to reject normality")

### CAPM Validation Summary (NEW)

A comprehensive validation table combining:
- Alpha significance (HAC robust, 5% level)
- Diagnostic flags: Heteroskedasticity (Breusch-Pagan), Autocorrelation (Ljung-Box)
- Beta stability across sub-periods
- Normality test results
- Final validation statement per asset/return type

Results in: `capm_validation_summary.csv`

---

## Module Descriptions

### `00_config.py`
Defines paths (ROOT_DIR, DATA_DIR, REPORT_DIR, etc.), constants (TRADING_DAYS, ASSETS, HAC_LAGS), and helper functions:
- `ensure_dirs()` – Create output directories
- `file_exists(path)` – Check if file exists
- `should_generate(output_path, force=False)` – Determine if file should be regenerated

**FORCE_REBUILD flag:** Set to True in config to regenerate all outputs (default False, skips existing files).

### `01_load_and_clean.py`
- Loads data from CSV or Excel
- Cleans column names
- Standardizes asset names to uppercase (MSFT, GE, FORD)
- Parses dates
- Sorts by date
- Removes missing values
- **Main Function:** `load_and_clean(source='csv')`

### `02_returns_and_excess.py` (ENHANCED)
- Computes **both log and simple returns** for each asset and market
- Converts T-bill % to daily risk-free rate
- Computes excess returns for both types
- Saves intermediate CSV files (if requested):
  - `capm_excess_log.csv`
  - `capm_excess_simple.csv`
- **Main Function:** `compute_returns_and_excess(df, save_intermediate=True)`
- **Column Naming:**
  - Log: `{ASSET}_Excess`, `{ASSET}_Return_LOG`
  - Simple: `{ASSET}_Excess_SIMPLE`, `{ASSET}_Return_SIMPLE`

### `03_regressions.py`
- Runs OLS CAPM regression for each asset (uses log returns)
- Computes HAC (Newey-West) robust standard errors and p-values
- Outputs alpha, beta, p-values, R², and diagnostics
- Saves results to CSV:
  - `capm_regression_results_ols.csv`
  - `capm_regression_results_hac.csv`
- **Main Function:** `capm_regression_all_assets(df)` → returns (ols_df, hac_df, models_dict)

### `04_diagnostics.py`
Diagnostic tests on CAPM residuals:
- Breusch-Pagan test (heteroskedasticity)
- Durbin-Watson statistic
- Ljung-Box test (autocorrelation at lag 10)
- **Main Function:** `run_all_diagnostics(df, models)` → diagnostics_df
- **Output:** `capm_diagnostics.csv`

### `05_robustness.py`
Robustness checks on CAPM stability:
- Sub-period analysis (split data into periods, compute betas)
- Rolling window beta regression
- **Output:** `capm_subperiod_results.csv`, rolling beta plots

### `06_plots.py`
- Generates Security Characteristic Line scatter plots
- Shows excess returns with fitted regression line
- Saves as PNG (300 dpi)
- **Main Function:** `create_all_scatter_plots(df, models)` → list of paths

### `07_descriptive_stats.py`
- Computes descriptive statistics for each asset and market
- Mean, std, min, max, skew, kurtosis for excess returns
- **Output:** `descriptive_stats.csv`

### `08_master_summary.py`
- Builds comprehensive master summary combining all results
- **Output:** `capm_master_summary.csv`

### `09_residual_plots.py`
- Creates diagnostic plots for residuals:
  - Q-Q plots (normality)
  - Time series plots
  - ACF plots (autocorrelation)
  - Residuals vs fitted values

### `10_distribution_validation.py` (NEW)
Validates residual distributions for **both LOG and SIMPLE returns**:
- Fits CAPM OLS for each asset and return type
- Computes residual statistics: skew, kurtosis, excess kurtosis
- Jarque-Bera test (always)
- Shapiro-Wilk test (if N ≤ 5000)
- Creates interpretation strings
- **Main Function:** `run_distribution_validation(df)` → results_df
- **Output:** `residual_distribution_tests.csv`
- **Existence Check:** Appends new rows only if return type/asset combo doesn't exist

### `11_residual_histograms.py` (NEW)
Creates residual histograms for **both LOG and SIMPLE returns**:
- 50 bins per histogram
- Vertical line at residual mean (zero)
- Optional normal distribution PDF overlay
- **Main Function:** `create_all_residual_histograms(df)` → list of paths
- **Output:** 6 PNG files (3 assets × 2 return types)
  - `{ASSET}_residual_hist_LOG.png`
  - `{ASSET}_residual_hist_SIMPLE.png`
- **Existence Check:** Skips if PNG already exists

### `12_capm_validation_summary.py` (NEW)
Comprehensive CAPM validation combining results from all modules:
- Loads HAC regression results (log returns)
- Computes HAC results for simple returns (if not existing)
- Loads diagnostics, sub-period results, and distribution tests
- Builds validation table per asset and return type
- **Output:** `capm_validation_summary.csv` & `capm_regression_results_hac_SIMPLE.csv` (if computed)
- **Columns:**
  - Return_Type (LOG/SIMPLE)
  - Asset
  - Alpha_HAC, Alpha_p_HAC, Beta_HAC, R2
  - Heteroskedasticity_flag, Autocorr_flag, Normality_reject
  - Beta_stability_range
  - CAPM_validated_statement (interpretation)

### `13_fullperiod_summary.py` (NEW)
Creates explicit full-period (whole-sample, no breaks) regression outputs:
- Aliases full-sample regression results into clearly-named fullperiod files
- Uses `ensure_alias_output()` from utils_io to copy if destination missing
- Builds interpretation summary based on alpha significance (HAC p-value, 5% level)
- **Main Function:** `main()` → returns summary_df
- **Outputs:**
  - `capm_fullperiod_results_ols.csv` – Full-period OLS regression results (copy of capm_regression_results_ols.csv)
  - `capm_fullperiod_results_hac.csv` – Full-period HAC regression results (copy of capm_regression_results_hac.csv)
  - `capm_fullperiod_summary.csv` – Interpretation summary
- **Summary Columns:**
  - Asset
  - Alpha_HAC, Alpha_p_HAC, Beta_HAC, R2
  - Key_Interpretation ("Alpha not/significant → CAPM not/rejected... HAC used due to daily data diagnostics.")
- **FORCE_REBUILD Aware:** Skips aliasing unless files missing or FORCE_REBUILD=True

### `utils_io.py` (NEW)
File I/O utilities for the pipeline:
- **`ensure_alias_output(src_path, dst_path, force=None)`** – Copy source to destination if destination missing. Respects FORCE_REBUILD.
- **`file_exists(path)`** – Check if path is a file
- **`should_generate(output_path, force=None)`** – Determine if output should be regenerated
- Used by 13_fullperiod_summary.py and future modules to manage file caching

### `run_all.py`
Master pipeline that orchestrates all steps with existence checking (skips already-generated files unless FORCE_REBUILD=True):
1. Load and clean data
2. Compute log + simple returns and excess returns
3. Run CAPM regressions (log returns)
4. Compute descriptive statistics
5. **Build full-period regression outputs (NEW)**
6. Generate scatter plots
7. Run diagnostic tests
8. Run robustness checks (sub-period, rolling beta)
9. Build master summary table
10. Generate residual diagnostic plots
11. Distribution validation (LOG + SIMPLE return types)
12. Create residual histograms (LOG + SIMPLE return types)
13. Build CAPM validation summary (LOG + SIMPLE return types)


---

## Running Individual Modules

Each module has a `main()` function and can be run independently (for debugging):

```bash
# Load and clean data
python -c "from src.load_and_clean import main; main()"

# Compute returns
python -c "from src.returns_and_excess import main; main()"

# Run regressions
python -c "from src.regressions import main; main()"

# Generate plots
python -c "from src.plots import main; main()"
```

---

## Dependencies

- **pandas** – Data manipulation
- **numpy** – Numerical computing
- **statsmodels** – OLS regression and statistical tests
- **matplotlib** – Plotting
- **openpyxl** – Excel file reading

Full list in `requirements.txt`

---

## Expected Outputs

### `capm_regression_results.csv`
Summary table with columns:
- Asset
- Alpha (intercept)
- Alpha_PValue
- Alpha_Significant (boolean, 5% level)
- Beta (slope)
- Beta_PValue
- R_Squared
- Adj_R_Squared
- N_Obs (number of observations)

### `Msft_scatter.png`, `GE_scatter.png`, `Ford_scatter.png`
Security Characteristic Line plots with:
- Blue scatter points (observed excess returns)
- Red fitted regression line
- Labels and grid

---

## Notes

- **All paths are relative** and runnable from the repo root
- **No external data sources** – uses only provided CSV/Excel files
- **Reproducible by design** – same inputs always produce same outputs
- **Modular structure** – individual steps can be modified without affecting others
- **PEP 8 compliant** – clean, readable code

---

## Assignment Details

This project implements LP1 (Linear Programming / Quantitative Finance Exercise 1) from the MBA Mathematical Finance course.

**Model Specification:**
The CAPM regression: R_i* = α + β R_m* + ε

**Key Findings (1993-2003):**
- All three securities show insignificant alphas at the 5% level
- Securities are correctly priced under CAPM
- Betas vary by asset (MSFT ~1.24, GE ~1.24, FORD ~0.97)
- R² varies (MSFT higher, FORD lower), suggesting firm-specific risks

---

## Author Notes

- To regenerate all outputs, run `python -m src.run_all`
- **Do not manually edit** `report/tables/*.csv` or `report/figures/*.png`—they are generated outputs
- The notebook `LP1_Jupyter_clean.ipynb` is a reference; the Python pipeline is the reproducible source
- Figures are saved at 300 DPI for high-quality printing

---

## License

Internal use for educational purposes. Assignment submission: MBA Mathematical Finance & Engineering.

---

*Last updated: February 2026*
