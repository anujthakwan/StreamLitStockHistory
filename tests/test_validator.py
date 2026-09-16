from __future__ import annotations
import pandas as pd
from src.validator import validate_dataframe


def test_validate_dataframe_valid():
    # Valid dataframe with at least 5 rows and positive Close prices
    df = pd.DataFrame({
        "Close": [10.0, 11.0, 12.0, 11.5, 13.0]
    })
    res = validate_dataframe(df)
    assert res["is_valid"] is True
    assert res["row_count"] == 5
    assert len(res["errors"]) == 0


def test_validate_dataframe_insufficient_rows():
    # Dataframe with less than 5 rows
    df = pd.DataFrame({
        "Close": [10.0, 11.0, 12.0]
    })
    res = validate_dataframe(df)
    assert res["is_valid"] is False
    assert "Insufficient rows returned." in res["errors"]


def test_validate_dataframe_missing_close():
    # Dataframe missing 'Close' column
    df = pd.DataFrame({
        "Open": [10.0, 11.0, 12.0, 13.0, 14.0]
    })
    res = validate_dataframe(df)
    assert res["is_valid"] is False
    assert "Missing 'Close' column." in res["errors"]


def test_validate_dataframe_negative_price():
    # Dataframe with a zero or negative Close price
    df = pd.DataFrame({
        "Close": [10.0, -1.0, 12.0, 11.5, 13.0]
    })
    res = validate_dataframe(df)
    assert res["is_valid"] is False
    assert "Found 1 invalid close prices." in res["errors"]
