import pandas as pd
import numpy as np

from risk_engine.portfolio import concentration_hhi, risk_contribution


def test_hhi():
    w = pd.Series([.5, .25, .25], index=["a", "b", "c"])
    assert abs(concentration_hhi(w) - .375) < 1e-12


def test_risk_contribution_sums():
    rng = np.random.default_rng(1)
    returns = pd.DataFrame(rng.normal(size=(500, 3)) * .01, columns=["a", "b", "c"])
    w = pd.Series([.4, .3, .3], index=["a", "b", "c"])
    rc = risk_contribution(returns, w)
    assert abs(rc["risk_contribution_pct"].sum() - 100) < 1e-8
