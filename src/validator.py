from __future__ import annotations
import pandas as pd


def validate_dataframe(df: pd.DataFrame) -> dict:
    """Validates row presence and price sanity."""
    results = {"is_valid": True, "row_count": len(df), "errors": []}

    if df is None or df.empty or len(df) < 5:
        results["is_valid"] = False
        results["errors"].append("Insufficient rows returned.")
        return results

    if 'Close' not in df.columns:
        results["is_valid"] = False
        results["errors"].append("Missing 'Close' column.")
        return results

    invalid_prices = (df['Close'] <= 0).sum()
    if invalid_prices > 0:
        results["is_valid"] = False
        results["errors"].append(f"Found {invalid_prices} invalid close prices.")

    return results
