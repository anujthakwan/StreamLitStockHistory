# StreamLitStockHistory

A modularized, production-grade Streamlit application for analyzing stock price history and Trailing Twelve Months (TTM) P/E ratio trends.

## Project Structure

StreamLitStockHistory/
├── app.py                     # Streamlit frontend (visualization layer)
├── etl.py                     # ETL Pipeline (CLI & orchestration)
├── src/                       # Domain-specific modules
│   ├── extractor.py           # Data extraction from yfinance
│   ├── validator.py           # Data quality validation
│   └── analytics.py           # P/E trend computation (TTM EPS)
├── data/                      # Data storage
│   ├── raw/                   # Raw API extracts
│   └── processed/             # Processed analytical outputs (CSV/Parquet)
├── tests/                     # Test suite
│   └── ...                    # Unit and integration tests
└── README.md                  # This file

## Setup & Execution

### Prerequisites
- Python 3.13+
- pip

### Installation
1. Clone the repository.
2. Install dependencies:
   pip install -r requirements.txt

### Running the Application
The Streamlit app automatically invokes the ETL pipeline.
streamlit run app.py

### Running the ETL Pipeline (CLI)
You can run the ETL pipeline independently for a specific ticker:
python etl.py --symbol AAPL --period 2y

### Testing
Run the full test suite using pytest:
pytest
