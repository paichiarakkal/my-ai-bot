import streamlit as st
import yfinance as yf
from PIL import Image
import os

# 1. പേജ് സെറ്റപ്പ്
st.set_page_config(
    page_title="Faisal's Pro Dashboard",
    page_icon="📈",
    layout="wide"
)

# 2. ആപ്പ് ഐക്കൺ Manifest
st.markdown('<link rel="manifest" href="./manifest.json">', unsafe_allow_html=True)

# 3. ഹെഡർ - ഫോട്ടോയും പേരും
cols = st.columns([1, 4, 1])
with cols[1]:
    if os.path.exists("image_12.png"):
        img = Image.open("image_12.png")
        st.image(img, width=150)
    else:
        st.write("FAISAL ARAKKAL")
    st.markdown("<h1 style='text-align: center; color: #1E88E5;'>🚀 FAISAL'S PRO DASHBOARD</h1>", unsafe_allow_html=True)

# 4. കറൻസി കൺവെർട്ടർ (AED to INR)
st.sidebar.header("💰 Currency Converter")
aed_amount = st.sidebar.number_input("Enter Amount in AED (Dubai Dirham)", min_value=0.0, value=1000.0)
exchange_rate = 22.85  # ഏകദേശ വിനിമയ നിരക്ക്
inr_value = aed_amount * exchange_rate
st.sidebar.success(f"In Indian Rupee: ₹{inr_value:,.2f}")
st.sidebar.info(f"Rate: 1 AED = ₹{exchange_rate}")

# 5. ഡാറ്റ ഫെച്ചിംഗ് (Cache)
@st.cache_data(ttl=60)
def get_stock_data(sym):
    try:
        df = yf.Ticker(sym).history(period="1d", interval="1m")
        return df
    except:
        return None

# 6. ട്രേഡിംഗ് ഡാഷ്‌ബോർഡ്
symbols = {
    "Nifty 50": "^NSEI",
    "Crude Oil (MCX Est.)": "CL=F", 
    "Gold (MCX Est.)": "GC=F"
}

main_cols = st.columns(3)

for i, (name, sym) in enumerate(symbols.items()):
    with main_cols[i]:
        df = get_stock_data(sym)
        if df is not None and not df.empty:
            price = df['Close'].iloc[-1]
            # രൂപയിലേക്ക് മാറ്റിയ വില കാണിക്കുന്നു
            if "MCX" in name:
                display_price = f"₹{price * 83.30:,.2f}"
            else:
                display_price = f"₹{price:,.2f}"
                
            st.metric(label=name, value=display_price)
            st.line_chart(df['Close'], use_container_width=True)
        else:
            st.warning(f"Waiting for {name}...")

st.info("💡 Live Trading & Currency Dashboard for Faisal.")
