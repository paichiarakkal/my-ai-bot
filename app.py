import streamlit as st
import yfinance as yf
from PIL import Image
import os

# 1. പേജ് സെറ്റപ്പ് - ടൈറ്റിലും ഐക്കണും
st.set_page_config(
    page_title="Faisal's Pro Dashboard",
    page_icon="📈",
    layout="wide"
)

# 2. ആപ്പ് ഐക്കൺ വരാനുള്ള Manifest ലിങ്ക് (ഇത് പ്രധാനമാണ്)
st.markdown('<link rel="manifest" href="./manifest.json">', unsafe_allow_html=True)

# 3. ലോഗോയും പേരും കാണിക്കുന്നു
cols = st.columns([1, 4, 1])
with cols[1]:
    if os.path.exists("image_12.png"):
        img = Image.open("image_12.png")
        st.image(img, width=150)
    else:
        st.write("FAISAL ARAKKAL")
    
    st.markdown("<h1 style='text-align: center; color: #1E88E5;'>🚀 FAISAL'S PRO DASHBOARD</h1>", unsafe_allow_html=True)

# 4. ഡാറ്റ ഓർത്തുവെക്കാൻ (Cache)
@st.cache_data(ttl=300)
def get_stock_data(sym):
    try:
        df = yf.Ticker(sym).history(period="1d", interval="5m")
        return df
    except:
        return None

# 5. ഡാഷ്‌ബോർഡ് കണ്ടന്റ് (Nifty, Bank Nifty, Crude Oil)
symbols = {"Nifty 50": "^NSEI", "Bank Nifty": "^NSEBANK", "Crude Oil": "CL=F"}
main_cols = st.columns(3)

for i, (name, sym) in enumerate(symbols.items()):
    with main_cols[i]:
        df = get_stock_data(sym)
        if df is not None and not df.empty:
            price = df['Close'].iloc[-1]
            st.metric(label=name, value=f"₹{price:,.2f}")
            st.line_chart(df['Close'], use_container_width=True)
        else:
            st.warning(f"Waiting for {name} data...")

st.info("💡 Data updates every 5 minutes. Use WhatsApp for instant signals!")
