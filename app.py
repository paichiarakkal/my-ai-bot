import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime
import pytz

# 1. പേജ് സെറ്റിംഗ്സ്
st.set_page_config(page_title="FTB AI Terminal", layout="wide")

# --- സൈഡ്‌ബാറിലെ വിവരങ്ങൾ ---
st.sidebar.markdown("## 📊 FTB SETTINGS")
uae_tz = pytz.timezone('Asia/Dubai')
st.sidebar.markdown(f"🕒 **UAE Time:** {datetime.now(uae_tz).strftime('%H:%M:%S')}")

show_st = st.sidebar.checkbox("Show SuperTrend", value=True)

# --- സമയം മാറ്റാനുള്ള ഓപ്ഷൻ (ഇവിടെയാണ് നീ നോക്കേണ്ടത്) ---
chart_int = st.sidebar.selectbox("Select Time Frame", ["1m", "5m", "15m", "1h"], index=0)

# --- SuperTrend Function ---
def get_st(df, period=10, mult=3):
    hl2 = (df['High'] + df['Low']) / 2
    tr = pd.concat([df['High'] - df['Low'], abs(df['High'] - df['Close'].shift(1)), abs(df['Low'] - df['Close'].shift(1))], axis=1).max(axis=1)
    atr = tr.rolling(period).mean()
    up, lo = hl2 + (mult * atr), hl2 - (mult * atr)
    st_line = [lo[i] if df['Close'][i] > up[i-1] else up[i] for i in range(len(df))]
    return st_line

# --- മെയിൻ ഡാഷ്‌ബോർഡ് ---
st.markdown("<h1 style='text-align: center; color: #00E676;'>📊 FTB SMART AI TERMINAL</h1>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📈 Trading Dashboard", "💬 FTB AI Chat"])

with tab1:
    try:
        # USDINR നിരക്ക്
        usdinr = yf.Ticker("USDINR=X").history(period="1d")['Close'].iloc[-1]
        
        # ക്രൂഡ് ഓയിൽ ലൈവ് ഡാറ്റ
        # 1m ആണെങ്കിൽ period="1d" മതിയാകും
        df = yf.Ticker("CL=F").history(period="1d", interval=chart_int)
        
        if not df.empty:
            # MCX വിലയിലേക്ക് മാറ്റുന്നു (₹9,850 റേഞ്ച് വരാൻ)
            mcx_val = df['Close'].iloc[-1] * usdinr * 1.135 / 10
            
            st.metric(f"CRUDEOIL MCX ({chart_int})", f"₹ {mcx_val:,.2f}")
            
            # ചാർട്ടിലെ ഡാറ്റ രൂപയിലേക്ക് മാറ്റുന്നു
            df = df * (usdinr * 1.135 / 10)

            fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
            
            if show_st:
                fig.add_trace(go.Scatter(x=df.index, y=get_st(df), line=dict(color='#FFEB3B', width=2), name='SuperTrend'))
            
            fig.update_layout(height=600, template='plotly_dark', xaxis_rangeslider_visible=False, yaxis=dict(side='right'))
            st.plotly_chart(fig, use_container_width=True)
            
            # Buy/Sell ബട്ടണുകൾ
            c1, c2 = st.columns(2)
            if c1.button("🟢 BUY", use_container_width=True): st.success(f"Buy at {mcx_val:.2f}")
            if c2.button("🔴 SELL", use_container_width=True): st.error(f"Sell at {mcx_val:.2f}")
                
    except: st.error("Data error")

with tab2:
    st.subheader("🤖 FTB AI Assistant")
    # (Chat code remains the same...)
