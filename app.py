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
install_if_missing('pandas_ta') # സൂപ്പർ ട്രെൻഡ് കണക്കാക്കാൻ ഇത് സഹായിക്കും

# 2. ലൈബ്രറികൾ ഇമ്പോർട്ട് ചെയ്യുന്നു
import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import pandas_ta as ta
from datetime import datetime

# 3. ആപ്പ് ഡിസൈൻ
st.set_page_config(page_title="Faisal Pro Smart Bot", layout="wide")

st.markdown("<h1 style='text-align: center; color: #1E88E5;'>📊 ഫൈസൽ പ്രോ സൂപ്പർ ട്രെൻഡ് ചാർട്ട്</h1>", unsafe_allow_html=True)

# സൈഡ് ബാർ - കറൻസി കൺവെർട്ടർ
st.sidebar.header("💰 AED to INR")
try:
    live_rate_data = yf.Ticker("AEDINR=X").history(period="1d")
    if not live_rate_data.empty:
        live_rate = live_rate_data['Close'].iloc[-1]
        aed = st.sidebar.number_input("ദിർഹം (AED)", min_value=0.0, value=1000.0)
        st.sidebar.success(f"ഇന്നത്തെ തുക: ₹{(aed * live_rate):.2f}")
except:
    st.sidebar.warning("Currency rate fetch error")

# 4. സൂപ്പർ ട്രെൻഡ് ചാർട്ട് ഫങ്ക്ഷൻ
def draw_supertrend_chart(name, symbol):
    try:
        # ഡാറ്റ എടുക്കുന്നു (കുറഞ്ഞത് 100 കാൻഡിലുകൾ വേണം സൂപ്പർ ട്രെൻഡ് കൃത്യമാകാൻ)
        df = yf.Ticker(symbol).history(period="5d", interval="5m")
        
        if not df.empty:
            # സൂപ്പർ ട്രെൻഡ് കണക്കാക്കുന്നു (Period: 7, Multiplier: 3)
            sti = ta.supertrend(df['High'], df['Low'], df['Close'], length=7, multiplier=3)
            
            # സൂപ്പർ ട്രെൻഡ് ഡാറ്റ മെയിൻ ഡാറ്റാഫ്രെയിമിലേക്ക് ചേർക്കുന്നു
            df['ST'] = sti['SUPERT_7_3.0']
            df['ST_Dir'] = sti['SUPERTd_7_3.0'] # 1 (Buy), -1 (Sell)

            fig = go.Figure()

            # കാൻഡിൽസ്റ്റിക് ചാർട്ട്
            fig.add_trace(go.Candlestick(
                x=df.index, open=df['Open'], high=df['High'],
                low=df['Low'], close=df['Close'], name='വില'
            ))

            # സൂപ്പർ ട്രെൻഡ് ലൈൻ (പച്ച/ചുവപ്പ്)
            # ഡയറക്ഷൻ 1 ആണെങ്കിൽ പച്ച (Buy), -1 ആണെങ്കിൽ ചുവപ്പ് (Sell)
            colors = ['green' if d == 1 else 'red' for d in df['ST_Dir']]
            
            fig.add_trace(go.Scatter(
                x=df.index, y=df['ST'], 
                line=dict(width=2, color='yellow'), # ട്രെൻഡ് ലൈൻ മഞ്ഞയിൽ
                name='Supertrend'
            ))

            fig.update_layout(
                title=f"{name} ലൈവ് ചാർട്ട് (Supertrend 7,3)",
                xaxis_rangeslider_visible=False,
                template='plotly_dark',
                height=600
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning(f"{name} ഡാറ്റ ഇപ്പോൾ ലഭ്യമല്ല.")
            
    except Exception as e:
        st.error(f"Error loading {name}: {e}")

# 5. ചാർട്ടുകൾ ഡിസ്പ്ലേ ചെയ്യുന്നു
draw_supertrend_chart("Nifty 50", "^NSEI")
draw_supertrend_chart("Crude Oil (CL=F)", "CL=F")

st.info("💡 മഞ്ഞ ലൈനിന് മുകളിൽ കാൻഡിൽ വന്നാൽ 'Buy' എന്നും താഴെ വന്നാൽ 'Sell' എന്നും മനസ്സിലാക്കാം.")
