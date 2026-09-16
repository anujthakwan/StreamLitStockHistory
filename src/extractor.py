from __future__ import annotations
import os
import json
from datetime import datetime
import pandas as pd
import yfinance as yf
import logging
import requests

logging.basicConfig(level=logging.INFO)

# Determine directories relative to this file
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SRC_DIR)
RAW_DIR = os.path.join(PROJECT_ROOT, "data", "raw")


def extract_stock_data(symbol: str, period: str = "2y", cache_raw: bool = True) -> tuple[
    pd.DataFrame, dict, pd.Series | None]:
    """Extracts price history and quarterly EPS from Yahoo Finance."""
    
    # Create a custom session with a user-agent to avoid rate limiting
    session = requests.Session()
    session.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    
    ticker = yf.Ticker(symbol, session=session)
    
    logging.info(f"Fetching data for {symbol} with period {period}.")
    df = ticker.history(period=period)
    
    # Safely get ticker info, default to empty dict if it fails
    try:
        info = ticker.info
    except Exception:
        info = {}

    if df.empty:
        return pd.DataFrame(), {}, None

    df = df.reset_index()
    df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)

    # Extract Quarterly EPS for historical P/E trend computation
    quarterly_financials = None
    try:
        quarterly_financials = ticker.quarterly_financials
    except Exception:
        pass
        
    eps_series = None

    if quarterly_financials is not None and not quarterly_financials.empty:
        for key in ['Diluted EPS', 'Basic EPS']:
            if key in quarterly_financials.index:
                eps_series = quarterly_financials.loc[key].dropna()
                break

    metadata = {
        "symbol": symbol.upper(),
        "name": info.get("shortName", symbol.upper()) if info else symbol.upper(),
        "sector": info.get("sector", "N/A") if info else "N/A",
        "trailing_pe": info.get("trailingPE", None) if info else None,
        "forward_pe": info.get("forwardPE", None) if info else None,
        "extracted_at": datetime.now().isoformat()
    }

    if cache_raw:
        os.makedirs(RAW_DIR, exist_ok=True)
        raw_filepath = os.path.join(RAW_DIR, f"{symbol.lower()}_raw.json")
        with open(raw_filepath, "w") as f:
            json.dump({
                "metadata": metadata,
                "prices": df.astype(str).to_dict(orient="records")
            }, f, indent=2)

    return df, metadata, eps_series
