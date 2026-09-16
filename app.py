from __future__ import annotations
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from etl import run_etl

st.set_page_config(
    page_title="Stock Price & P/E Ratio Chart",
    page_icon="📈",
    layout="wide"
)

st.markdown("""
    <style>
    .stApp {
        background-color: #131722;
        color: #D1D4DC;
    }
    </style>
""", unsafe_allow_html=True)


def main():
    st.title("📈 Stock Price & P/E Ratio Trend")

    st.sidebar.header("Filter Controls")
    preset_symbol = st.sidebar.selectbox("Select Stock Symbol",
                                         ["AAPL", "NVDA", "MSFT", "AMZN", "GOOGL", "TSLA", "Custom Symbol"])

    if preset_symbol == "Custom Symbol":
        symbol_input = st.sidebar.text_input("Enter Ticker Symbol", value="AMD").strip().upper()
    else:
        symbol_input = preset_symbol

    timeframe = st.sidebar.selectbox("Historical Timeframe", ["1y", "2y", "5y", "max"], index=1)

    if not symbol_input:
        st.info("Please select or enter a stock symbol in the sidebar.")
        return

    try:
        with st.spinner(f"Loading chart data for {symbol_input}..."):
            analyzed_df, metadata = run_etl(symbol_input, period=timeframe)
    except Exception as e:
        st.error(f"Could not load valid stock data for symbol {symbol_input}. Error: {e}")
        return

    if analyzed_df.empty:
        st.error(f"Could not load valid stock data for symbol {symbol_input}.")
        return

    latest_row = analyzed_df.iloc[-1]

    st.subheader(f"{metadata.get('name', symbol_input)} ({symbol_input})")
    col1, col2, col3 = st.columns(3)
    col1.metric("Stock Price", f"$" + f"{latest_row['Close']:,.2f}")
    col2.metric("Trailing P/E Ratio", f"{metadata.get('trailing_pe') if metadata.get('trailing_pe') else 'N/A'}")
    col3.metric("Forward P/E Ratio", f"{metadata.get('forward_pe') if metadata.get('forward_pe') else 'N/A'}")

    st.markdown("---")

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Scatter(
            x=analyzed_df['Date'],
            y=analyzed_df['Close'],
            name="Stock Price ($)",
            line=dict(color="#2962FF", width=2.5)
        ),
        secondary_y=False
    )

    if 'PE_Ratio' in analyzed_df.columns and not analyzed_df['PE_Ratio'].isnull().all():
        fig.add_trace(
            go.Scatter(
                x=analyzed_df['Date'],
                y=analyzed_df['PE_Ratio'],
                name="Trailing P/E Ratio",
                line=dict(color="#FF6D00", width=2, dash="dash")
            ),
            secondary_y=True
        )

    fig.update_layout(
        template="plotly_dark",
        height=550,
        hovermode="x unified",
        margin=dict(l=20, r=20, t=20, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    fig.update_yaxes(title_text="Stock Price ($)", secondary_y=False, gridcolor="#2A2E39")
    fig.update_yaxes(title_text="P/E Ratio (x)", secondary_y=True, showgrid=False)

    st.plotly_chart(fig, width='stretch')


if __name__ == "__main__":
    main()
