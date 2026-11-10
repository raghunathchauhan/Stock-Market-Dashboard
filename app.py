import streamlit as st
import yfinance as yf
import requests
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import time

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="AlgoWinner01 | Market Terminal",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# DESIGN SYSTEM
# ---------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

:root {
    --bg: #080b12;
    --panel: #101722;
    --panel2: #141e2b;
    --line: rgba(148,163,184,.16);
    --muted: #91a0b5;
    --text: #edf2f8;
    --red: #ff405c;
    --green: #00d68f;
    --purple: #9b7bff;
}
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}
.stApp {
    background:
      radial-gradient(circle at 80% 0%, rgba(81,55,150,.16), transparent 28%),
      radial-gradient(circle at 8% 30%, rgba(0,160,130,.08), transparent 24%),
      var(--bg);
    color: var(--text);
}
[data-testid="stHeader"] { background: rgba(8,11,18,.88); }
.block-container { padding-top: 1.4rem; padding-bottom: 3rem; max-width: 1600px; }
h1, h2, h3 { font-family: 'Space Grotesk', sans-serif !important; letter-spacing: -.7px; }
h1 { font-size: 2.45rem !important; font-weight: 700 !important; }
h2 { font-size: 1.35rem !important; }
p, label, span { color: inherit; }
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1420 0%, #0a0e16 100%);
    border-right: 1px solid var(--line);
}
[data-testid="stSidebar"] .block-container { padding-top: 1.6rem; }
div[data-testid="stMetric"] {
    background: linear-gradient(145deg, #172232, #101722);
    border: 1px solid var(--line);
    padding: 17px 18px;
    border-radius: 16px;
    box-shadow: 0 10px 30px rgba(0,0,0,.16);
}
div[data-testid="stMetricLabel"] { color: #a8b5c7 !important; font-size: .82rem; }
div[data-testid="stMetricValue"] { color: #f5f7fb !important; font-family: 'Space Grotesk'; }
div[data-testid="stMetricDelta"] { font-weight: 600; }
div[data-testid="stButton"] button, div[data-testid="stDownloadButton"] button {
    border-radius: 10px;
    border: 1px solid rgba(155,123,255,.42);
    background: linear-gradient(100deg, #6d4aff, #a044ff);
    color: white;
    font-weight: 700;
}
div[data-testid="stButton"] button:hover, div[data-testid="stDownloadButton"] button:hover {
    border-color: #c0aaff;
    color: white;
    box-shadow: 0 0 22px rgba(155,123,255,.25);
}
div[data-testid="stTextInput"] input, div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
    background: #111a27;
    border-color: var(--line);
    border-radius: 10px;
}
hr { border-color: var(--line); }
.aw-brand {
    font-family: 'Space Grotesk';
    font-size: 1.15rem;
    font-weight: 700;
    padding: 8px 0 24px;
    color: #f4f7fb;
}
.aw-brand span { color: #ff405c; }
.eyebrow {
    color: #a9b6c8; text-transform: uppercase; letter-spacing: 2px;
    font-size: .68rem; font-weight: 700;
}
.hero-title {
    font-family: 'Space Grotesk'; font-size: clamp(2rem, 4vw, 3.2rem);
    font-weight: 700; line-height: 1.05; letter-spacing: -2px;
}
.hero-title span {
    background: linear-gradient(90deg, #fff 0%, #c3b2ff 48%, #ff536b 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.hero-sub { color: var(--muted); margin-top: 8px; }
.status-pill {
    display: inline-block; border: 1px solid rgba(0,214,143,.35);
    background: rgba(0,214,143,.08); color: #00e49a;
    border-radius: 30px; padding: 6px 11px; font-size: .76rem; font-weight: 700;
}
.panel {
    background: linear-gradient(145deg, rgba(20,30,43,.94), rgba(12,18,28,.96));
    border: 1px solid var(--line); border-radius: 17px; padding: 17px 18px;
}
.panel-title { font-family: 'Space Grotesk'; font-size: 1.05rem; font-weight: 700; }
.small-muted { color: var(--muted); font-size: .8rem; }
.positive { color: #00d68f; }
.negative { color: #ff536b; }
div[data-testid="stDataFrame"] { border: 1px solid var(--line); border-radius: 12px; }
footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# DATA HELPERS
# ---------------------------------------------------------
@st.cache_data(ttl=180, show_spinner=False)
def load_history(symbol: str, period: str, interval: str = "1d"):
    ticker = yf.Ticker(symbol)
    df = ticker.history(period=period, interval=interval, auto_adjust=True)
    if df is None or df.empty:
        return pd.DataFrame()
    df = df.dropna(subset=["Close"])
    return df

@st.cache_data(ttl=300, show_spinner=False)
@st.cache_data(ttl=300, show_spinner=False)
def search_stocks(query: str):
    if not query.strip():
        return []

    url = "https://query1.finance.yahoo.com/v1/finance/search"

    params = {
        "q": query,
        "quotesCount": 10,
        "newsCount": 0
    }

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=10
        )

        response.raise_for_status()
        results = response.json().get("quotes", [])

        stocks = []

        for item in results:
            symbol = item.get("symbol")
            name = item.get("shortname") or item.get("longname")

            if symbol and name:
                stocks.append({
                    "label": f"{name} ({symbol})",
                    "symbol": symbol
                })

        return stocks

    except (requests.RequestException, ValueError):
        return []
def load_company_name(symbol: str):
    try:
        info = yf.Ticker(symbol).get_info()
        return info.get("shortName") or info.get("longName") or symbol
    except Exception:
        return symbol

def money(value, currency="USD"):
    if pd.isna(value):
        return "—"
    return f"{currency} {value:,.2f}"

def add_indicators(df):
    out = df.copy()
    out["SMA 20"] = out["Close"].rolling(20).mean()
    out["SMA 50"] = out["Close"].rolling(50).mean()
    delta = out["Close"].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss.replace(0, float("nan"))
    out["RSI"] = 100 - (100 / (1 + rs))
    return out

def get_index_snapshot(symbol):
    try:
        df = load_history(symbol, "5d")
        if df.empty:
            return None
        latest = float(df["Close"].iloc[-1])
        previous = float(df["Close"].iloc[-2]) if len(df) > 1 else latest
        delta = latest - previous
        pct = (delta / previous * 100) if previous else 0
        return latest, delta, pct
    except Exception:
        return None

def format_large(value):
    if pd.isna(value):
        return "—"
    value = float(value)
    if abs(value) >= 1_000_000_000:
        return f"{value/1_000_000_000:.2f}B"
    if abs(value) >= 1_000_000:
        return f"{value/1_000_000:.2f}M"
    if abs(value) >= 1_000:
        return f"{value/1_000:.1f}K"
    return f"{value:,.0f}"

# ---------------------------------------------------------2
# SIDEBAR
# ---------------------------------------------------------
with st.sidebar:
    st.markdown('<div class="aw-brand">◢ <span>Algo</span>Winner01 <small style="color:#9aa8ba;font-size:.65rem">MARKET TERMINAL</small></div>', unsafe_allow_html=True)
    st.markdown("### MARKET WORKSPACE")
    st.caption("Live dashboard · Technical analysis · Watchlist")
    st.divider()
    st.markdown("### Market controls")
    stock_options = {
    "Apple (AAPL)": "AAPL",
    "Microsoft (MSFT)": "MSFT",
    "NVIDIA (NVDA)": "NVDA",
    "Tesla (TSLA)": "TSLA",
    "Amazon (AMZN)": "AMZN",
    "Google (GOOGL)": "GOOGL",
    "Meta (META)": "META",
    "Netflix (NFLX)": "NFLX",
    "AMD (AMD)": "AMD",
    "Reliance Industries": "RELIANCE.NS",
    "TCS": "TCS.NS",
    "Infosys": "INFY.NS",
    "HDFC Bank": "HDFCBANK.NS",
    "ICICI Bank": "ICICIBANK.NS",
    "State Bank of India": "SBIN.NS",
    "Tata Motors": "TMPV.NS",
    "ITC": "ITC.NS",
    "Bharti Airtel": "BHARTIARTL.NS",
}
st.markdown("### Search any company")

search_query = st.text_input(
    "Company name or ticker",
    placeholder="e.g. Apple, Reliance, NVIDIA"
)

if search_query:
    search_results = search_stocks(search_query)

    if search_results:
        selected_result = st.selectbox(
            "API search results",
            search_results,
            format_func=lambda x: x["label"]
        )
        api_symbol = selected_result["symbol"]
    else:
        api_symbol = None
        st.warning("No matching stocks found.")
else:
    api_symbol = None
selected_stock = st.selectbox(
    "Select stock",
    list(stock_options.keys())
)
symbol_input = api_symbol if api_symbol else stock_options[selected_stock]
period_label = st.selectbox(
    "Chart range",
    ["1 Month", "3 Months", "6 Months", "1 Year", "2 Years", "5 Years"],
    index=2
)

period_map = {
    "1 Month": "1mo",
    "3 Months": "3mo",
    "6 Months": "6mo",
    "1 Year": "1y",
    "2 Years": "2y",
    "5 Years": "5y"
}

period = period_map[period_label]

st.caption("Data source: Yahoo Finance via yfinance")
st.caption("Quotes can be delayed. Not investment advice.")
symbol = symbol_input
# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------
top_left, top_right = st.columns([5, 1])
with top_left:
    st.markdown('<div class="eyebrow">MARKET INTELLIGENCE PLATFORM</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-title">Stock Market <span>Dashboard</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Real-time market data · Technical analysis · Smarter decisions</div>', unsafe_allow_html=True)
with top_right:
    st.markdown('<div style="text-align:right;padding-top:12px"><span class="status-pill">● DATA CONNECTED</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="small-muted" style="text-align:right;margin-top:8px">{datetime.now().strftime("%d %b %Y · %I:%M %p")}</div>', unsafe_allow_html=True)

st.write("")

# ---------------------------------------------------------
# MARKET INDEX CARDS - REAL YAHOO FINANCE DATA
# ---------------------------------------------------------
st.markdown('<div class="eyebrow">INDIAN MARKET PULSE</div>', unsafe_allow_html=True)
indices = [
    ("NIFTY 50", "^NSEI"),
    ("SENSEX", "^BSESN"),
    ("BANK NIFTY", "^NSEBANK"),
    ("INDIA VIX", "^INDIAVIX"),
]
index_cols = st.columns(4)
for col, (label, ticker) in zip(index_cols, indices):
    with col:
        with st.spinner(f"Loading {label}"):
            snap = get_index_snapshot(ticker)
        if snap:
            val, delta, pct = snap
            col.metric(label, f"{val:,.2f}", f"{delta:+,.2f} ({pct:+.2f}%)")
        else:
            col.metric(label, "Unavailable", "Data feed unavailable")

st.write("")

# ---------------------------------------------------------
# MAIN STOCK DATA
# ---------------------------------------------------------
with st.spinner(f"Fetching {symbol} market data..."):
    raw_data = load_history(symbol, period)

if raw_data.empty:
    st.error(f"No market data returned for **{symbol}**. Check the ticker symbol and try again.")
    st.info("Examples: AAPL, MSFT, NVDA, TSLA, RELIANCE.NS, TCS.NS, INFY.NS")
    st.stop()

data = add_indicators(raw_data)
company_name = load_company_name(symbol)
currency = "INR" if symbol.endswith(".NS") or symbol.endswith(".BO") else "USD"
latest = float(data["Close"].iloc[-1])
previous = float(data["Close"].iloc[-2]) if len(data) > 1 else latest
change = latest - previous
change_pct = (change / previous * 100) if previous else 0
sma20 = data["SMA 20"].iloc[-1]
sma50 = data["SMA 50"].iloc[-1]
rsi = data["RSI"].iloc[-1]
volume = data["Volume"].iloc[-1] if "Volume" in data else float("nan")

# Company / quote strip
st.markdown(f"""
<div class="panel" style="margin-bottom:14px">
  <div style="display:flex;justify-content:space-between;align-items:center;gap:16px;flex-wrap:wrap">
    <div>
      <div class="eyebrow">SELECTED ASSET</div>
      <div style="font-family:Space Grotesk;font-size:1.55rem;font-weight:700;margin-top:4px">{company_name} <span style="color:#9ba9bb;font-size:1rem">({symbol})</span></div>
    </div>
    <div style="text-align:right">
      <div style="font-family:Space Grotesk;font-size:1.8rem;font-weight:700">{money(latest, currency)}</div>
      <div class="{'positive' if change_pct >= 0 else 'negative'}" style="font-weight:700">{change:+,.2f} ({change_pct:+.2f}%) <span style="color:#91a0b5;font-weight:400">vs previous close</span></div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

metric_cols = st.columns(5)
metric_cols[0].metric("Latest price", money(latest, currency), f"{change_pct:+.2f}%")
metric_cols[1].metric("Previous close", money(previous, currency))
metric_cols[2].metric("SMA · 20", f"{sma20:,.2f}" if pd.notna(sma20) else "Calculating")
metric_cols[3].metric("RSI · 14", f"{rsi:.2f}" if pd.notna(rsi) else "Calculating")
metric_cols[4].metric("Latest volume", format_large(volume))

st.write("")

# ---------------------------------------------------------
# CHART CONTROLS
# ---------------------------------------------------------
chart_col, insight_col = st.columns([2.15, 1])
with chart_col:
    st.markdown('<div class="panel-title">Price action & technicals</div>', unsafe_allow_html=True)
    chart_options = st.columns(4)
    show_sma20 = chart_options[0].checkbox("SMA 20", value=True)
    show_sma50 = chart_options[1].checkbox("SMA 50", value=True)
    show_volume = chart_options[2].checkbox("Volume", value=True)
    chart_type = chart_options[3].selectbox("Chart", ["Candlestick", "Line"], label_visibility="collapsed")

    fig = make_subplots(
        rows=2 if show_volume else 1, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.06,
        row_heights=[0.74, 0.26] if show_volume else [1],
    )
    if chart_type == "Candlestick":
        fig.add_trace(go.Candlestick(
            x=data.index, open=data["Open"], high=data["High"],
            low=data["Low"], close=data["Close"], name="Price",
            increasing_line_color="#00d68f", decreasing_line_color="#ff536b",
            increasing_fillcolor="#00d68f", decreasing_fillcolor="#ff536b"
        ), row=1, col=1)
    else:
        fig.add_trace(go.Scatter(
            x=data.index, y=data["Close"], name="Close",
            line=dict(color="#7c8cff", width=2.5),
            fill="tozeroy", fillcolor="rgba(124,140,255,.08)"
        ), row=1, col=1)

    if show_sma20:
        fig.add_trace(go.Scatter(
            x=data.index, y=data["SMA 20"], name="SMA 20",
            line=dict(color="#a78bfa", width=1.8)
        ), row=1, col=1)
    if show_sma50:
        fig.add_trace(go.Scatter(
            x=data.index, y=data["SMA 50"], name="SMA 50",
            line=dict(color="#f7a94b", width=1.8)
        ), row=1, col=1)
    if show_volume and "Volume" in data:
        colors = ["#00b982" if c >= o else "#e94b65" for c, o in zip(data["Close"], data["Open"])]
        fig.add_trace(go.Bar(
            x=data.index, y=data["Volume"], name="Volume",
            marker_color=colors, opacity=.75
        ), row=2, col=1)

    fig.update_layout(
        template="plotly_dark", height=510 if show_volume else 430,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=8, r=8, t=20, b=8),
        font=dict(family="DM Sans", color="#cbd5e1"),
        legend=dict(orientation="h", y=1.08, x=0),
        hovermode="x unified",
        xaxis_rangeslider_visible=False,
    )
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(gridcolor="rgba(148,163,184,.12)", zeroline=False)
    st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False, "scrollZoom": True})

with insight_col:
    st.markdown('<div class="panel-title">Technical snapshot</div>', unsafe_allow_html=True)
    if pd.notna(rsi):
        if rsi >= 70:
            rsi_label, rsi_color = "Overbought zone", "#ff536b"
        elif rsi <= 30:
            rsi_label, rsi_color = "Oversold zone", "#00d68f"
        else:
            rsi_label, rsi_color = "Neutral momentum", "#a78bfa"
    else:
        rsi_label, rsi_color = "Insufficient data", "#91a0b5"

    rsi_display = f"{rsi:.1f}" if pd.notna(rsi) else "—"
    sma20_display = f"{sma20:,.2f}" if pd.notna(sma20) else "—"
    st.markdown(f"""
    <div class="panel" style="margin-top:12px">
      <div class="eyebrow">RSI MOMENTUM</div>
      <div style="font-size:2.2rem;font-family:Space Grotesk;font-weight:700">{rsi_display}</div>
      <div style="color:{rsi_color};font-weight:700">{rsi_label}</div>
      <div style="height:8px;background:#263244;border-radius:20px;margin-top:13px;overflow:hidden">
        <div style="width:{max(0,min(100,float(rsi) if pd.notna(rsi) else 0))}%;height:100%;background:linear-gradient(90deg,#00d68f,#a78bfa,#ff536b);border-radius:20px"></div>
      </div>
      <div class="small-muted" style="margin-top:8px">Below 30: oversold · Above 70: overbought</div>
    </div>
    """, unsafe_allow_html=True)

    trend = "Above" if pd.notna(sma20) and latest > sma20 else "Below"
    trend_color = "#00d68f" if trend == "Above" else "#ffb454"
    st.markdown(f"""
    <div class="panel" style="margin-top:12px">
      <div class="eyebrow">MOVING AVERAGE CHECK</div>
      <div style="font-size:1.25rem;font-weight:700;color:{trend_color};margin:8px 0">{trend} 20-day SMA</div>
      <div class="small-muted">Price: {latest:,.2f}</div>
      <div class="small-muted">SMA 20: {sma20_display}</div>
    </div>
    """, unsafe_allow_html=True)

    if pd.notna(sma20) and pd.notna(sma50):
        if sma20 > sma50:
            signal = "Short-term average is above long-term average."
            signal_tag = "Positive trend structure"
        else:
            signal = "Short-term average is below long-term average."
            signal_tag = "Negative trend structure"
    else:
        signal = "More historical data is needed to compare moving averages."
        signal_tag = "Not enough data"

    st.markdown(f"""
    <div class="panel" style="margin-top:12px">
      <div class="eyebrow">RULE-BASED MARKET NOTE</div>
      <div style="font-weight:700;margin:8px 0">{signal_tag}</div>
      <div class="small-muted">{signal}</div>
      <div class="small-muted" style="margin-top:10px">This is a simple indicator summary, not AI-generated advice or a buy/sell recommendation.</div>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# WATCHLIST / MARKET MOVERS
# ---------------------------------------------------------
st.write("")
left, right = st.columns([1.2, 1])
with left:
    st.markdown('<div class="panel-title">Market watchlist</div>', unsafe_allow_html=True)
    watchlist = [
        ("AAPL", "Apple"), ("MSFT", "Microsoft"), ("NVDA", "NVIDIA"),
        ("TSLA", "Tesla"), ("RELIANCE.NS", "Reliance"), ("TCS.NS", "TCS"),
    ]
    rows = []
    with st.spinner("Loading watchlist quotes..."):
        for ticker, name in watchlist:
            try:
                hist = load_history(ticker, "5d")
                if hist.empty:
                    continue
                last = float(hist["Close"].iloc[-1])
                prev = float(hist["Close"].iloc[-2]) if len(hist) > 1 else last
                pct = ((last - prev) / prev * 100) if prev else 0
                rows.append({"Symbol": ticker, "Company": name, "Last price": round(last, 2), "Change %": round(pct, 2)})
            except Exception:
                pass
    if rows:
        watch_df = pd.DataFrame(rows)
        st.dataframe(
            watch_df.style.format({"Last price": "{:,.2f}", "Change %": "{:+.2f}%"}),
            use_container_width=True, hide_index=True
        )
    else:
        st.info("Watchlist data is temporarily unavailable.")

with right:
    st.markdown('<div class="panel-title">Price range overview</div>', unsafe_allow_html=True)
    high = float(data["High"].max())
    low = float(data["Low"].min())
    avg = float(data["Close"].mean())
    st.metric("Period high", money(high, currency))
    st.metric("Period low", money(low, currency))
    st.metric("Period average close", money(avg, currency))

# ---------------------------------------------------------
# RSI + DATA TABLE + DOWNLOAD
# ---------------------------------------------------------
st.write("")
st.markdown('<div class="panel-title">Momentum & historical records</div>', unsafe_allow_html=True)
rsi_fig = go.Figure()
rsi_fig.add_trace(go.Scatter(
    x=data.index, y=data["RSI"], mode="lines", name="RSI (14)",
    line=dict(color="#a78bfa", width=2.2),
    fill="tozeroy", fillcolor="rgba(167,139,250,.08)"
))
rsi_fig.add_hline(y=70, line_dash="dash", line_color="#ff536b", annotation_text="Overbought 70")
rsi_fig.add_hline(y=30, line_dash="dash", line_color="#00d68f", annotation_text="Oversold 30")
rsi_fig.update_layout(
    template="plotly_dark", height=250, margin=dict(l=8,r=8,t=20,b=8),
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    yaxis=dict(range=[0,100], gridcolor="rgba(148,163,184,.12)"),
    xaxis=dict(showgrid=False), font=dict(color="#cbd5e1"),
)
st.plotly_chart(rsi_fig, use_container_width=True, config={"displaylogo": False})

with st.expander("View latest historical records"):
    display_cols = [c for c in ["Open", "High", "Low", "Close", "Volume", "SMA 20", "SMA 50", "RSI"] if c in data.columns]
    st.dataframe(data[display_cols].tail(30).sort_index(ascending=False), use_container_width=True)

csv_bytes = data.to_csv().encode("utf-8")
st.download_button(
    "⬇ Download historical data (CSV)",
    data=csv_bytes,
    file_name=f"{symbol.replace('.', '_')}_{period}_market_data.csv",
    mime="text/csv"
)

st.divider()
st.markdown(
    '<div class="small-muted">AlgoWinner01 Market Terminal · Built with Python, Streamlit, Plotly and Yahoo Finance. '
    'Market data may be delayed or unavailable. This dashboard is for educational purposes only and is not financial advice.</div>',
    unsafe_allow_html=True
)
