import subprocess
import sys
import os

# 1. ആവശ്യമായ ലൈബ്രറി (plotly) ഉണ്ടോ എന്ന് നോക്കുന്നു, ഇല്ലെങ്കിൽ ഇൻസ്റ്റാൾ ചെയ്യുന്നു
def install_if_missing(package):
    try:
        __import__(package)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install_if_missing('plotly')

# 2. ബാക്കി ലൈബ്രറികൾ ഇമ്പോർട്ട് ചെയ്യുന്നു
import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime

# 3. ആപ്പ് ഡിസൈൻ (Faisal Pro Smart Bot)
st.set_page_config(page_title="Faisal Pro Smart Bot", layout="wide")

st.markdown("<h1 style='text-align: center; color: #1E88E5;'>📊 ഫൈസൽ പ്രോ ട്രേഡിംഗ് ചാർട്ടുകൾ</h1>", unsafe_allow_html=True)

# സൈഡ് ബാർ - കറൻസി കൺവെർട്ടർ
st.sidebar.header("💰 AED to INR")
try:
    live_rate_data = yf.Ticker("AEDINR=X").history(period="1d")
    if not live_rate_data.empty:
        live_rate = live_rate_data['Close'].iloc[-1]
        aed = st.sidebar.number_input("ദിർഹം (AED)", min_value=0.0, value=1000.0)
        st.sidebar.success(f"ഇന്നത്തെ തുക: ₹{(aed * live_rate):.2f}")
except:
    st.sidebar.error("Currency rate fetch error")

# ചാർട്ട് വരയ്ക്കാനുള്ള ഫങ്ക്ഷൻ
def draw_chart(name, symbol):
    try:
        df = yf.Ticker(symbol).history(period="1d", interval="5m")
        if not df.empty:
            fig = go.Figure(data=[go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close']
            )])
            fig.update_layout(title=f"{name} ലൈവ് ചാർട്ട് (5 min)", xaxis_rangeslider_visible=False, height=450)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error(f"{name} ഡാറ്റ ലഭ്യമല്ല.")
    except Exception as e:
        st.error(f"Error drawing chart: {e}")

# ചാർട്ടുകൾ ഡിസ്പ്ലേ ചെയ്യുന്നു
draw_chart("Nifty 50", "^NSEI")
draw_chart("Crude Oil (CL=F)", "CL=F")

st.info("💡 Upstox-ൽ കാണുന്നതുപോലെ ചാർട്ടിൽ തൊട്ടാൽ നിങ്ങൾക്ക് വില അറിയാൻ സാധിക്കും.")
