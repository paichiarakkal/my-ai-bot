import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import time

# --- Page Config ---
st.set_page_config(page_title="Faisal's MCX Terminal", layout="wide")

# --- 1. വാലറ്റ് ബാലൻസ് ---
if 'balance' not in st.session_state:
    st.session_state.balance = 471435.50 #

# --- 2. ലൈവ് ഡാറ്റാ ഫംഗ്‌ഷൻ ---
def get_market_data(ticker):
    try:
        data = yf.download(ticker, period="1d", interval="1m", progress=False)
        if not data.empty:
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)
            return data
    except: return pd.DataFrame()
    return pd.DataFrame()

# --- 3. AI അസിസ്റ്റന്റ് ലോജിക് ---
def get_ai_advice(rsi_val, price, ema_val):
    try:
        rsi = float(rsi_val)
        if rsi < 35: return "🔥 AI BUY: മാർക്കറ്റ് താഴെയാണ്, വാങ്ങാൻ നല്ല സമയം!", "#00FFA3", "#003322"
        elif rsi > 65: return "⚡ AI SELL: വില ഉയർന്നിട്ടുണ്ട്, ഇപ്പോൾ വിൽക്കാം!", "#FF3131", "#330000"
        return "📈 TREND: മാർക്കറ്റ് അനുകൂലമാണ്. ശ്രദ്ധയോടെ ട്രേഡ് ചെയ്യുക.", "#00D1FF", "#002B36"
    except: return "⚖️ SYNCING...", "#FFD700", "#332B00"

# --- 4. സൈഡ്‌ബാർ (Exchange Calculator) ---
st.sidebar.title("🤖 Faisal AI Control")

# എക്സ്ചേഞ്ച് റേറ്റ് കാൽക്കുലേറ്റർ
st.sidebar.header("💱 Exchange Calculator")
calc_pair = st.sidebar.selectbox("Select Pair", ["AED to INR", "INR to AED", "USD to INR"])
calc_amt = st.sidebar.number_input("Enter Amount", value=1.0)

try:
    pair_map = {"AED to INR": "AEDINR=X", "INR to AED": "INRAED=X", "USD to INR": "INR=X"}
    rate_df = yf.download(pair_map[calc_pair], period="1d", progress=False)
    if not rate_df.empty:
        if isinstance(rate_df.columns, pd.MultiIndex): rate_df.columns = rate_df.columns.get_level_values(0)
        current_rate = float(rate_df['Close'].iloc[-1])
        st.sidebar.success(f"1 Unit = {current_rate:.2f}")
        st.sidebar.write(f"Total: **{calc_amt * current_rate:,.2f}**")
except: st.sidebar.error("Rate Fetch Error")

st.sidebar.divider()
asset_choice = st.sidebar.selectbox("Select Asset", ["Crude Oil (MCX)", "Gold (Live)", "Nifty 50"])

# --- 5. മെയിൻ ഡിസ്‌പ്ലേ ---
placeholder = st.empty()

while True:
    with placeholder.container():
        # MCX ക്രൂഡ് ഓയിലിനായി 'MCX' ടിക്കർ ഉപയോഗിക്കുന്നു
        ticker_map = {"Crude Oil (MCX)": "CL=F", "Gold (Live)": "GC=F", "Nifty 50": "^NSEI"}
        df = get_market_data(ticker_map[asset_choice])
        
        if not df.empty:
            last_p = float(df['Close'].iloc[-1])
            
            # Indicators
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rsi = (100 - (100 / (1 + (gain / loss)))).iloc[-1]
            ema = df['Close'].ewm(span=20).mean().iloc[-1]

            advice, text_col, bg_col = get_ai_advice(rsi, last_p, ema)

            st.metric("Live Wallet Balance", f"₹{st.session_state.balance:,.2f}") #

            # AI Advisor
            st.markdown(f'<div style="background:{bg_col};padding:20px;border-radius:15px;border:2px solid {text_col};">'
                        f'<h3 style="color:{text_col};margin:0;">🚀 Faisal AI Advisor</h3>'
                        f'<p style="color:white;margin-top:10px;">{advice}</p></div>', unsafe_allow_html=True)

            # Chart
            st.write(f"### {asset_choice} Live Tracker")
            fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
            fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,t=0,b=0))
            st.plotly_chart(fig, use_container_width=True)

    time.sleep(30)
    st.rerun()
