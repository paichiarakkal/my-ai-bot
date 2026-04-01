import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import os

# പേജ് സെറ്റിംഗ്സ്
st.set_page_config(page_title="Upstox AI Terminal", layout="wide", initial_sidebar_state="expanded")

# --- 1. ഡാറ്റാ ലോഡിംഗ് & സേവിംഗ് (Persistence) ---
DATA_FILE = 'faisal_trade_data.csv'

def load_user_data():
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_csv(DATA_FILE)
            balance = float(df['bal'].iloc[-1])
            trades = df.drop(columns=['bal']).to_dict('records')
            return balance, trades
        except: return 100000.0, []
    return 100000.0, []

if 'balance' not in st.session_state:
    b, t = load_user_data()
    st.session_state.balance = b
    st.session_state.trades = t

def save_current_trade(trade_row):
    trade_row['bal'] = st.session_state.balance
    df = pd.DataFrame([trade_row])
    if not os.path.exists(DATA_FILE):
        df.to_csv(DATA_FILE, index=False)
    else:
        df.to_csv(DATA_FILE, mode='a', header=False, index=False)

# --- 2. സൂപ്പർട്രെൻഡ് & AI സ്ട്രാറ്റജി ലോജിക് ---
def get_strategy_data(df):
    df = df.copy()
    close = df['Close'].values.flatten()
    high = df['High'].values.flatten()
    low = df['Low'].values.flatten()
    
    # Simple Supertrend Calculation
    atr = pd.Series(high - low).rolling(7).mean().values
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

# --- 3. UI ഡിസൈൻ & ഫീച്ചറുകൾ ---
st.sidebar.title("🏨 Market Terminal")
asset_choice = st.sidebar.selectbox("Market Asset", ["Nifty 50", "Crude Oil", "Gold", "Currency Calc"])

def render_terminal(ticker, name):
    try:
        # ഡാറ്റ എടുക്കുന്നു
        data = yf.download(ticker, period="2d", interval="5m", progress=False)
        if not data.empty:
            df = get_strategy_data(data)
            last_price = float(df['Close'].iloc[-1])
            curr_trend = df['trend'].iloc[-1]
            
            # --- AI ADVISOR BOX ---
            advice = "🚀 AI SIGNAL: BUY" if curr_trend == 1 else "🔴 AI SIGNAL: SELL"
            color = "#00FF00" if curr_trend == 1 else "#FF4B4B"
            
            st.markdown(f"""
                <div style="background-color:#1E1E1E; padding:20px; border-radius:15px; border-left: 10px solid {color}; margin-bottom:20px;">
                    <h2 style="color:{color}; margin:0;">{advice}</h2>
                    <p style="color:white; font-size:18px;">Target Asset: {name} | Price: <b>₹{last_price:,.2f}</b></p>
                </div>
            """, unsafe_allow_html=True)

            # ചാർട്ട്
            fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price")])
            fig.add_trace(go.Scatter(x=df.index, y=df['st_line'], line=dict(color='orange', width=1.5), name="Supertrend"))
            fig.update_layout(height=450, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
            st.plotly_chart(fig, use_container_width=True)

            # പേപ്പർ ട്രേഡിംഗ് പാനൽ
            st.markdown(f"### 💰 Wallet: **₹{st.session_state.balance:,.2f}**")
            col1, col2 = st.columns(2)
            qty = st.number_input("Enter Quantity", min_value=1, value=10, step=1, key=f"qty_{ticker}")
            
            if col1.button(f"🟢 BUY {name}", use_container_width=True):
                st.session_state.balance -= (last_price * qty)
                save_trade_entry = {'Sym': name, 'Qty': qty, 'Price': last_price, 'Type': 'BUY'}
                st.session_state.trades.append(save_trade_entry)
                save_current_trade(save_trade_entry)
                st.rerun()

            if col2.button(f"🔴 SELL {name}", use_container_width=True):
                st.session_state.balance += (last_price * qty)
                save_trade_entry = {'Sym': name, 'Qty': qty, 'Price': last_price, 'Type': 'SELL'}
                st.session_state.trades.append(save_trade_entry)
                save_current_trade(save_trade_entry)
                st.rerun()

    except Exception as e:
        st.error(f"Error Loading Data: {e}")

# --- 4. മെയിൻ ലോജിക് എക്സിക്യൂഷൻ ---
if asset_choice == "Nifty 50":
    render_terminal("^NSEI", "Nifty 50")
elif asset_choice == "Crude Oil":
    render_terminal("CL=F", "Crude Oil")
elif asset_choice == "Gold":
    render_terminal("GC=F", "Gold")
elif asset_choice == "Currency Calc":
    st.header("💱 Currency Calculator (USD/INR)")
    usd_val = st.number_input("Amount in USD ($)", value=1.0)
    rate = float(yf.download("INR=X", period="1d", progress=False)['Close'].iloc[-1])
    st.success(f"Equivalent Indian Rupees: ₹{usd_val * rate:,.2f}")

# --- 5. ഓർഡർ ബുക്ക് (History) ---
st.divider()
st.subheader("📜 Recent Order Book")
if st.session_state.trades:
    df_history = pd.DataFrame(st.session_state.trades).tail(10)
    st.table(df_history)
else:
    st.info("No trades executed yet. Start trading to see history!")
