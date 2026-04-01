import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import os

st.set_page_config(page_title="AI Trading Advisor", layout="wide")

# --- 1. ഡാറ്റ സേവിംഗ് ലോജിക് (Auto-Save) ---
DATA_FILE = 'trade_data.csv'

def save_account_info(balance, trades):
    df = pd.DataFrame(trades)
    df['current_balance'] = balance
    df.to_csv(DATA_FILE, index=False)

def load_account_info():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        balance = df['current_balance'].iloc[-1]
        trades = df.drop(columns=['current_balance']).to_dict('records')
        return float(balance), trades
    return 100000.0, []

# സെഷൻ സ്റ്റേറ്റ് ലോഡിംഗ്
if 'balance' not in st.session_state or 'trades' not in st.session_state:
    b, t = load_account_info()
    st.session_state.balance = b
    st.session_state.trades = t

# --- 2. സൂപ്പർട്രെൻഡ് കാൽക്കുലേഷൻ (No Library) ---
def get_indicators(df, period=7, multiplier=3):
    df = df.copy().reset_index()
    # ATR & Supertrend
    hl = df['High'] - df['Low']
    hc = np.abs(df['High'] - df['Close'].shift())
    lc = np.abs(df['Low'] - df['Close'].shift())
    tr = pd.concat([hl, hc, lc], axis=1).max(axis=1)
    atr = tr.rolling(period).mean()
    hl2 = (df['High'] + df['Low']) / 2
    upper = hl2 + (multiplier * atr)
    lower = hl2 - (multiplier * atr)
    
    st_line = np.zeros(len(df))
    trend = np.ones(len(df))
    for i in range(1, len(df)):
        if df['Close'].iloc[i] > upper.iloc[i-1]: trend[i] = 1
        elif df['Close'].iloc[i] < lower.iloc[i-1]: trend[i] = 0
        else: trend[i] = trend[i-1]
        st_line[i] = lower.iloc[i] if trend[i] == 1 else upper.iloc[i]
    
    df['st_line'] = st_line
    df['trend'] = trend # 1 = Green, 0 = Red
    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    df['RSI'] = 100 - (100 / (1 + (gain / loss)))
    return df.set_index('Date')

# --- 3. AI ADVISOR LOGIC ---
def ai_advisor(df):
    curr = df.iloc[-1]
    # സൂപ്പർട്രെൻഡും RSI-യും ഒരേപോലെ വന്നാൽ കൺഫർമേഷൻ നൽകുന്നു
    if curr['trend'] == 1 and curr['RSI'] < 40:
        return "🚀 STRONG BUY: Supertrend is Green & RSI is low!", "green"
    elif curr['trend'] == 0 and curr['RSI'] > 60:
        return "⚠️ SELL: Supertrend is Red & RSI is high!", "red"
    elif curr['trend'] == 1:
        return "📈 HOLD BUY: Supertrend says Up, but wait for RSI dip.", "blue"
    else:
        return "📉 WAIT: No clear signal at the moment.", "grey"

# --- 4. MAIN UI ---
st.title("🤖 AI Trading Terminal")
symbol = st.text_input("Enter Symbol", "RELIANCE.NS")

try:
    df = yf.download(symbol, period="2d", interval="5m")
    if not df.empty:
        df = get_indicators(df)
        advice, color = ai_advisor(df)
        last_p = df['Close'].iloc[-1]

        # AI കൺഫർമേഷൻ ബോക്സ്
        st.markdown(f"<div style='padding:20px; border-radius:10px; border-left:8px solid {color}; background:#f9f9f9;'><h4>AI Advice: {advice}</h4></div>", unsafe_allow_html=True)
        
        # ചാർട്ട്
        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"))
        fig.add_trace(go.Scatter(x=df.index, y=df['st_line'], line=dict(color='orange', width=2), name="Supertrend"))
        fig.update_layout(height=400, template="plotly_white", xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

        # പേപ്പർ ട്രേഡിംഗ് പാനൽ
        col1, col2, col3 = st.columns([1,1,1])
        q = col1.number_input("Qty", min_value=1, value=1)
        
        if col2.button("🟢 Confirm BUY"):
            st.session_state.balance -= (last_p * q)
            st.session_state.trades.append({'Sym': symbol, 'Qty': q, 'Price': last_p, 'Type': 'BUY'})
            save_account_info(st.session_state.balance, st.session_state.trades)
            st.success("Trade Saved!")
            
        if col3.button("🔴 Confirm SELL"):
            st.session_state.balance += (last_p * q)
            st.session_state.trades.append({'Sym': symbol, 'Qty': q, 'Price': last_p, 'Type': 'SELL'})
            save_account_info(st.session_state.balance, st.session_state.trades)
            st.warning("Trade Saved!")

except Exception as e:
    st.error(f"Error: {e}")

# പോർട്ട്‌ഫോളിയോ താഴെ കാണിക്കുന്നു
st.divider()
st.subheader(f"Current Balance: ₹{st.session_state.balance:,.2f}")
if st.session_state.trades: st.table(pd.DataFrame(st.session_state.trades).tail(5))
