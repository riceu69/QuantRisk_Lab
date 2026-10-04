"""Run the complete portfolio risk analysis pipeline."""

from pathlib import Path

import pandas as pd

from risk_engine.backtest import backtest_var
from risk_engine.data import ensure_data
from risk_engine.metrics import portfolio_returns, simple_returns
from risk_engine.portfolio import (
    concentration_hhi,
    exposure_summary,
    normalize_weights,
    risk_contribution,
)
from risk_engine.reporting import write_csv_bundle, write_excel_report
from risk_engine.stress import historical_stress_scenarios, hypothetical_stress
from risk_engine.var import compare_var_models, historical_var

ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "outputs"
CONFIDENCE = 0.95


def main() -> None:
    prices_path, portfolio_path = ensure_data()
    prices = pd.read_csv(prices_path, index_col=0, parse_dates=True)
    portfolio = pd.read_csv(portfolio_path)

    returns = simple_returns(prices)
    weights = normalize_weights(portfolio)
    portfolio_returns_series = portfolio_returns(returns, weights)
    portfolio_value = float(portfolio["position_value_cr"].sum())

    exposure = exposure_summary(portfolio)
    hhi = concentration_hhi(weights)
    var_table = compare_var_models(
        portfolio_returns_series, portfolio_value, CONFIDENCE
    )
    historical_estimate = historical_var(
        portfolio_returns_series, portfolio_value, CONFIDENCE
    )

    backtest = backtest_var(
        portfolio_returns_series,
        historical_estimate.var / portfolio_value,
        CONFIDENCE,
    )
    backtest_table = pd.DataFrame([backtest])

    risk_contribution_table = risk_contribution(returns, weights)
    historical_stress = historical_stress_scenarios(
        returns, weights, portfolio_value
    )

    scenario_shocks = {
        "US_Equity": -0.15,
        "Tech_Equity": -0.20,
        "Gov_Bond": -0.05,
        "Corporate_Bond": -0.08,
        "USD_INR": 0.03,
        "Gold": 0.05,
    }
    scenario_stress = hypothetical_stress(
        weights, scenario_shocks, portfolio_value
    )

    OUTPUT_DIR.mkdir(exist_ok=True)
    write_excel_report(
        OUTPUT_DIR / "quant_risk_report.xlsx",
        Exposure=exposure,
        VaR_Comparison=var_table,
        Backtest=backtest_table,
        Risk_Contribution=risk_contribution_table,
        Historical_Stress=historical_stress,
        Scenario_Stress=scenario_stress,
    )
    write_csv_bundle(
        OUTPUT_DIR,
        exposure=exposure,
        var_comparison=var_table,
        backtest=backtest_table,
        risk_contribution=risk_contribution_table,
        historical_stress=historical_stress,
        scenario_stress=scenario_stress,
    )

    print("\nQuantRisk Lab")
    print("-" * 40)
    print(f"Portfolio value : INR {portfolio_value:.2f} Cr")
    print(f"Portfolio HHI   : {hhi:.4f}")
    print(f"VaR confidence  : {CONFIDENCE:.0%}")
    print("\nVaR comparison")
    print(var_table[["method", "VaR", "Expected Shortfall"]].to_string(index=False))
    print("\nBacktest")
    print(backtest_table.to_string(index=False))
    print(f"\nReports written to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
