import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import os

st.set_page_config(page_title="AI Terminal", layout="wide")

# --- ഡാറ്റ ലോഡിംഗ് & സേവിംഗ് ---
DATA_FILE = 'terminal_data.csv'
if 'balance' not in st.session_state:
    if os.path.exists(DATA_FILE):
        df_save = pd.read_csv(DATA_FILE)
        st.session_state.balance = float(df_save['bal'].iloc[-1])
    else: st.session_state.balance = 100000.0

def save_bal():
    pd.DataFrame({'bal': [st.session_state.balance]}).to_csv(DATA_FILE, index=False)

# --- AI അഡ്വൈസർ ലോജിക് ---
def get_ai_advice(df):
    close = df['Close'].values.flatten()
    # ലളിതമായ സൂപ്പർട്രെൻഡ് ലോജിക്
    if close[-1] > close[-5]:
        return "🚀 AI SIGNAL: BULLISH (Trend is UP. Good to Buy)", "green"
    else:
        return "⚠️ AI SIGNAL: BEARISH (Trend is DOWN. Be Careful)", "red"

def show_market_data(ticker, name):
    try:
        df = yf.download(ticker, period="2d", interval="5m", progress=False)
        if not df.empty:
            last_price = float(df['Close'].iloc[-1])
            advice, color = get_ai_advice(df)

            # --- AI അസിസ്റ്റന്റ് ബോക്സ് (ഇതാണ് നീ തിരഞ്ഞത്) ---
            st.markdown(f"""
                <div style="padding:15px; border-radius:10px; border-left: 8px solid {color}; background-color:#f0f2f6; margin-bottom:20px;">
                    <h3 style="color:{color}; margin:0;">{advice}</h3>
                    <p style="margin:5px 0 0 0; color:gray;">Current Price: ₹{last_price:,.2f}</p>
                </div>
            """, unsafe_allow_html=True)

            # ചാർട്ട്
            fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
            fig.update_layout(height=400, template="plotly_white", xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)
            
            # ട്രേഡിംഗ് പാനൽ
            st.subheader(f"Wallet: ₹{st.session_state.balance:,.2f}")
            col1, col2 = st.columns(2)
            qty = st.number_input(f"Qty for {name}", min_value=1, value=1, key=ticker)
            
            if col1.button(f"🟢 BUY {name}", use_container_width=True):
                st.session_state.balance -= (last_price * qty)
                save_bal(); st.rerun()
            
            if col2.button(f"🔴 SELL {name}", use_container_width=True):
                st.session_state.balance += (last_price * qty)
                save_bal(); st.rerun()
    except Exception as e: st.error(f"Error: {e}")

# --- നാവിഗേഷൻ ---
st.sidebar.title("📈 Market Hub")
choice = st.sidebar.selectbox("Choose Asset", ["Nifty 50", "Crude Oil", "Gold", "USD/INR Calculator"])

if choice == "Nifty 50": show_market_data("^NSEI", "Nifty 50")
elif choice == "Crude Oil": show_market_data("CL=F", "Crude Oil")
elif choice == "Gold": show_market_data("GC=F", "Gold Futures")
elif choice == "USD/INR Calculator":
    st.header("💱 Currency Exchange")
    rate = float(yf.download("INR=X", period="1d")['Close'].iloc[-1])
    usd = st.number_input("Enter USD ($)", value=1.0)
    st.success(f"In Rupees: ₹{usd * rate:,.2f}")
