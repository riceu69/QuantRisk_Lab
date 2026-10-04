"""Portfolio and statistical metrics."""

import numpy as np
import pandas as pd


def simple_returns(prices: pd.DataFrame) -> pd.DataFrame:
    return prices.pct_change().dropna()


def log_returns(prices: pd.DataFrame) -> pd.DataFrame:
    return np.log(prices / prices.shift(1)).dropna()


def annualized_volatility(returns: pd.Series, periods: int = 252) -> float:
    return float(returns.std(ddof=1) * np.sqrt(periods))


def portfolio_returns(asset_returns: pd.DataFrame, weights: pd.Series) -> pd.Series:
    weights = weights.reindex(asset_returns.columns).fillna(0.0)
    return asset_returns.mul(weights, axis=1).sum(axis=1)


def covariance_matrix(asset_returns: pd.DataFrame, annualize: bool = False) -> pd.DataFrame:
    cov = asset_returns.cov()
    return cov * 252 if annualize else cov


def rolling_volatility(returns: pd.Series, window: int = 60) -> pd.Series:
    return returns.rolling(window).std() * np.sqrt(252)


def correlation_matrix(returns: pd.DataFrame) -> pd.DataFrame:
    return returns.corr()
