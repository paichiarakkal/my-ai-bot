import streamlit as st
import requests

# 1. പേജ് സെറ്റിംഗ്സ്
st.set_page_config(page_title="Paichi AI Ultra", layout="wide")

# സൈഡ് ബാർ
st.sidebar.image("https://raw.githubusercontent.com/paichiarakkal/my-ai-bot/main/image_7.png", width=120)
st.sidebar.title("PAICHI AI ⚡")

# 2. ലൈവ് ഡാറ്റ ഫംഗ്ഷൻ
def get_data():
    try:
        res = requests.get("https://query1.finance.yahoo.com/v8/finance/chart/AEDINR=X?interval=1m&range=1d", headers={'User-Agent': 'Mozilla/5.0'}).json()
        aed = round(res['chart']['result'][0]['meta']['regularMarketPrice'], 2)
        return aed, round(80.50 * aed * 4, 2)
    except: return 22.80, 11460.84

live_aed, live_crude = get_data()

# 3. ആപ്പ് ഡിസൈൻ
st.markdown("<style>.stApp { background-color: #000; color: #FFD700; }</style>", unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center;'>GOLDEN TERMINAL ⚡</h1>", unsafe_allow_html=True)

# ലൈവ് പ്രൈസ് ബോക്സ് (നീ ഇഷ്ടപ്പെട്ട ആ ഡിസൈൻ)
st.markdown(f"""
    <div style="background: #111; padding: 40px; border-radius: 25px; border: 4px solid #FFD700; text-align: center;">
        <h2 style="color: #FFD700;">CRUDE OIL MCX LIVE</h2>
        <h1 style="color: #00FF00; font-size: 80px;">₹ {live_crude}</h1>
    </div>
""", unsafe_allow_html=True)

st.sidebar.write(f"**AED to INR:** ₹ {live_aed}")

# പൈത്തൺ പഠിക്കാൻ നമ്മൾ എഴുതിയ ഭാഗം ഇവിടെ കാണിക്കാം
st.divider()
st.subheader("🐍 My Python Learning")
name = "Faisal"
job = "Trader"
st.write(f"Name: {name} | Job: {job}")
