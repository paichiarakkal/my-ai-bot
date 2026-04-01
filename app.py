import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd

# 1. Page Config (Dark Theme & Mobile Look)
st.set_page_config(page_title="FTB PRO TERMINAL", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #131722; color: white; }
    .stSidebar { background-color: #171b26; border-right: 1px solid #2a2e39; }
    header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: WATCHLIST & TOOLS ---
st.sidebar.title("📑 Watchlist")

# നിഫ്റ്റിയിലെ പ്രധാന സ്റ്റോക്കുകൾ (ഇത് എല്ലാം വർക്ക് ആകും)
watchlist = {
    "NIFTY 50": "^NSEI",
    "BANK NIFTY": "^NSEBANK",
    "CRUDE OIL": "CL=F",
    "RELIANCE": "RELIANCE.NS",
    "SBIN": "SBIN.NS",
    "TATA MOTORS": "TATAMOTORS.NS",
    "ADANI PORTS": "ADANIPORTS.NS"
}

selected_name = st.sidebar.selectbox("Select Asset", list(watchlist.keys()))
ticker = watchlist[selected_name]

# ഇന്റർവൽ സെലക്ഷൻ
interval = st.sidebar.radio("Timeframe", ["1m", "5m", "15m", "1h", "1d"], index=1)

# ഇൻഡിക്കേറ്ററുകൾ വേണോ എന്ന് തീരുമാനിക്കാം
show_st = st.sidebar.checkbox("Show Supertrend", value=True)

# --- CHART LOGIC ---
def get_data(symbol, inter):
    df = yf.download(symbol, period="5d", interval=inter, multi_level_index=False)
    return df

try:
    df = get_data(ticker, interval)
    
    if not df.empty:
        # Supertrend Calculation (Simple Logic for the App)
        if show_st:
            atr = (df['High'] - df['Low']).rolling(10).mean()
            df['ST_Upper'] = ((df['High'] + df['Low']) / 2) + (3 * atr)
            df['ST_Lower'] = ((df['High'] + df['Low']) / 2) - (3 * atr)

        # മനോഹരമായ ചാർട്ട് നിർമ്മാണം (43641.jpg ലുക്ക്)
        fig = go.Figure(data=[go.Candlestick(
            x=df.index,
            open=df['Open'], high=df['High'],
            low=df['Low'], close=df['Close'],
            name="Price"
        )])

        if show_st:
            fig.add_trace(go.Scatter(x=df.index, y=df['ST_Upper'], name="Upper Band", line=dict(color='red', width=1)))
            fig.add_trace(go.Scatter(x=df.index, y=df['ST_Lower'], name="Lower Band", line=dict(color='green', width=1)))

        fig.update_layout(
            template='plotly_dark',
            xaxis_rangeslider_visible=False,
            height=500,
            paper_bgcolor='#131722',
            plot_bgcolor='#131722',
            margin=dict(l=10, r=10, t=10, b=10)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # ലൈവ് പ്രൈസ് കാണിക്കാൻ (43632.jpg പ്രൈസ് സെക്ഷൻ പോലെ)
        curr_price = df['Close'].iloc[-1]
        st.metric(label=f"{selected_name} Live", value=f"₹ {curr_price:,.2f}")

except Exception as e:
    st.error("Market close ആണ് അല്ലെങ്കിൽ ഡാറ്റ കിട്ടുന്നില്ല. പിന്നീട് ശ്രമിക്കൂ.")
