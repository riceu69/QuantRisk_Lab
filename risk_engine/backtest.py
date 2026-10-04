"""VaR backtesting and exception diagnostics."""

import numpy as np
import pandas as pd


def backtest_var(
    portfolio_returns: pd.Series,
    var_return: float,
    confidence: float = 0.95,
) -> dict:
    """Compare realized losses with a fixed one-day VaR return threshold.

    Parameters
    ----------
    portfolio_returns:
        Realized daily portfolio returns.
    var_return:
        Positive VaR expressed as a fraction of portfolio value.
    confidence:
        VaR confidence level, e.g. 0.95.
    """
    if not 0 < confidence < 1:
        raise ValueError("confidence must be between 0 and 1")
    if var_return < 0:
        raise ValueError("var_return must be non-negative")

    losses = -portfolio_returns.dropna()
    exceptions = losses > var_return
    observations = len(losses)
    exception_count = int(exceptions.sum())
    expected_count = observations * (1 - confidence)
    exception_rate = exception_count / observations if observations else np.nan

    return {
        "observations": observations,
        "exceptions": exception_count,
        "exception_rate": exception_rate,
        "expected_exceptions": expected_count,
        "excess_exceptions": exception_count - expected_count,
        "status": (
            "Review required"
            if exception_count > expected_count * 1.5
            else "Within expected range"
        ),
    }


def rolling_var_series(
    returns: pd.Series,
    window: int = 250,
    confidence: float = 0.95,
) -> pd.Series:
    """Return rolling historical one-day VaR as a positive loss-return series."""
    if window < 30:
        raise ValueError("window must be at least 30 observations")
    if not 0 < confidence < 1:
        raise ValueError("confidence must be between 0 and 1")

    return (
        returns.rolling(window)
        .apply(lambda values: np.quantile(-values, confidence), raw=True)
        .rename("VaR")
    )


def exception_series(returns: pd.Series, rolling_var: pd.Series) -> pd.Series:
    """Flag days where realized loss exceeds the corresponding VaR forecast."""
    losses = -returns
    return (losses > rolling_var).fillna(False).astype(int).rename("exception")
