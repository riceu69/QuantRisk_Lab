"""Exposure, concentration and risk-contribution analytics."""

import numpy as np
import pandas as pd


def normalize_weights(portfolio: pd.DataFrame) -> pd.Series:
    total = portfolio["position_value_cr"].sum()
    return portfolio.set_index("asset")["position_value_cr"] / total


def exposure_summary(portfolio: pd.DataFrame) -> pd.DataFrame:
    out = portfolio.copy()
    total = out["position_value_cr"].sum()
    out["weight"] = out["position_value_cr"] / total
    return out.sort_values("weight", ascending=False)


def concentration_hhi(weights: pd.Series) -> float:
    """Herfindahl-Hirschman Index using decimal portfolio weights."""
    w = weights[weights > 0]
    return float((w ** 2).sum())


def risk_contribution(
    asset_returns: pd.DataFrame,
    weights: pd.Series,
    portfolio_value: float = 100.0,
) -> pd.DataFrame:
    """Variance-based marginal and component risk contribution."""
    w = weights.reindex(asset_returns.columns).fillna(0.0).to_numpy()
    cov = asset_returns.cov().to_numpy()
    sigma = float(np.sqrt(w @ cov @ w))
    if sigma == 0:
        mrc = np.zeros_like(w)
    else:
        mrc = (cov @ w) / sigma
    crc = w * mrc
    result = pd.DataFrame({
        "asset": asset_returns.columns,
        "weight": w,
        "marginal_risk": mrc,
        "component_risk": crc,
    })
    result["risk_contribution_pct"] = (
        result["component_risk"] / result["component_risk"].sum() * 100
        if result["component_risk"].sum() != 0 else 0
    )
    result["component_vol_pct"] = result["component_risk"] * 100
    return result.sort_values("risk_contribution_pct", ascending=False)
