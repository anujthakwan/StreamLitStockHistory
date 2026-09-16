from __future__ import annotations
import os
import shutil
import tempfile
import pandas as pd
from unittest.mock import patch, MagicMock
from etl import run_etl


def test_run_etl_pipeline():
    # Setup mock extracted data
    mock_df = pd.DataFrame({
        "Close": [10.0, 11.0, 12.0, 11.5, 13.0]
    }, index=pd.date_range("2026-01-01", periods=5))
    mock_df.index.name = "Date"
    
    mock_metadata = {
        "symbol": "MOCK",
        "name": "Mock Inc.",
        "sector": "Utilities",
        "trailing_pe": 15.0,
        "forward_pe": 14.0,
        "extracted_at": "2026-09-16T12:00:00"
    }
    
    mock_eps_series = pd.Series(
        data=[0.5, 0.6, 0.5, 0.7],
        index=pd.to_datetime(["2025-03-31", "2025-06-30", "2025-09-30", "2025-12-31"])
    )

    # Use temp dirs for caching
    temp_processed_dir = tempfile.mkdtemp()
    
    with patch("etl.extract_stock_data") as mock_extract, \
         patch("etl.PROCESSED_DIR", temp_processed_dir):
         
        mock_extract.return_value = (mock_df, mock_metadata, mock_eps_series)
        
        # Run the ETL pipeline
        processed_df, meta = run_etl("MOCK", period="2y", cache_raw=False)
        
        assert not processed_df.empty
        assert meta["symbol"] == "MOCK"
        assert "PE_Ratio" in processed_df.columns
        
        # Verify processed CSV was created
        csv_path = os.path.join(temp_processed_dir, "mock_processed.csv")
        assert os.path.exists(csv_path)
        
        loaded_df = pd.read_csv(csv_path)
        assert len(loaded_df) == 5

    # Cleanup
    shutil.rmtree(temp_processed_dir)
