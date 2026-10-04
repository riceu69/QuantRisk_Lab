# Data

The project uses synthetic market data so it can be shared publicly without licensing or confidentiality concerns.

Run:

```bash
python -m risk_engine.data
```

This creates:

- `prices.csv`
- `portfolio.csv`

The synthetic universe contains equity, bond, FX and commodity-style assets with correlated returns and realistic-looking volatility regimes.
