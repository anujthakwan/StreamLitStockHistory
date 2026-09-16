from __future__ import annotations
import pandas as pd
import numpy as np
from src.analytics import compute_price_and_pe_analytics


def test_compute_price_and_pe_analytics_empty():
    df = compute_price_and_pe_analytics(pd.DataFrame(), None)
    assert df.empty


def test_compute_price_and_pe_analytics_no_eps():
    dates = pd.date_range(start="2026-01-01", periods=5)
    df = pd.DataFrame({
        "Date": dates,
        "Close": [100.0, 102.0, 101.0, 105.0, 110.0]
    })
    res = compute_price_and_pe_analytics(df, None)
    assert "PE_Ratio" in res.columns
    assert res["PE_Ratio"].isnull().all()


def test_compute_price_and_pe_analytics_with_eps():
    # Setup stock price data for two years
    dates = pd.date_range(start="2025-01-01", end="2025-12-31", freq="D")
    df = pd.DataFrame({
        "Date": dates,
        "Close": [100.0] * len(dates)
    })

    # Setup quarterly EPS (at least 4 quarterly data points for TTM calculation)
    # yfinance dates are usually end of quarter or reporting dates, oldest to newest
    eps_series = pd.Series(
        data=[1.0, 1.5, 2.0, 2.5],
        index=pd.to_datetime(["2024-03-31", "2024-06-30", "2024-09-30", "2024-12-31"])
    )

    res = compute_price_and_pe_analytics(df, eps_series)

    # 4-quarter rolling sum of [1.0, 1.5, 2.0, 2.5] is 7.0
    # On or after 2024-12-31, TTM_EPS should align to 7.0
    assert "TTM_EPS" in res.columns
    assert "PE_Ratio" in res.columns

    # Since all close prices are 100.0 and TTM EPS is 7.0, P/E should be 100 / 7 = 14.2857...
    latest_row = res.iloc[-1]
    assert latest_row["TTM_EPS"] == 7.0
    assert np.isclose(latest_row["PE_Ratio"], 100.0 / 7.0)
