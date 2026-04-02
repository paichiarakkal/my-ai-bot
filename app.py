import streamlit as st
import pandas as pd
import requests
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Paichi Trader Pro", layout="wide")

# ഓട്ടോ റിഫ്രഷ് സെറ്റിംഗ്സ് (1 സെക്കൻഡ്)
st_autorefresh(interval=1000, limit=1000, key="faisal_live")

# സൈഡ് ബാർ
st.sidebar.title("💎 Paichi Menu")
choice = st.sidebar.radio("സേവനം തിരഞ്ഞെടുക്കുക:", ["Indian Indices", "Commodities & Forex", "Quick Links"])

def get_data(symbol):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1m&range=1d"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        data = response.json()
        result = data['chart']['result'][0]
        price = result['meta']['regularMarketPrice']
        return {"price": price}
    except: return None

if choice == "Indian Indices":
    st.title("📊 Indian Stock Market (Live)")
    col1, col2 = st.columns(2)
    with col1:
        d = get_data("^NSEI")
        if d: st.metric("Nifty 50", f"{d['price']:.2f}")
        
        db = get_data("^NSEBANK")
        if db: st.metric("Bank Nifty", f"{db['price']:.2f}")

elif choice == "Commodities & Forex":
    st.title("🛢️ Commodities (Live)")
    dc = get_data("CL=F")
    if dc:
        mcx_future = dc['price'] * 85.5
        st.metric("Crude Oil Future (MCX)", f"₹{mcx_future:.2f}")

    da = get_data("AEDINR=X")
    if da: st.metric("1 Dirham (AED)", f"₹{da['price']:.2f}")

else:
    st.title("🔗 Quick Access")
    st.markdown("### [🌐 Open Upstox](https://upstox.com/)")
