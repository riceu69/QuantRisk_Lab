"""Stress and scenario analytics."""

import pandas as pd


def historical_stress_scenarios(
    returns: pd.DataFrame,
    weights: pd.Series,
    portfolio_value: float = 100.0,
    top_n: int = 10,
) -> pd.DataFrame:
    """Find historical worst portfolio return days."""
    w = weights.reindex(returns.columns).fillna(0.0)
    p = returns.mul(w, axis=1).sum(axis=1)
    worst = p.nsmallest(top_n)
    return pd.DataFrame({
        "date": worst.index,
        "portfolio_return": worst.values,
        "estimated_pnl": worst.values * portfolio_value,
    })


def hypothetical_stress(
    weights: pd.Series,
    shocks: dict,
    portfolio_value: float = 100.0,
) -> pd.DataFrame:
    """Apply deterministic asset shocks."""
    rows = []
    total_return = 0.0
    for asset, weight in weights.items():
        shock = shocks.get(asset, 0.0)
        contribution = weight * shock
        total_return += contribution
        rows.append({
            "asset": asset,
            "weight": weight,
            "shock": shock,
            "pnl": contribution * portfolio_value,
        })
    out = pd.DataFrame(rows)
    out.loc[len(out)] = {
        "asset": "TOTAL",
        "weight": weights.sum(),
        "shock": total_return,
        "pnl": total_return * portfolio_value,
    }
    return out
