import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd

# 1. ലുക്ക് ശരിയാക്കാൻ (Dark Mode)
st.set_page_config(page_title="FTB PRO", layout="wide")
st.markdown("<style>.main {background-color: #131722;} header {visibility: hidden;}</style>", unsafe_allow_html=True)

# --- SIDEBAR ---
st.sidebar.title("📑 Watchlist")
assets = {"NIFTY 50": "^NSEI", "BANK NIFTY": "^NSEBANK", "CRUDE OIL": "CL=F", "RELIANCE": "RELIANCE.NS"}
selected = st.sidebar.selectbox("Select Asset", list(assets.keys()))
interval = st.sidebar.select_slider("Timeframe", options=["1m", "5m", "15m", "1h", "1d"], value="5m")

# --- DATA & CHART ---
try:
    # 2 ദിവസത്തെ ഡാറ്റ എടുക്കുന്നു (ചാർട്ട് വലുതായി കാണാൻ)
    df = yf.download(assets[selected], period="2d", interval=interval, multi_level_index=False)
    
    if not df.empty:
        # സൂപ്പർട്രെൻഡ് കാൽക്കുലേഷൻ
        atr = (df['High'] - df['Low']).rolling(10).mean()
        df['Upper'] = ((df['High'] + df['Low']) / 2) + (2 * atr)
        df['Lower'] = ((df['High'] + df['Low']) / 2) - (2 * atr)

        # പ്രൊഫഷണൽ കാൻഡിൽസ്റ്റിക് ചാർട്ട്
        fig = go.Figure(data=[go.Candlestick(
            x=df.index, open=df['Open'], high=df['High'],
            low=df['Low'], close=df['Close'], name="Price"
        )])

        # സൂപ്പർട്രെൻഡ് ലൈനുകൾ ചേർക്കുന്നു
        fig.add_trace(go.Scatter(x=df.index, y=df['Upper'], line=dict(color='red', width=1), name="Sell Line"))
        fig.add_trace(go.Scatter(x=df.index, y=df['Lower'], line=dict(color='green', width=1), name="Buy Line"))

        # ചാർട്ട് ലുക്ക് സെറ്റിംഗ്സ്
        fig.update_layout(
            template='plotly_dark',
            xaxis_rangeslider_visible=False,
            height=600, # ചാർട്ടിന്റെ ഉയരം കൂട്ടി
            margin=dict(l=10, r=10, t=10, b=10),
            plot_bgcolor='#131722',
            paper_bgcolor='#131722'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # ലൈവ് പ്രൈസ് വലിയ അക്ഷരത്തിൽ
        st.markdown(f"<h1 style='color: white; text-align: center;'>₹ {df['Close'].iloc[-1]:,.2f}</h1>", unsafe_allow_html=True)

except Exception as e:
    st.error("Market Data കിട്ടുന്നില്ല, പിന്നീട് ശ്രമിക്കൂ.")
