import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from risk_engine.data import ensure_data
from risk_engine.metrics import simple_returns, portfolio_returns, rolling_volatility
from risk_engine.portfolio import normalize_weights, exposure_summary, concentration_hhi, risk_contribution
from risk_engine.var import compare_var_models
from risk_engine.stress import historical_stress_scenarios, hypothetical_stress

st.set_page_config(
    page_title="QuantRisk Lab",
    page_icon="📊",
    layout="wide",
)

st.title("QuantRisk Lab")
st.caption("Portfolio Risk Analytics • VaR • Stress Testing • Model Monitoring")

prices_path, portfolio_path = ensure_data()
prices = pd.read_csv(prices_path, index_col=0, parse_dates=True)
portfolio = pd.read_csv(portfolio_path)

with st.sidebar:
    st.header("Model Controls")
    confidence = st.selectbox("VaR confidence", [0.90, 0.95, 0.99], index=1)
    lookback = st.slider("Lookback window", 100, len(prices), 500)
    portfolio_value = float(portfolio["position_value_cr"].sum())
    st.metric("Portfolio Value", f"₹{portfolio_value:.1f} Cr")

returns = simple_returns(prices).tail(lookback)
weights = normalize_weights(portfolio)
p_returns = portfolio_returns(returns, weights)

var_table = compare_var_models(p_returns, portfolio_value, confidence)
rc = risk_contribution(returns, weights)
exposure = exposure_summary(portfolio)
hhi = concentration_hhi(weights)

tab1, tab2, tab3, tab4 = st.tabs([
    "Executive Risk View",
    "VaR & Backtesting",
    "Stress Testing",
    "Portfolio Diagnostics",
])

with tab1:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Historical VaR", f"₹{var_table.iloc[0]['VaR']:.2f} Cr")
    c2.metric("Parametric VaR", f"₹{var_table.iloc[1]['VaR']:.2f} Cr")
    c3.metric("Monte Carlo VaR", f"₹{var_table.iloc[2]['VaR']:.2f} Cr")
    c4.metric("Concentration HHI", f"{hhi:.3f}")

    left, right = st.columns(2)
    with left:
        st.subheader("Portfolio exposure")
        fig = px.bar(
            exposure.sort_values("weight"),
            x="weight",
            y="asset",
            orientation="h",
            labels={"weight": "Portfolio Weight", "asset": ""},
        )
        fig.update_layout(xaxis_tickformat=".0%")
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.subheader("Risk contribution")
        fig = px.bar(
            rc.sort_values("risk_contribution_pct"),
            x="risk_contribution_pct",
            y="asset",
            orientation="h",
            labels={"risk_contribution_pct": "Risk Contribution (%)", "asset": ""},
        )
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("VaR model comparison")
    display = var_table.copy()
    display["VaR"] = display["VaR"].map(lambda x: f"₹{x:.3f} Cr")
    display["Expected Shortfall"] = display["Expected Shortfall"].map(lambda x: f"₹{x:.3f} Cr")
    st.dataframe(display, use_container_width=True, hide_index=True)

    st.subheader("Rolling 1-day Historical VaR")
    rolling = rolling_var_series(
        p_returns, window=250, confidence=confidence
    ).dropna()
    chart = pd.DataFrame({
        "VaR": rolling,
        "Loss": (-p_returns).reindex(rolling.index),
        "Exception": exception_series(p_returns, rolling).reindex(rolling.index),
    })
    fig = px.line(chart, labels={"value": "Loss / VaR Return", "index": "Date"})
    st.plotly_chart(fig, use_container_width=True)

    exceptions = int(chart["Exception"].sum())
    expected = len(chart) * (1 - confidence)
    st.info(
        f"Backtesting window: {len(chart)} observations | "
        f"Exceptions: {exceptions} | Expected: {expected:.1f}"
    )

with tab3:
    st.subheader("Historical stress days")
    hist = historical_stress_scenarios(returns, weights, portfolio_value, 10)
    hist["date"] = hist["date"].astype(str)
    st.dataframe(hist, use_container_width=True, hide_index=True)

    st.subheader("Hypothetical adverse scenario")
    shock_scale = st.slider("Shock severity", 0.5, 2.0, 1.0, 0.25)
    base_shocks = {
        "US_Equity": -0.15,
        "Tech_Equity": -0.20,
        "Gov_Bond": -0.05,
        "Corporate_Bond": -0.08,
        "USD_INR": 0.03,
        "Gold": 0.05,
    }
    shocks = {k: v * shock_scale for k, v in base_shocks.items()}
    scenario = hypothetical_stress(weights, shocks, portfolio_value)
    st.dataframe(scenario, use_container_width=True, hide_index=True)

    total_pnl = scenario.loc[scenario["asset"] == "TOTAL", "pnl"].iloc[0]
    st.metric("Scenario P&L", f"₹{total_pnl:.2f} Cr")

with tab4:
    st.subheader("Correlation matrix")
    corr = returns.corr()
    fig = px.imshow(
        corr,
        text_auto=".2f",
        aspect="auto",
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Rolling annualized portfolio volatility")
    vol = rolling_volatility(p_returns, 60).dropna()
    fig = px.line(vol, labels={"value": "Annualized Volatility", "index": "Date"})
    st.plotly_chart(fig, use_container_width=True)

st.divider()
st.caption(
    "Educational portfolio project. Synthetic data only. "
    "Production risk models require approved methodologies, validation, governance and controls."
)
