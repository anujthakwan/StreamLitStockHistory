from __future__ import annotations
import os
import shutil
import tempfile
import pandas as pd
from unittest.mock import MagicMock, patch
from src.extractor import extract_stock_data, RAW_DIR


def test_extract_stock_data():
    mock_df = pd.DataFrame({
        "Close": [100.0, 102.0, 101.0, 105.0, 110.0]
    }, index=pd.date_range("2026-01-01", periods=5))
    mock_df.index.name = "Date"  # Emulate yfinance index naming
    
    mock_info = {
        "shortName": "Test Inc.",
        "sector": "Technology",
        "trailingPE": 25.5,
        "forwardPE": 22.0
    }
    
    mock_quarterly_financials = pd.DataFrame(
        data={
            "2025-12-31": [1.5],
            "2025-09-30": [1.2],
            "2025-06-30": [1.0],
            "2025-03-31": [0.8]
        },
        index=["Diluted EPS"]
    )

    # Mock yfinance Ticker
    with patch("yfinance.Ticker") as mock_ticker_cls:
        mock_ticker = MagicMock()
        mock_ticker.history.return_value = mock_df
        mock_ticker.info = mock_info
        mock_ticker.quarterly_financials = mock_quarterly_financials
        mock_ticker_cls.return_value = mock_ticker

        # Use a temporary directory for raw caching to avoid polluting production data folder
        temp_raw_dir = tempfile.mkdtemp()
        with patch("src.extractor.RAW_DIR", temp_raw_dir):
            df, metadata, eps_series = extract_stock_data("TEST", period="2y", cache_raw=True)

            assert not df.empty
            assert metadata["symbol"] == "TEST"
            assert metadata["name"] == "Test Inc."
            assert metadata["sector"] == "Technology"
            assert metadata["trailing_pe"] == 25.5
            assert metadata["forward_pe"] == 22.0
            
            # Verify quarterly EPS
            assert eps_series is not None
            assert len(eps_series) == 4
            assert eps_series["2025-12-31"] == 1.5

            # Verify raw cache file is created
            cache_file = os.path.join(temp_raw_dir, "test_raw.json")
            assert os.path.exists(cache_file)

        # Cleanup
        shutil.rmtree(temp_raw_dir)
