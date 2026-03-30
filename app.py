import streamlit as st
import yfinance as yf

# 1. പേജ് സെറ്റപ്പ്
st.set_page_config(page_title="Faisal's Dashboard", layout="wide")
st.markdown("<h1 style='text-align: center; color: #1E88E5;'>🚀 FAISAL'S PRO DASHBOARD</h1>", unsafe_allow_html=True)

# 2. ഡാറ്റ ഓർത്തുവെക്കാൻ (Cache) - ഇത് എറർ വരുന്നത് ഒഴിവാക്കും
@st.cache_data(ttl=300)
def get_stock_data(sym):
    try:
        df = yf.Ticker(sym).history(period="1d", interval="5m")
        return df
    except:
        return None

# 3. ഡാഷ്‌ബോർഡ് കണ്ടന്റ്
symbols = {"Nifty 50": "^NSEI", "Bank Nifty": "^NSEBANK", "Crude Oil": "CL=F"}
cols = st.columns(3)

for i, (name, sym) in enumerate(symbols.items()):
    with cols[i]:
        df = get_stock_data(sym)
        if df is not None and not df.empty:
            price = df['Close'].iloc[-1]
            st.metric(label=name, value=f"₹{price:,.2f}")
            st.line_chart(df['Close'], use_container_width=True)
        else:
            st.warning(f"Waiting for {name} data...")

st.info("💡 Tip: Data updates every 5 minutes. Check WhatsApp for instant signals!")
