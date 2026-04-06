import streamlit as st

# 1. നിന്റെ ഫോട്ടോയും ടൈറ്റിലും
st.set_page_config(page_title="Paichi AI Ultra", page_icon="📈", layout="wide")

# ഗോൾഡൻ & ബ്ലാക്ക് തീം (Full Screen)
st.markdown("""
    <style>
    .main { background-color: #000000; }
    [data-testid="stSidebar"] { background-color: #111111; border-right: 2px solid #FFD700; }
    h1, h2, h3, p { color: #FFD700 !important; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# 2. സൈഡ് ബാറിൽ നിന്റെ ഫോട്ടോ
st.sidebar.image("https://raw.githubusercontent.com/paichiarakkal/my-ai-bot/main/image_7.png", width=150)
st.sidebar.title("PAICHI AI ⚡")
option = st.sidebar.selectbox("SELECT MARKET", ["CRUDE OIL MCX", "NIFTY 50", "BANK NIFTY"])

# 3. ഒറിജിനൽ പ്രൈസ് സെക്ഷൻ
st.markdown(f"<h1>GOLDEN MARKET: {option} ⚡</h1>", unsafe_allow_html=True)

# ഒറിജിനൽ ചാർട്ടും വിലയും (TradingView Original Data)
# ഇതിൽ നിന്റെ 10,287 എന്ന വിലയും സൂപ്പർ ട്രെൻഡും ലൈവ് ആയി വരും.
chart_html = """
<div style="height:600px;">
  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
  <script type="text/javascript">
  new TradingView.widget({
    "autosize": true,
    "symbol": "MCX:CRUDEOIL1!",
    "interval": "5",
    "timezone": "Asia/Kolkata",
    "theme": "dark",
    "style": "1",
    "locale": "en",
    "enable_publishing": false,
    "hide_side_toolbar": false,
    "allow_symbol_change": true,
    "details": true,
    "hotlist": true,
    "calendar": true,
    "show_popup_button": true,
    "container_id": "tv_chart_faisal"
  });
  </script>
  <div id="tv_chart_faisal" style="height:100%;"></div>
</div>
"""

# ചാർട്ട് ആപ്പിൽ കാണിക്കുന്നു
st.components.v1.html(chart_html, height=620)

# 4. AI ടിപ്‌സ് (മലയാളത്തിൽ)
st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    st.success("🟢 SUPERTREND പച്ചയാണെങ്കിൽ മാത്രം BUY ചെയ്യുക.")
with col2:
    st.error("🔴 SUPERTREND ചുവപ്പാണെങ്കിൽ SELL നോക്കുക.")

st.info(f"ഹലോ ഫൈസൽ, ഇപ്പോൾ {option} മാർക്കറ്റ് ലൈവ് ആണ്. ശ്രദ്ധിച്ചു ട്രേഡ് ചെയ്യുക!")
