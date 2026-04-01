import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import os

st.set_page_config(page_title="AI Trade Advisor", layout="wide")

# --- 1. ഡാറ്റ സേവിംഗ് ലോജിക് ---
DATA_FILE = 'trade_history_faisal.csv'

def save_data(balance, trades):
    df = pd.DataFrame(trades)
    df['saved_balance'] = balance
    df.to_csv(DATA_FILE, index=False)

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_csv(DATA_FILE)
            balance = df['saved_balance'].iloc[-1]
            trades = df.drop(columns=['saved_balance']).to_dict('records')
            return float(balance), trades
        except: return 100000.0, []
    return 100000.0, []

if 'balance' not in st.session_state:
    b, t = load_data()
    st.session_state.balance = b
    st.session_state.trades = t

# --- 2. സ്ട്രാറ്റജി കാൽക്കുലേഷൻ (Error Fix for 2D Arrays) ---
def compute_strategy(df, period=7, multiplier=3):
    df = df.copy()
    # 2D Array എറർ ഒഴിവാക്കാൻ ഡാറ്റ ഫ്ലാറ്റൻ ചെയ്യുന്നു
    close = df['Close'].values.flatten()
    high = df['High'].values.flatten()
    low = df['Low'].values.flatten()
    
    # ATR കണക്കാക്കുന്നു
    hl = high - low
    hc = np.abs(high - pd.Series(close).shift(1).values)
    lc = np.abs(low - pd.Series(close).shift(1).values)
    tr = np.nan_to_num(np.max([hl, hc, lc], axis=0))
    atr = pd.Series(tr).rolling(period).mean().values
    
    hl2 = (high + low) / 2
    upper = hl2 + (multiplier * atr)
    lower = hl2 - (multiplier * atr)
    
    st_line = np.zeros(len(df))
    trend = np.ones(len(df)) 
    
    for i in range(1, len(df)):
        if close[i] > upper[i-1]: trend[i] = 1
        elif close[i] < lower[i-1]: trend[i] = -1
        else: trend[i] = trend[i-1]
        st_line[i] = lower[i] if trend[i] == 1 else upper[i]
    
    df['st_line'] = st_line
    df['trend'] = trend
    
    # RSI
    delta = pd.Series(close).diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    df['RSI'] = 100 - (100 / (1 + (gain / loss).fillna(0)))
    return df

# --- 3. MAIN APP ---
st.title("🤖 AI Trading Terminal")
symbol = st.text_input("Enter Symbol", "RELIANCE.NS")

try:
    # ഡാറ്റ ഡൗൺലോഡ് (Error Handling Added)
    data = yf.download(symbol, period="2d", interval="5m", progress=False)
    
    if not data.empty:
        df = compute_strategy(data)
        last_price = float(df['Close'].iloc[-1])
        curr_trend = df['trend'].iloc[-1]
        curr_rsi = df['RSI'].iloc[-1]

        # AI Advice Box
        if curr_trend == 1 and curr_rsi < 50:
            st.success(f"**AI Advice:** STRONG BUY (Trend is UP, RSI is {curr_rsi:.1f})")
        elif curr_trend == -1 and curr_rsi > 50:
            st.error(f"**AI Advice:** SELL (Trend is DOWN, RSI is {curr_rsi:.1f})")
        else:
            st.warning(f"**AI Advice:** HOLD (Wait for better entry)")

        # ചാർട്ട്
        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"))
        fig.add_trace(go.Scatter(x=df.index, y=df['st_line'], line=dict(color='orange', width=2), name="Supertrend"))
        fig.update_layout(height=450, template="plotly_white", xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

        # പേപ്പർ ട്രേഡിംഗ്
        st.subheader(f"Current Balance: ₹{st.session_state.balance:,.2f}")
        qty = st.number_input("Quantity", min_value=1, value=1)
        b1, b2 = st.columns(2)
        
        if b1.button("🟢 BUY", use_container_width=True):
            st.session_state.balance -= (last_price * qty)
            st.session_state.trades.append({'Sym': symbol, 'Qty': qty, 'Price': last_price, 'Type': 'BUY'})
            save_data(st.session_state.balance, st.session_state.trades)
            st.rerun()

        if b2.button("🔴 SELL", use_container_width=True):
            st.session_state.balance += (last_price * qty)
            st.session_state.trades.append({'Sym': symbol, 'Qty': qty, 'Price': last_price, 'Type': 'SELL'})
            save_data(st.session_state.balance, st.session_state.trades)
            st.rerun()

except Exception as e:
    st.error(f"Something went wrong: {e}")

# ഹിസ്റ്ററി കാണിക്കുന്നു
if st.session_state.trades:
    st.write("### Recent Trades (Saved)")
    st.table(pd.DataFrame(st.session_state.trades).tail(5))
