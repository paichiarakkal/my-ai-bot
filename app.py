import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Faisal's Pro Terminal", layout="wide")

# --- സൈഡ്ബാറിൽ വാച്ച്‌ലിസ്റ്റ് ---
st.sidebar.title("💎 Markets")
market_choice = st.sidebar.radio("ചെക്ക് ചെയ്യേണ്ടത് തിരഞ്ഞെടുക്കുക:", 
    ["Nifty 50", "Crude Oil", "Gold", "Currency (USD/INR)", "Watchlist"])

# --- കറൻസി കാൽക്കുലേറ്റർ ഫങ്ക്ഷൻ ---
def currency_converter():
    st.subheader("💱 Currency Calculator")
    usd_rate = yf.Ticker("INR=X").history(period="1d")['Close'].iloc[-1]
    col1, col2 = st.columns(2)
    usd_amt = col1.number_input("Amount in USD ($)", value=1.0)
    inr_amt = usd_amt * usd_rate
    col2.metric("Equivalent INR (₹)", f"₹{inr_amt:,.2f}")
    st.write(f"Current Exchange Rate: 1 USD = ₹{usd_rate:.2f}")

# --- ഡാറ്റ കാണിക്കാനുള്ള ഫങ്ക്ഷൻ ---
def show_market_data(ticker, name):
    st.header(f"📊 {name}")
    data = yf.download(ticker, period="1d", interval="5m")
    if not data.empty:
        last_price = data['Close'].iloc[-1]
        change = last_price - data['Open'].iloc[0]
        st.metric("Current Price", f"{last_price:,.2f}", f"{change:+.2f}")
        
        # ലളിതമായ ചാർട്ട്
        fig = go.Figure(data=[go.Candlestick(x=data.index, open=data['Open'], 
                high=data['High'], low=data['Low'], close=data['Close'])])
        fig.update_layout(height=400, template="plotly_white", xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

# --- മെയിൻ ലോജിക് ---
if market_choice == "Nifty 50":
    show_market_data("^NSEI", "Nifty 50 Index")
    
elif market_choice == "Crude Oil":
    show_market_data("CL=F", "Crude Oil Futures") # International Price
    
elif market_choice == "Gold":
    show_market_data("GC=F", "Gold Futures")
    
elif market_choice == "Currency (USD/INR)":
    currency_converter()
    show_market_data("INR=X", "USD to INR Trend")

elif market_choice == "Watchlist":
    st.subheader("📋 Your Watchlist")
    # വാച്ച്‌ലിസ്റ്റിലേക്ക് സ്റ്റോക്കുകൾ ആഡ് ചെയ്യാൻ
    sym = st.text_input("Enter Stock Symbol (eg: SBIN.NS)")
    if sym:
        show_market_data(sym, sym)
