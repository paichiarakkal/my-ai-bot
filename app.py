import streamlit as st
import yfinance as yf

st.set_page_config(page_title="Faisal's Dashboard", layout="wide")
st.title("🚀 FAISAL'S PRO DASHBOARD")

symbols = {"Nifty 50": "^NSEI", "Bank Nifty": "^NSEBANK", "Crude Oil": "CL=F"}
cols = st.columns(3)

for i, (name, sym) in enumerate(symbols.items()):
    with cols[i]:
        df = yf.Ticker(sym).history(period="1d", interval="5m")
        if not df.empty:
            price = df['Close'].iloc[-1]
            st.metric(label=name, value=f"₹{price:,.2f}")
            st.line_chart(df['Close'])

st.success("Dashboard is Live! Use WhatsApp for signals.")
