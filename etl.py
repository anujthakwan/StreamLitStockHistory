from __future__ import annotations
import os
import argparse
import pandas as pd
from src.extractor import extract_stock_data
from src.validator import validate_dataframe
from src.analytics import compute_price_and_pe_analytics

# Determine directories relative to this file
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
PROCESSED_DIR = os.path.join(PROJECT_ROOT, "data", "processed")


def run_etl(symbol: str, period: str = "2y", cache_raw: bool = True) -> tuple[pd.DataFrame, dict]:
    """Runs the full ETL pipeline for a given stock symbol and period.
    
    1. Extracts price and quarterly financials data.
    2. Validates raw prices.
    3. Computes daily price and P/E ratio historical curves.
    4. Caches processed analytical outputs.
    """
    symbol = symbol.upper()
    print(f"[*] Starting ETL pipeline for {symbol} (period: {period})...")

    # 1. Extraction
    df, metadata, eps_series = extract_stock_data(symbol, period=period, cache_raw=cache_raw)
    if df.empty:
        raise ValueError(f"No data returned for symbol: {symbol}")

    # 2. Validation
    validation_results = validate_dataframe(df)
    if not validation_results["is_valid"]:
        errors_str = "; ".join(validation_results["errors"])
        raise ValueError(f"Data validation failed for {symbol}: {errors_str}")

    # 3. Analytics / Computation
    processed_df = compute_price_and_pe_analytics(df, eps_series)

    # 4. Save Processed Data
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    
    # Save as CSV for transparency and broad compatibility
    csv_filename = f"{symbol.lower()}_processed.csv"
    csv_filepath = os.path.join(PROCESSED_DIR, csv_filename)
    processed_df.to_csv(csv_filepath, index=False)
    print(f"[+] Successfully saved processed CSV: {csv_filepath}")

    # Save as Parquet if pyarrow/fastparquet is available for fast retrieval
    try:
        import pyarrow
        parquet_filename = f"{symbol.lower()}_processed.parquet"
        parquet_filepath = os.path.join(PROCESSED_DIR, parquet_filename)
        processed_df.to_parquet(parquet_filepath, index=False)
        print(f"[+] Successfully saved processed Parquet: {parquet_filepath}")
    except ImportError:
        pass

    return processed_df, metadata


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run ETL Pipeline for Stock History Analytics.")
    parser.add_argument("--symbol", type=str, required=True, help="Stock ticker symbol (e.g., AAPL)")
    parser.add_argument("--period", type=str, default="2y", help="Lookback period (e.g., 1y, 2y, 5y, max)")
    parser.add_argument("--no-cache", action="store_true", help="Disable raw caching")

    args = parser.parse_args()

    try:
        df_processed, meta = run_etl(args.symbol, args.period, cache_raw=not args.no_cache)
        print("\n=== ETL RUN SUCCESSFUL ===")
        print(f"Symbol: {meta['symbol']}")
        print(f"Company: {meta['name']}")
        print(f"Sector: {meta['sector']}")
        print(f"Row count: {len(df_processed)}")
        print("==========================")
    except Exception as e:
        print(f"\n[!] ETL RUN FAILED: {e}")
