# QuantRisk Lab

A Python-based portfolio risk analytics project covering **Value-at-Risk, Expected Shortfall, backtesting, stress testing, portfolio concentration, and risk contribution**.

The project is designed around a practical risk-analytics workflow: ingest market data and portfolio positions, calculate multiple risk measures, compare model outputs, investigate risk drivers, run adverse scenarios, and publish reproducible reports.

> **Data note:** The project uses synthetic market data generated locally. It is intended for learning and portfolio demonstration, not for production or regulatory use.

## What it does

- Calculates **Historical VaR**
- Calculates **Parametric VaR** under a normal-return assumption
- Calculates **Monte Carlo VaR**
- Calculates **Expected Shortfall (ES)**
- Performs rolling **VaR backtesting** and exception monitoring
- Measures portfolio **concentration (HHI)**
- Calculates **component risk contribution**
- Produces historical and hypothetical **stress-test scenarios**
- Tracks rolling portfolio volatility and asset correlations
- Generates an interactive **Streamlit dashboard**
- Exports an **Excel risk report** and CSV tables
- Includes unit tests for the core risk calculations

## Project structure

```text
QuantRisk-Lab/
├── app.py
├── run_analysis.py
├── requirements.txt
├── pyproject.toml
├── README.md
│
├── data/
│   ├── README.md
│   ├── portfolio.csv
│   └── prices.csv
│
├── risk_engine/
│   ├── __init__.py
│   ├── data.py
│   ├── metrics.py
│   ├── portfolio.py
│   ├── var.py
│   ├── backtest.py
│   ├── stress.py
│   └── reporting.py
│
├── tests/
│   ├── test_var.py
│   └── test_portfolio.py
│
├── docs/
│   └── data_dictionary.md
│
└── outputs/
    └── .gitkeep
```

## Methodology

### Value-at-Risk

For a confidence level \(c\), VaR estimates a loss threshold that should only be exceeded with probability \(1-c\) under the model assumptions.

Three approaches are implemented:

1. **Historical VaR** — uses the empirical distribution of observed portfolio losses.
2. **Parametric VaR** — estimates risk from the portfolio return mean and volatility under a normality assumption.
3. **Monte Carlo VaR** — simulates portfolio returns from estimated distribution parameters.

### Expected Shortfall

Expected Shortfall measures the average loss conditional on losses being beyond the VaR threshold. It provides additional information about the severity of tail losses.

### Backtesting

The rolling backtest compares realized portfolio losses with the model's historical VaR forecast. An exception occurs when realized loss exceeds the forecast VaR.

The dashboard reports the observed exception count against the expected count implied by the confidence level.

### Stress testing

Two forms of stress analysis are included:

- **Historical stress:** identifies the worst observed portfolio-return days.
- **Hypothetical stress:** applies user-defined shocks to individual portfolio assets and aggregates their P&L impact.

### Portfolio diagnostics

The project also measures:

- Portfolio weights
- Herfindahl-Hirschman concentration index
- Component risk contribution
- Rolling annualized volatility
- Asset return correlations

## Quick start

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd QuantRisk-Lab
```

### 2. Create a virtual environment

Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

Linux/macOS:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Generate the sample data

```bash
python -m risk_engine.data
```

### 5. Run the analysis pipeline

```bash
python run_analysis.py
```

The pipeline writes the generated Excel and CSV reports to `outputs/`. These files are intentionally ignored by Git.

### 6. Launch the dashboard

```bash
streamlit run app.py
```

### 7. Run tests

```bash
pytest -q
```

## Example workflow

```text
Market prices + portfolio positions
                │
                ▼
        Return calculation
                │
       ┌────────┼─────────┐
       ▼        ▼         ▼
 Historical  Parametric  Monte Carlo
    VaR         VaR         VaR
       └────────┼─────────┘
                ▼
       Expected Shortfall
                │
       ┌────────┴────────┐
       ▼                 ▼
   Backtesting       Stress Tests
       │                 │
       └────────┬────────┘
                ▼
       Risk diagnostics
                │
       ┌────────┴────────┐
       ▼                 ▼
    Dashboard         Reports
```

## Testing

The repository includes tests covering the core VaR calculations and portfolio risk-contribution logic.

Run:

```bash
pytest -q
```

## Design choices

The implementation intentionally keeps the core calculations separated from the UI and reporting layers:

- `risk_engine/var.py` contains VaR and Expected Shortfall models.
- `risk_engine/backtest.py` contains rolling VaR monitoring logic.
- `risk_engine/portfolio.py` contains exposure and risk-contribution calculations.
- `risk_engine/stress.py` contains scenario analysis.
- `risk_engine/reporting.py` handles report generation.
- `app.py` is only the presentation layer.

This separation makes individual calculations easier to test and extend.

## Limitations

This project is a research/learning implementation rather than a production risk engine. In a production environment, the methodology would require stronger controls around data quality, market-data lineage, model validation, model versioning, independent benchmarking, limit monitoring, audit trails, and treatment of non-linear instruments.

The Monte Carlo implementation is intentionally simple and assumes a fitted normal return process. A production implementation would typically need a more appropriate stochastic model and, for portfolios containing derivatives, full or approximate revaluation of the relevant instruments.

## Possible extensions

- Kupiec and Christoffersen VaR backtests
- Expected Shortfall backtesting
- GARCH volatility modelling
- Fat-tailed return distributions
- Factor-based risk decomposition
- Full historical P&L attribution
- Derivative pricing and Greeks
- FRTB-style Expected Shortfall calculations
- Database-backed market-data ingestion
- Model/version metadata and audit logs

## License

MIT License. See `LICENSE`.
