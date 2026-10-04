"""Synthetic market and portfolio data generation."""

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"

ASSETS = [
    "US_Equity",
    "Tech_Equity",
    "Gov_Bond",
    "Corporate_Bond",
    "USD_INR",
    "Gold",
]


def generate_market_data(n_days: int = 1250, seed: int = 42) -> pd.DataFrame:
    """Generate a reproducible correlated synthetic daily price history."""
    if n_days < 252:
        raise ValueError("n_days must be at least 252 for a meaningful risk history")

    rng = np.random.default_rng(seed)
    vols = np.array([0.018, 0.024, 0.006, 0.009, 0.0045, 0.012])
    corr = np.array(
        [
            [1.00, 0.72, -0.18, -0.08, 0.10, 0.12],
            [0.72, 1.00, -0.20, -0.06, 0.12, 0.08],
            [-0.18, -0.20, 1.00, 0.55, -0.04, 0.10],
            [-0.08, -0.06, 0.55, 1.00, 0.02, 0.14],
            [0.10, 0.12, -0.04, 0.02, 1.00, 0.05],
            [0.12, 0.08, 0.10, 0.14, 0.05, 1.00],
        ]
    )

    covariance = np.outer(vols, vols) * corr
    cholesky = np.linalg.cholesky(covariance)
    innovations = rng.normal(size=(n_days, len(ASSETS))) @ cholesky.T

    # Two higher-volatility regimes make rolling risk measures and stress analysis
    # more informative while keeping the data fully synthetic.
    regime = np.ones(n_days)
    regime[int(n_days * 0.35) : int(n_days * 0.43)] = 1.70
    regime[int(n_days * 0.72) : int(n_days * 0.79)] = 1.45

    drifts = np.array([0.00030, 0.00038, 0.00008, 0.00012, 0.00003, 0.00018])
    returns = innovations * regime[:, None] + drifts
    prices = 100.0 * np.exp(np.cumsum(returns, axis=0))

    # Fixed end date keeps the sample reproducible across machines and runs.
    dates = pd.bdate_range(end="2026-09-30", periods=n_days)
    return pd.DataFrame(prices, index=dates, columns=ASSETS)


def generate_portfolio() -> pd.DataFrame:
    """Generate the example portfolio used by the analytics pipeline."""
    return pd.DataFrame(
        {
            "asset": ASSETS,
            "asset_class": [
                "Equity",
                "Equity",
                "Rates",
                "Credit",
                "FX",
                "Commodity",
            ],
            "position_value_cr": [38.0, 27.0, 18.0, 12.0, 10.0, 8.0],
        }
    )


def ensure_data() -> tuple[Path, Path]:
    """Create the sample data files if they are missing."""
    DATA_DIR.mkdir(exist_ok=True)
    prices_path = DATA_DIR / "prices.csv"
    portfolio_path = DATA_DIR / "portfolio.csv"

    if not prices_path.exists():
        generate_market_data().to_csv(prices_path, index_label="date")
    if not portfolio_path.exists():
        generate_portfolio().to_csv(portfolio_path, index=False)

    return prices_path, portfolio_path


if __name__ == "__main__":
    prices, portfolio = ensure_data()
    print(f"Market data: {prices}")
    print(f"Portfolio:   {portfolio}")
