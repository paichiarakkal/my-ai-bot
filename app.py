import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import os

st.set_page_config(page_title="Pro AI Terminal", layout="wide")

# --- 1. ഡാറ്റാ സേവിംഗ് (Persistence) ---
DATA_FILE = 'faisal_pro_trades.csv'
if 'balance' not in st.session_state:
    if os.path.exists(DATA_FILE):
        try:
            df_hist = pd.read_csv(DATA_FILE)
            st.session_state.balance = float(df_hist['bal'].iloc[-1])
        except: st.session_state.balance = 100000.0
    else: st.session_state.balance = 100000.0

def log_trade(sym, price, qty, t_type, sl, tg):
    bal = st.session_state.balance
    df = pd.DataFrame([{'Sym': sym, 'Price': price, 'Qty': qty, 'Type': t_type, 'SL': sl, 'TG': tg, 'bal': bal}])
    df.to_csv(DATA_FILE, mode='a', header=not os.path.exists(DATA_FILE), index=False)

# --- 2. പ്രൊഫഷണൽ ഇൻഡിക്കേറ്റർ ലോജിക് ---
def add_indicators(df):
    close = df['Close']
    # EMA (Trend line)
    df['EMA_20'] = close.ewm(span=20, adjust=False).mean()
    # RSI (Overbought/Oversold)
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    # Bollinger Bands (Volatility)
    df['MA20'] = close.rolling(window=20).mean()
    df['STD'] = close.rolling(window=20).std()
    df['Upper_Band'] = df['MA20'] + (df['STD'] * 2)
    df['Lower_Band'] = df['MA20'] - (df['STD'] * 2)
    return df

# --- 3. മെയിൻ ടെർമിനൽ ---
def render_pro_terminal(ticker, name):
    try:
        df = yf.download(ticker, period="1d", interval="1m", auto_adjust=True, progress=False)
        if not df.empty:
            df = add_indicators(df)
            last_p = float(df['Close'].iloc[-1])
            rsi_v = float(df['RSI'].iloc[-1])
            
            # AI Advisor Box
            advice = "🚀 STRONG BUY" if rsi_v < 35 else "🔴 STRONG SELL" if rsi_v > 65 else "⚖️ HOLD / WAIT"
            color = "#00ff00" if "BUY" in advice else "#ff4b4b" if "SELL" in advice else "#ffa500"
            
            st.markdown(f"""<div style="background:#1e1e1e; padding:20px; border-radius:15px; border:2px solid {color}; text-align:center;">
                <h2 style="color:{color};">{advice}</h2>
                <p style="color:white;">RSI: {rsi_v:.2f} | Price: ₹{last_p:,.2f}</p></div>""", unsafe_allow_html=True)

            # ചാർട്ട് വിത്ത് ഇൻഡിക്കേറ്റേഴ്സ്
            fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price")])
            fig.add_trace(go.Scatter(x=df.index, y=df['EMA_20'], line=dict(color='yellow', width=1), name="EMA 20"))
            fig.add_trace(go.Scatter(x=df.index, y=df['Upper_Band'], line=dict(color='gray', dash='dash'), name="Upper Band"))
            fig.add_trace(go.Scatter(x=df.index, y=df['Lower_Band'], line=dict(color='gray', dash='dash'), name="Lower Band"))
            fig.update_layout(height=450, template="plotly_dark", xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)

            # ട്രേഡിംഗ് കൺട്രോൾസ് (With SL & Target)
            st.subheader(f"💰 Wallet: ₹{st.session_state.balance:,.2f}")
            c1, c2, c3 = st.columns(3)
            qty = c1.number_input("Qty", min_value=1, value=10)
            sl_val = c2.number_input("Stop Loss Price", value=last_p * 0.98) # 2% താഴെ
            tg_val = c3.number_input("Target Price", value=last_p * 1.05)   # 5% ലാഭം
            
            btn1, btn2 = st.columns(2)
            if btn1.button("🟢 PRO BUY", use_container_width=True):
                st.session_state.balance -= (last_p * qty)
                log_trade(name, last_p, qty, "BUY", sl_val, tg_val); st.rerun()
            if btn2.button("🔴 PRO SELL", use_container_width=True):
                st.session_state.balance += (last_p * qty)
                log_trade(name, last_p, qty, "SELL", sl_val, tg_val); st.rerun()

    except Exception as e: st.error(f"Error: {e}")

# --- 4. മെനു ---
choice = st.sidebar.selectbox("Market Asset", ["Crude Oil", "Nifty 50", "Gold"])
if choice == "Crude Oil": render_pro_terminal("CL=F", "Crude Oil")
elif choice == "Nifty 50": render_pro_terminal("^NSEI", "Nifty 50")
elif choice == "Gold": render_pro_terminal("GC=F", "Gold")

# ഹിസ്റ്ററി വിത്ത് SL/Target
if os.path.exists(DATA_FILE):
    st.divider(); st.write("### 📜 Pro Order History")
    st.table(pd.read_csv(DATA_FILE).tail(5))
