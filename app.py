import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import os

st.set_page_config(page_title="AI Terminal", layout="wide")

# --- ഡാറ്റ ലോഡിംഗ് & സേവിംഗ് ---
DATA_FILE = 'terminal_data.csv'
if 'balance' not in st.session_state:
    if os.path.exists(DATA_FILE):
        df_save = pd.read_csv(DATA_FILE)
        st.session_state.balance = float(df_save['bal'].iloc[-1])
    else:
        st.session_state.balance = 100000.0

def save_bal():
    pd.DataFrame({'bal': [st.session_state.balance]}).to_csv(DATA_FILE, index=False)

# --- മെയിൻ ഫങ്ക്ഷൻ ---
def show_market_data(ticker, name):
    try:
        # ഡാറ്റ ഡൗൺലോഡ് ചെയ്യുന്നു
        df = yf.download(ticker, period="2d", interval="5m", progress=False)
        
        if not df.empty:
            # വാല്യൂസ് എടുക്കുമ്പോൾ .item() ഉപയോഗിക്കുന്നത് എറർ ഒഴിവാക്കും
            last_price = float(df['Close'].iloc[-1])
            open_price = float(df['Open'].iloc[0])
            change = last_price - open_price
            
            st.metric(f"{name} Live", f"₹{last_price:,.2f}", f"{change:+.2f}")

            # ചാർട്ട്
            fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], 
                    high=df['High'], low=df['Low'], close=df['Close'])])
            fig.update_layout(height=400, margin=dict(l=0,r=0,t=0,b=0), template="plotly_white", xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)
            
            # പേപ്പർ ട്രേഡിംഗ് സെക്ഷൻ
            st.subheader(f"Wallet: ₹{st.session_state.balance:,.2f}")
            col1, col2 = st.columns(2)
            qty = st.number_input(f"Quantity for {name}", min_value=1, value=1, key=ticker)
            
            if col1.button(f"🟢 BUY {name}", use_container_width=True):
                st.session_state.balance -= (last_price * qty)
                save_bal()
                st.success("Trade Success!")
                st.rerun()
            
            if col2.button(f"🔴 SELL {name}", use_container_width=True):
                st.session_state.balance += (last_price * qty)
                save_bal()
                st.warning("Position Closed!")
                st.rerun()
    except Exception as e:
        st.error(f"Error in {name}: {e}")

# --- സൈഡ്ബാർ നാവിഗേഷൻ ---
st.sidebar.title("📈 Market Hub")
choice = st.sidebar.selectbox("Choose Asset", ["Nifty 50", "Crude Oil", "Gold", "USD/INR Calculator"])

if choice == "Nifty 50":
    show_market_data("^NSEI", "Nifty 50")
elif choice == "Crude Oil":
    show_market_data("CL=F", "Crude Oil (Intl)")
elif choice == "Gold":
    show_market_data("GC=F", "Gold Futures")
elif choice == "USD/INR Calculator":
    st.header("💱 Currency Exchange")
    rate_data = yf.download("INR=X", period="1d")
    if not rate_data.empty:
        rate = float(rate_data['Close'].iloc[-1])
        st.write(f"Current Rate: 1 USD = ₹{rate:.2f}")
        usd = st.number_input("Enter USD ($)", value=1.0)
        st.success(f"In Indian Rupees: ₹{usd * rate:,.2f}")
