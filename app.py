import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 1. ലുക്ക് ശരിയാക്കാൻ (Dark Mode)
st.set_page_config(page_title="FTB PRO TERMINAL", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #131722; color: white; }
    header { visibility: hidden; }
    .stMetric { background-color: #1e222d; padding: 10px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
st.sidebar.title("🚀 FTB PRO")
assets = {
    "NIFTY 50": "^NSEI",
    "BANK NIFTY": "^NSEBANK",
    "CRUDE OIL": "CL=F",
    "RELIANCE": "RELIANCE.NS"
}
selected = st.sidebar.selectbox("Select Asset", list(assets.keys()))
# 43641.jpg പോലെ ടൈംഫ്രെയിം മാറ്റാൻ
timeframe = st.sidebar.selectbox("Timeframe", ["1m", "5m", "15m", "1h", "1d"], index=1)

# --- DATA FETCHING ---
try:
    # കൃത്യമായ ചാർട്ട് കിട്ടാൻ ഡാറ്റാ ലിമിറ്റ് സെറ്റ് ചെയ്യുന്നു
    df = yf.download(assets[selected], period="5d", interval=timeframe, multi_level_index=False)
    
    if not df.empty:
        # പ്രൊഫഷണൽ കാൻഡിൽസ്റ്റിക് ഡിസൈൻ (43633.jpg ലുക്ക്)
        fig = go.Figure(data=[go.Candlestick(
            x=df.index,
            open=df['Open'], high=df['High'],
            low=df['Low'], close=df['Close'],
            increasing_line_color='#089981', decreasing_line_color='#f23645'
        )])

        # സൂപ്പർട്രെൻഡ് (ലളിതമായ രീതിയിൽ)
        df['SMA'] = df['Close'].rolling(window=20).mean()
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA'], line=dict(color='#2962ff', width=1.5), name="Trend Line"))

        fig.update_layout(
            template='plotly_dark',
            xaxis_rangeslider_visible=False,
            height=550,
            margin=dict(l=5, r=5, t=5, b=5),
            plot_bgcolor='#131722',
            paper_bgcolor='#131722'
        )
        
        # ചാർട്ട് പ്രദർശിപ്പിക്കുന്നു
        st.plotly_chart(fig, use_container_width=True)
        
        # നിലവിലെ വില വലിയ അക്ഷരത്തിൽ
        curr_p = df['Close'].iloc[-1]
        st.metric(label=f"LIVE {selected}", value=f"₹ {curr_p:,.2f}")

except Exception as e:
    st.error("Market close ആണ് അല്ലെങ്കിൽ ഡാറ്റ ലോഡ് ആവുന്നില്ല.")
