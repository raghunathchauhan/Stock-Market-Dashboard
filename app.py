
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="Stock Market Dashboard",
    page_icon="📈",
    layout="wide"
)

# Custom styling
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
    }
    div[data-testid="stMetric"] {
        background: #1e293b;
        padding: 18px;
        border-radius: 12px;
    }
</style>
""", unsafe_allow_html=True)

st.title("📈 Real-Time Stock Market Dashboard")
st.caption("Explore stock prices, historical trends and financial indicators.")

# Sidebar
st.sidebar.header("Stock Selection")

symbol = st.sidebar.text_input(
    "Enter Stock Symbol",
    value="AAPL"
).strip().upper()

period = st.sidebar.selectbox(
    "Select Time Period",
    ["1mo", "3mo", "6mo", "1y", "2y", "5y"],
    index=2
)

if st.sidebar.button("Fetch Stock Data"):
    st.session_state["refresh"] = True

# Fetch stock data
@st.cache_data(ttl=300)
def get_stock_data(ticker, selected_period):
    try:
        # Use yfinance to fetch historical stock prices
        stock = yf.Ticker(ticker)
        history = stock.history(period=selected_period)

        if history.empty:
            return pd.DataFrame(), {}

        # Use Requests API to fetch company information
        api_url = f"https://query1.finance.yahoo.com/v1/finance/search?q={ticker}"

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(
            api_url,
            headers=headers,
            timeout=10
        )
        response.raise_for_status()

        api_data = response.json()
        info = {}

        quotes = api_data.get("quotes", [])

        if quotes:
            company = quotes[0]
            info["longName"] = company.get("longname", ticker)
            info["currency"] = "USD"

        return history, info

    except Exception as error:
        st.error(f"Data fetching failed: {error}")
        return pd.DataFrame(), {}
if not symbol:
    st.warning("Please enter a valid stock symbol.")
    st.stop()

try:
    with st.spinner("Fetching stock market data..."):
        data, info = get_stock_data(symbol, period)

    if data.empty:
        st.error("No stock data found. Check the symbol and try again.")
        st.stop()

    # Financial calculations
    data["Moving Average (20)"] = data["Close"].rolling(20).mean()

    delta = data["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / avg_loss.replace(0, float("nan"))
    data["RSI"] = 100 - (100 / (1 + rs))

    latest_price = data["Close"].iloc[-1]
    previous_price = data["Close"].iloc[-2] if len(data) > 1 else latest_price
    change = latest_price - previous_price
    change_pct = (change / previous_price * 100) if previous_price else 0

    # Company information
    company_name = info.get("longName", symbol)
    currency = info.get("currency", "USD")

    st.subheader(f"{company_name} ({symbol})")

    # Metrics
    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Latest Available Price",
        f"{currency} {latest_price:,.2f}",
        f"{change_pct:.2f}%"
    )

    col2.metric(
        "Previous Close",
        f"{currency} {previous_price:,.2f}"
    )

    col3.metric(
        "20-Day Moving Average",
        f"{data['Moving Average (20)'].iloc[-1]:,.2f}"
        if pd.notna(data["Moving Average (20)"].iloc[-1])
        else "Not enough data"
    )

    col4.metric(
        "RSI (14)",
        f"{data['RSI'].iloc[-1]:.2f}"
        if pd.notna(data["RSI"].iloc[-1])
        else "Calculating..."
    )

    # Price chart
    st.subheader("Historical Stock Price")

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=data.index,
        y=data["Close"],
        mode="lines",
        name="Closing Price",
        line=dict(color="#38bdf8", width=2)
    ))

    fig.add_trace(go.Scatter(
        x=data.index,
        y=data["Moving Average (20)"],
        mode="lines",
        name="20-Day Moving Average",
        line=dict(color="#f59e0b", width=2)
    ))

    fig.update_layout(
        template="plotly_dark",
        xaxis_title="Date",
        yaxis_title=f"Price ({currency})",
        hovermode="x unified",
        height=480
    )

    st.plotly_chart(fig, width="stretch")

    # Volume chart
    st.subheader("Trading Volume")

    volume_fig = go.Figure()

    volume_fig.add_trace(go.Bar(
        x=data.index,
        y=data["Volume"],
        name="Volume",
        marker_color="#8b5cf6"
    ))

    volume_fig.update_layout(
        template="plotly_dark",
        xaxis_title="Date",
        yaxis_title="Volume",
        height=300
    )

    st.plotly_chart(volume_fig, width="stretch")

    # RSI chart
    st.subheader("Relative Strength Index (RSI)")

    rsi_fig = go.Figure()

    rsi_fig.add_trace(go.Scatter(
        x=data.index,
        y=data["RSI"],
        name="RSI",
        line=dict(color="#22c55e", width=2)
    ))

    rsi_fig.add_hline(y=70, line_dash="dash", line_color="red")
    rsi_fig.add_hline(y=30, line_dash="dash", line_color="green")

    rsi_fig.update_layout(
        template="plotly_dark",
        yaxis_title="RSI",
        yaxis_range=[0, 100],
        height=300
    )

    st.plotly_chart(rsi_fig, width="stretch")

    # Data table
    st.subheader("Historical Data")

    st.dataframe(
        data.tail(20).sort_index(ascending=False),
        width="stretch"
    )

    # CSV download
    csv_data = data.to_csv().encode("utf-8")

    st.download_button(
        label="Download Stock Data as CSV",
        data=csv_data,
        file_name=f"{symbol}_stock_data.csv",
        mime="text/csv"
    )

    st.caption(
        f"Last data point: {data.index[-1].strftime('%Y-%m-%d')}. "
        "Market data may be delayed. This dashboard is for educational use."
    )

except Exception as error:
    st.error(f"Unable to fetch stock data: {error}")
    st.info("Check your internet connection and stock symbol.")
