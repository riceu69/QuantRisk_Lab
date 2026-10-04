import numpy as np
import pandas as pd

from risk_engine.var import historical_var, parametric_var, monte_carlo_var


def test_historical_var_is_positive():
    r = pd.Series(np.array([-.02, -.01, 0.01, .015, -.03, .005]))
    result = historical_var(r, 100)
    assert result.var > 0
    assert result.expected_shortfall >= result.var


def test_parametric_var_is_positive():
    rng = np.random.default_rng(1)
    r = pd.Series(rng.normal(0, .01, 1000))
    result = parametric_var(r, 100)
    assert result.var > 0


def test_monte_carlo_is_positive():
    rng = np.random.default_rng(2)
    r = pd.Series(rng.normal(0, .01, 1000))
    result = monte_carlo_var(r, 100, simulations=5000)
    assert result.var > 0
