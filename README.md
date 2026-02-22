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
│   ├── 00_config.py                   # Configuration and paths
│   ├── 01_load_and_clean.py           # Data loading and cleaning
│   ├── 02_returns_and_excess.py       # Return and excess return computation
│   ├── 03_regressions.py              # CAPM OLS regression analysis
│   ├── 04_diagnostics.py              # Diagnostic tests (TODO)
│   ├── 05_robustness.py               # Robustness checks (TODO)
│   ├── 06_plots.py                    # Scatter plots and visualization
│   └── run_all.py                     # Master pipeline orchestrator
│
├── notebooks/                         # Jupyter notebooks
│   └── LP1_Jupyter_clean.ipynb        # Cleaned analysis notebook
│
└── report/                            # Analysis outputs
    ├── LP1_CAPM_Report_Scaffold.md    # Report template
    ├── tables/                        # Output tables (CSV)
    │   └── capm_regression_results.csv
    └── figures/                       # Output figures (PNG)
        ├── Msft_scatter.png
        ├── GE_scatter.png
        └── Ford_scatter.png
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

After running the pipeline, check:

- **Regression Results Table:** `report/tables/capm_regression_results.csv`
- **Scatter Plots:** `report/figures/Msft_scatter.png`, `report/figures/GE_scatter.png`, `report/figures/Ford_scatter.png`

---

## Analysis Overview

### Data
- **Source:** Daily closing prices and T-bill rates (1993-2003)
- **Assets:** Microsoft (MSFT), General Electric (GE), Ford Motor (FORD)
- **Market Index:** S&P 500
- **Trading Days:** 252 per year

### Methodology

**Daily Log Returns:**
$$R_t = \ln\left(\frac{P_t}{P_{t-1}}\right)$$

**Daily Risk-Free Rate:**
$$R_f^{daily} = \frac{\text{T-bill annual rate}}{100} / 252$$

**Excess Returns:**
$$R^{excess} = R - R_f^{daily}$$

**CAPM Regression:**
$$R_i^{excess} = \alpha + \beta \cdot R_m^{excess} + \epsilon$$

### Hypothesis Test

- **H₀:** α = 0 (Security is correctly priced)
- **H₁:** α ≠ 0 (Security is mispriced)
- **Significance Level:** 5%

---

## Module Descriptions

### `00_config.py`
Defines paths (ROOT_DIR, DATA_DIR, REPORT_DIR, etc.), constants (TRADING_DAYS, ASSETS), and helper functions.

### `01_load_and_clean.py`
- Loads data from CSV or Excel
- Cleans column names
- Parses dates
- Sorts by date
- Removes missing values
- **Main Function:** `load_and_clean(source='csv')`

### `02_returns_and_excess.py`
- Computes daily log returns using: R_t = ln(P_t / P_{t-1})
- Converts T-bill % to daily rate
- Computes excess returns
- **Main Function:** `compute_returns_and_excess(df)`

### `03_regressions.py`
- Runs OLS CAPM regression for each asset
- Outputs alpha, beta, p-values, R², and test statistics
- Saves results to CSV
- **Main Function:** `capm_regression_all_assets(df)` → returns (results_df, models_dict)

### `04_diagnostics.py`
Placeholder for diagnostic tests (TODO):
- Residual normality (Jarque-Bera)
- Heteroskedasticity (Breusch-Pagan)
- Autocorrelation (Durbin-Watson)

### `05_robustness.py`
Placeholder for robustness checks (TODO):
- Rolling window regression
- Sub-period analysis
- Robust regression

### `06_plots.py`
- Generates Security Characteristic Line plots
- Shows scatter of excess returns with fitted regression line
- Saves as PNG (300 dpi)
- **Main Function:** `create_all_scatter_plots(df, models)`

### `run_all.py`
Master pipeline script that runs all steps in sequence and reports outputs.

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
