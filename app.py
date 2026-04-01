import streamlit as st
import streamlit.components.v1 as components

# 1. Page Settings (43641.jpg പോലെ പ്രൊഫഷണൽ ആക്കാൻ)
st.set_page_config(page_title="FTB PRO TERMINAL", layout="wide")

# 2. Dark Mode UI - ബാക്ക്ഗ്രൗണ്ട് കറുപ്പാക്കാൻ (43641.jpg ലുക്ക്)
st.markdown("""
    <style>
    .main { background-color: #131722; }
    header { visibility: hidden; }
    footer { visibility: hidden; }
    .stSidebar { background-color: #171b26; border-right: 1px solid #2a2e39; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: WATCHLIST (43632.jpg പോലെയുള്ള സെലക്ഷൻ) ---
st.sidebar.title("🚀 FTB PRO")
selected_asset = st.sidebar.selectbox("Select Market", 
    ["NIFTY", "BANKNIFTY", "CRUDEOIL", "RELIANCE", "TATA MOTORS", "SBI"])

# TradingView-ലേക്ക് നൽകേണ്ട സിംബലുകൾ
symbol_dict = {
    "NIFTY": "NSE:NIFTY",
    "BANKNIFTY": "NSE:BANKNIFTY",
    "CRUDEOIL": "MCX:CRUDEOIL1!",
    "RELIANCE": "NSE:RELIANCE",
    "TATA MOTORS": "NSE:TATAMOTORS",
    "SBI": "NSE:SBIN"
}

# --- ADVANCED CHART WIDGET (The Real Pro Look) ---
st.markdown(f"<h3 style='color:white; text-align:center;'>📈 {selected_asset} Advanced Terminal</h3>", unsafe_allow_html=True)

# 43633.jpg-ലെ പോലെ എല്ലാ ഇൻഡിക്കേറ്ററുകളും ടൂൾസും കിട്ടാനുള്ള വിഡ്ജറ്റ്
tv_chart = f"""
<div class="tradingview-widget-container" style="height:600px;width:100%">
  <div id="tradingview_pro"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
  <script type="text/javascript">
  new TradingView.widget({{
    "autosize": true,
    "symbol": "{symbol_dict[selected_asset]}",
    "interval": "5",
    "timezone": "Asia/Kolkata",
    "theme": "dark",
    "style": "1",
    "locale": "en",
    "toolbar_bg": "#131722",
    "enable_publishing": false,
    "withdateranges": true,
    "hide_side_toolbar": false,
    "allow_symbol_change": true,
    "details": true,
    "hotlist": true,
    "calendar": true,
    "container_id": "tradingview_pro"
  }});
  </script>
</div>
"""

# വിഡ്ജറ്റ് ആപ്പിൽ ഡിസ്‌പ്ലേ ചെയ്യുന്നു
components.html(tv_chart, height=620)

st.sidebar.info("ഈ ചാർട്ടിന് മുകളിലുള്ള 'fx' ബട്ടണിൽ ക്ലിക്ക് ചെയ്താൽ നിനക്ക് സൂപ്പർട്രെൻഡ് (Supertrend) ഉൾപ്പെടെയുള്ള എല്ലാ ഇൻഡിക്കേറ്ററുകളും ചേർക്കാം.")
