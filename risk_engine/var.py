"""Value-at-Risk and Expected Shortfall models."""

from dataclasses import dataclass
import numpy as np
import pandas as pd
from scipy.stats import norm


@dataclass
class RiskEstimate:
    var: float
    expected_shortfall: float
    confidence: float
    horizon_days: int
    method: str


def historical_var(
    portfolio_returns: pd.Series,
    portfolio_value: float,
    confidence: float = 0.95,
    horizon_days: int = 1,
) -> RiskEstimate:
    """Historical VaR using the empirical loss quantile."""
    losses = -portfolio_returns.dropna()
    q = float(np.quantile(losses, confidence))
    if horizon_days > 1:
        q *= np.sqrt(horizon_days)
    tail = losses[losses >= q]
    es = float(tail.mean()) if len(tail) else q
    return RiskEstimate(q * portfolio_value, es * portfolio_value, confidence, horizon_days, "Historical")


def parametric_var(
    portfolio_returns: pd.Series,
    portfolio_value: float,
    confidence: float = 0.95,
    horizon_days: int = 1,
) -> RiskEstimate:
    """Normal-distribution parametric VaR."""
    mu = portfolio_returns.mean()
    sigma = portfolio_returns.std(ddof=1)
    z = norm.ppf(confidence)
    loss = z * sigma - mu
    loss = max(loss, 0.0) * np.sqrt(horizon_days)
    # Expected shortfall under a normal model.
    phi_z = norm.pdf(z)
    es_loss = (sigma * phi_z / (1 - confidence) - mu) * np.sqrt(horizon_days)
    es_loss = max(es_loss, loss)
    return RiskEstimate(
        loss * portfolio_value,
        es_loss * portfolio_value,
        confidence,
        horizon_days,
        "Parametric-Normal",
    )


def monte_carlo_var(
    portfolio_returns: pd.Series,
    portfolio_value: float,
    confidence: float = 0.95,
    horizon_days: int = 1,
    simulations: int = 100_000,
    seed: int = 42,
) -> RiskEstimate:
    """Monte Carlo VaR under a fitted normal return process."""
    rng = np.random.default_rng(seed)
    mu = portfolio_returns.mean() * horizon_days
    sigma = portfolio_returns.std(ddof=1) * np.sqrt(horizon_days)
    simulated_returns = rng.normal(mu, sigma, simulations)
    losses = -simulated_returns
    var_loss = float(np.quantile(losses, confidence))
    tail = losses[losses >= var_loss]
    es_loss = float(tail.mean())
    return RiskEstimate(
        max(var_loss, 0) * portfolio_value,
        max(es_loss, var_loss, 0) * portfolio_value,
        confidence,
        horizon_days,
        "Monte-Carlo",
    )


def compare_var_models(
    portfolio_returns: pd.Series,
    portfolio_value: float,
    confidence: float = 0.95,
) -> pd.DataFrame:
    estimates = [
        historical_var(portfolio_returns, portfolio_value, confidence),
        parametric_var(portfolio_returns, portfolio_value, confidence),
        monte_carlo_var(portfolio_returns, portfolio_value, confidence),
    ]
    return pd.DataFrame([{
        "method": x.method,
        "VaR": x.var,
        "Expected Shortfall": x.expected_shortfall,
        "confidence": x.confidence,
        "horizon_days": x.horizon_days,
    } for x in estimates])
