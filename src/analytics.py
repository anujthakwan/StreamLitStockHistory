from __future__ import annotations
import pandas as pd


def compute_price_and_pe_analytics(df: pd.DataFrame, eps_series: pd.Series | None) -> pd.DataFrame:
    """Computes daily price movement and aligns quarterly TTM EPS to generate a historical P/E curve."""
    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy().sort_values('Date')

    if eps_series is not None and len(eps_series) >= 4:
        eps_df = pd.DataFrame(eps_series).reset_index()
        eps_df.columns = ['Date', 'Quarterly_EPS']
        eps_df['Date'] = pd.to_datetime(eps_df['Date']).dt.tz_localize(None)
        eps_df = eps_df.sort_values('Date')

        # 4-quarter rolling sum to derive Trailing Twelve Months (TTM) EPS
        eps_df['TTM_EPS'] = eps_df['Quarterly_EPS'].rolling(window=4).sum()

        df = pd.merge_asof(
            df,
            eps_df[['Date', 'TTM_EPS']].dropna().sort_values('Date'),
            on='Date',
            direction='backward'
        )
        df['PE_Ratio'] = df['Close'] / df['TTM_EPS']
        df['PE_Ratio'] = df['PE_Ratio'].apply(lambda x: x if 0 < x < 500 else None)
    else:
        df['PE_Ratio'] = None

    return df
