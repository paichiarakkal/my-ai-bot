import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import os

st.set_page_config(page_title="AI Terminal", layout="wide")

# --- ഡാറ്റ ഫയൽ സെറ്റിംഗ്സ് ---
DATA_FILE = 'trade_log.csv'
if 'balance' not in st.session_state:
    if os.path.exists(DATA_FILE):
        try:
            df_hist = pd.read_csv(DATA_FILE)
            st.session_state.balance = float(df_hist['bal'].iloc[-1])
        except: st.session_state.balance = 100000.0
    else: st.session_state.balance = 100000.0

def save_trade(trade_data):
    trade_data['bal'] = st.session_state.balance
    df = pd.DataFrame([trade_data])
    df.to_csv(DATA_FILE, mode='a', header=not os.path.exists(DATA_FILE), index=False)

# --- മാർക്കറ്റ് ഡാറ്റ കാണിക്കാനുള്ള ഫങ്ക്ഷൻ ---
def show_market_data(ticker, name):
    try:
        # പ്രധാനം: auto_adjust=True ചേർത്തു, ഇത് എറർ ഒഴിവാക്കും
        df = yf.download(ticker, period="1d", interval="1m", auto_adjust=True, progress=False)
        
        if not df.empty:
            # ഡാറ്റ എടുക്കുന്ന രീതി മാറ്റി
            last_price = float(df['Close'].iloc[-1])
            
            # AI Advisor Box
            st.success(f"🚀 AI Advice: Trend is Strong for {name}")
            
            # ചാർട്ട്
            fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
            fig.update_layout(height=400, template="plotly_dark", xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)
            
            # ട്രേഡിംഗ് പാനൽ
            st.subheader(f"Wallet: ₹{st.session_state.balance:,.2f}")
            qty = st.number_input("Qty", min_value=1, value=10, key=ticker)
            c1, c2 = st.columns(2)
            
            if c1.button(f"🟢 BUY", use_container_width=True):
                st.session_state.balance -= (last_price * qty)
                save_trade({'Sym': name, 'Price': last_price, 'Type': 'BUY'})
                st.rerun()
            
            if c2.button(f"🔴 SELL", use_container_width=True):
                st.session_state.balance += (last_price * qty)
                save_trade({'Sym': name, 'Price': last_price, 'Type': 'SELL'})
                st.rerun()
        else:
            st.warning("ഡാറ്റ ലഭ്യമല്ല. മാർക്കറ്റ് അവധി ആയതുകൊണ്ടാകാം.")
            
    except Exception as e:
        st.error(f"Error: {e}")

# --- നാവിഗേഷൻ ---
st.sidebar.title("Menu")
choice = st.sidebar.selectbox("Market", ["Nifty 50", "Crude Oil", "Gold"])

if choice == "Nifty 50": show_market_data("^NSEI", "Nifty 50")
elif choice == "Crude Oil": show_market_data("CL=F", "Crude Oil")
elif choice == "Gold": show_market_data("GC=F", "Gold")

# ഹിസ്റ്ററി
if os.path.exists(DATA_FILE):
    st.divider()
    st.write("### Recent Orders")
    st.table(pd.read_csv(DATA_FILE).tail(5))
