import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import os

st.set_page_config(page_title="Upstox AI Terminal", layout="wide")

# --- 1. ഡാറ്റ സേവിംഗ് ലോജിക് (Auto-Save) ---
DATA_FILE = 'trade_history_faisal.csv'

def save_data(balance, trades, watchlist):
    # ബാലൻസ്, ട്രേഡുകൾ, വാച്ച്‌ലിസ്റ്റ് എന്നിവ സേവ് ചെയ്യുന്നു
    data = {
        'balance': [balance],
        'trades': [trades],
        'watchlist': [watchlist]
    }
    pd.DataFrame([data]).to_json('user_data.json')

def load_data():
    if os.path.exists('user_data.json'):
        try:
            data = pd.read_json('user_data.json')
            return data['balance'][0], data['trades'][0], data['watchlist'][0]
        except: pass
    return 100000.0, [], ["RELIANCE.NS", "SBIN.NS", "INFY.NS"]

# സെഷൻ സ്റ്റേറ്റ് ലോഡിംഗ്
if 'balance' not in st.session_state:
    b, t, w = load_data()
    st.session_state.balance = b
    st.session_state.trades = t
    st.session_state.watchlist = w

# --- 2. സ്ട്രാറ്റജി (Supertrend & RSI) ---
def compute_strategy(df):
    df = df.copy()
    close = df['Close'].values.flatten()
    high = df['High'].values.flatten()
    low = df['Low'].values.flatten()
    
    # Simple ATR logic for Supertrend
    hl = high - low
    atr = pd.Series(hl).rolling(7).mean().values
    hl2 = (high + low) / 2
    upper = hl2 + (3 * atr)
    lower = hl2 - (3 * atr)
    
    st_line = np.zeros(len(df))
    trend = np.ones(len(df)) 
    for i in range(1, len(df)):
        if close[i] > upper[i-1]: trend[i] = 1
        elif close[i] < lower[i-1]: trend[i] = -1
        else: trend[i] = trend[i-1]
        st_line[i] = lower[i] if trend[i] == 1 else upper[i]
    
    df['st_line'] = st_line
    df['trend'] = trend
    return df

# --- 3. UI SIDEBAR (വാച്ച്‌ലിസ്റ്റ് മാനേജ്‌മെന്റ്) ---
with st.sidebar:
    st.title("🗂 Watchlist")
    new_sym = st.text_input("Add Symbol (eg: TATAMOTORS.NS)")
    if st.button("➕ Add to List"):
        if new_sym and new_sym not in st.session_state.watchlist:
            st.session_state.watchlist.append(new_sym.upper())
            save_data(st.session_state.balance, st.session_state.trades, st.session_state.watchlist)
            st.rerun()
    
    st.divider()
    # വാച്ച്‌ലിസ്റ്റിലുള്ള സ്റ്റോക്കുകൾ തിരഞ്ഞെടുക്കാൻ
    selected_stock = st.radio("Select Stock", st.session_state.watchlist)

# --- 4. MAIN DASHBOARD ---
st.title(f"📊 {selected_stock}")

try:
    data = yf.download(selected_stock, period="2d", interval="5m", progress=False)
    if not data.empty:
        df = compute_strategy(data)
        last_price = float(df['Close'].iloc[-1])
        
        # AI Advice Box
        advice = "🚀 BUY" if df['trend'].iloc[-1] == 1 else "🔴 SELL"
        st.info(f"**AI Strategy Suggestion:** {advice} at ₹{last_price:,.2f}")

        # ചാർട്ട്
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price")])
        fig.add_trace(go.Scatter(x=df.index, y=df['st_line'], line=dict(color='orange', width=1.5), name="Supertrend"))
        fig.update_layout(height=400, template="plotly_white", xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

        # പേപ്പർ ട്രേഡിംഗ്
        st.subheader(f"Account Balance: ₹{st.session_state.balance:,.2f}")
        qty = st.number_input("Quantity", min_value=1, value=1)
        c1, c2 = st.columns(2)
        
        if c1.button("🟢 BUY", use_container_width=True):
            st.session_state.balance -= (last_price * qty)
            st.session_state.trades.append({'Sym': selected_stock, 'Qty': qty, 'Price': last_price, 'Type': 'BUY'})
            save_data(st.session_state.balance, st.session_state.trades, st.session_state.watchlist)
            st.success("Buy Order Placed!")

        if c2.button("🔴 SELL", use_container_width=True):
            st.session_state.balance += (last_price * qty)
            st.session_state.trades.append({'Sym': selected_stock, 'Qty': qty, 'Price': last_price, 'Type': 'SELL'})
            save_data(st.session_state.balance, st.session_state.trades, st.session_state.watchlist)
            st.warning("Sell Order Placed!")

except Exception as e:
    st.error(f"Stock not found or Data error: {e}")

# ട്രേഡ് ഹിസ്റ്ററി
if st.session_state.trades:
    st.divider()
    st.write("### 📜 Recent Order Book")
    st.table(pd.DataFrame(st.session_state.trades).tail(5))
