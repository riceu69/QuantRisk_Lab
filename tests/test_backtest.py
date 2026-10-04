import numpy as np
import pandas as pd

from risk_engine.backtest import backtest_var, exception_series, rolling_var_series


def test_backtest_counts_exceptions():
    returns = pd.Series([-0.01, -0.06, 0.01, -0.02, -0.08])
    result = backtest_var(returns, var_return=0.05, confidence=0.95)
    assert result["observations"] == 5
    assert result["exceptions"] == 2


def test_rolling_var_and_exception_series():
    returns = pd.Series(np.array([-0.01, -0.02, 0.01, -0.03] * 20))
    var = rolling_var_series(returns, window=30, confidence=0.95)
    exceptions = exception_series(returns, var)
    assert var.notna().sum() > 0
    assert set(exceptions.dropna().unique()).issubset({0, 1})
