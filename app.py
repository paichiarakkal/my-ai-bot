import streamlit as st
import yfinance as yf
from PIL import Image

# 1. ലോഗോ സേവ് ചെയ്യുക:
# ഈ കോഡ് സേവ് ചെയ്യുന്നതിന് മുൻപ് നിങ്ങളുടെ image_12.png ഫോട്ടോ GitHub-ൽ app.py ഉള്ള അതേ ഫോൾഡറിൽ അപ്‌ലോഡ് ചെയ്യണം.
# അല്ലെങ്കിൽ താഴെയുള്ള line കമന്റ് ചെയ്യുക.

# 2. പേജ് സെറ്റപ്പ് - ഐക്കൺ ചേർക്കുന്നു
st.set_page_config(
    page_title="Faisal's Pro Dashboard",
    page_icon="📈", # ഇമോജി ഐക്കൺ (പടം സെറ്റാകുന്നതു വരെ)
    layout="wide"
)

# 3. ലോഗോയും പേരും കാണിക്കുന്നു (ഡാഷ്‌ബോർഡിന്റെ മുകളിൽ)
cols = st.columns([1, 4, 1]) # മൂന്ന് കോളങ്ങൾ (നടുവിൽ പേരും പടവും)
with cols[1]:
    try:
        # ലോഗോ ഫോട്ടോ GitHub-ൽ അപ്‌ലോഡ് ചെയ്തിട്ടുണ്ടെങ്കിൽ ഇത് പ്രവർത്തിക്കും
        img = Image.open("image_12.png") 
        st.image(img, caption="Faisal Arakkal", width=150) # പടം
    except:
        st.write("FAISAL ARAKKAL") # പടം കിട്ടിയില്ലെങ്കിൽ പേര്

    st.markdown("<h1 style='text-align: center; color: #1E88E5;'>🚀 FAISAL'S PRO DASHBOARD</h1>", unsafe_allow_html=True)


# 4. ഡാറ്റ ഓർത്തുവെക്കാൻ (Cache)
@st.cache_data(ttl=300)
def get_stock_data(sym):
    try:
        df = yf.Ticker(sym).history(period="1d", interval="5m")
        return df
    except:
        return None

# 5. ഡാഷ്‌ബോർഡ് കണ്ടന്റ്
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
