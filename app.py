import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import os

st.set_page_config(page_title="AI Trade Advisor", layout="wide")

# --- 1. ഡാറ്റ സേവിംഗ് (Refresh ആയാലും പോകാതിരിക്കാൻ) ---
DATA_FILE = 'trade_history_faisal.csv'

def save_data(balance, trades):
    # ബാലൻസും ട്രേഡുകളും ഒരു ഫയലിലേക്ക് സേവ് ചെയ്യുന്നു
    df = pd.DataFrame(trades)
    df['saved_balance'] = balance
    df.to_csv(DATA_FILE, index=False)

def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        balance = df['saved_balance'].iloc[-1]
        trades = df.drop(columns=['saved_balance']).to_dict('records')
        return float(balance), trades
    return 100000.0, []

if 'balance' not in st.session_state:
    b, t = load_data()
    st.session_state.balance = b
    st.session_state.trades = t

# --- 2. സൂപ്പർട്രെൻഡ് & RSI (Error Free Version) ---
def compute_strategy(df, period=7, multiplier=3):
    df = df.copy()
    # ഇൻഡക്സ് പ്രശ്നം ഒഴിവാക്കാൻ ലളിതമായ ലൂപ്പ് ഉപയോഗിക്കുന്നു
    high = df['High'].values
    low = df['Low'].values
    close = df['Close'].values
    
    # ATR കണക്കാക്കുന്നു
    hl = high - low
    hc = np.abs(high - pd.Series(close).shift(1).values)
    lc = np.abs(low - pd.Series(close).shift(1).values)
    tr = np.max([hl, hc, lc], axis=0)
    atr = pd.Series(tr).rolling(period).mean().values
    
    hl2 = (high + low) / 2
    upperband = hl2 + (multiplier * atr)
    lowerband = hl2 - (multiplier * atr)
    
    st_line = np.zeros(len(df))
    direction = np.ones(len(df)) # 1 for Up, -1 for Down
    
    for i in range(1, len(df)):
        if close[i] > upperband[i-1]:
            direction[i] = 1
        elif close[i] < lowerband[i-1]:
            direction[i] = -1
        else:
            direction[i] = direction[i-1]
            
        st_line[i] = lowerband[i] if direction[i] == 1 else upperband[i]
    
    df['st_line'] = st_line
    df['trend'] = direction
    
    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    df['RSI'] = 100 - (100 / (1 + (gain / loss)))
    return df

# --- 3. AI ADVISOR ---
def get_ai_advice(df):
    curr = df.iloc[-1]
    if curr['trend'] == 1 and curr['RSI'] < 45:
        return "✅ STRONG BUY: Trend is UP and RSI is healthy.", "green"
    elif curr['trend'] == -1 and curr['RSI'] > 55:
        return "❌ SELL: Trend is DOWN and RSI is high.", "red"
    else:
        return "⚖️ HOLD: Wait for clear confirmation.", "orange"

# --- 4. MAIN UI ---
st.title("🤖 AI Trading Terminal")
symbol = st.text_input("Enter Symbol", "RELIANCE.NS")

try:
    data = yf.download(symbol, period="2d", interval="5m")
    if not data.empty:
        df = compute_strategy(data)
        advice, color = get_ai_advice(df)
        last_price = df['Close'].iloc[-1]

        # AI ഉപദേശം കാണിക്കുന്നു
        st.info(f"**AI Recommendation:** {advice}")
        
        # ചാർട്ട്
        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"))
        fig.add_trace(go.Scatter(x=df.index, y=df['st_line'], line=dict(color='orange', width=2), name="Supertrend"))
        fig.update_layout(height=450, template="plotly_white", xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

        # പേപ്പർ ട്രേഡിംഗ് പാനൽ
        st.subheader(f"Balance: ₹{st.session_state.balance:,.2f}")
        q = st.number_input("Quantity", min_value=1, value=1)
        c1, c2 = st.columns(2)
        
        if c1.button("🟢 BUY"):
            st.session_state.balance -= (last_price * q)
            st.session_state.trades.append({'Sym': symbol, 'Qty': q, 'Price': last_price, 'Type': 'BUY'})
            save_data(st.session_state.balance, st.session_state.trades)
            st.success("Trade Executed & Saved!")
            
        if c2.button("🔴 SELL"):
            st.session_state.balance += (last_price * q)
            st.session_state.trades.append({'Sym': symbol, 'Qty': q, 'Price': last_price, 'Type': 'SELL'})
            save_data(st.session_state.balance, st.session_state.trades)
            st.warning("Trade Executed & Saved!")

except Exception as e:
    st.error(f"Something went wrong: {e}")

# ട്രേഡ് ഹിസ്റ്ററി
if st.session_state.trades:
    st.divider()
    st.write("### Recent Trades")
    st.table(pd.DataFrame(st.session_state.trades).tail(5))
