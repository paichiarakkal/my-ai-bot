import streamlit as st
import streamlit.components.v1 as components

# 1. Page Settings
st.set_page_config(page_title="FTB PRO TERMINAL", layout="wide")

# 2. Custom CSS to hide Streamlit header/footer for Clean Look
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .main { background-color: #131722; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: SYMBOL SELECTION ---
st.sidebar.title("🚀 FTB PRO")
symbol = st.sidebar.selectbox("Select Asset", ["NIFTY", "BANKNIFTY", "CRUDEOIL", "RELIANCE", "SBIN"])

# Mapping symbols to TradingView format
tv_symbols = {
    "NIFTY": "NSE:NIFTY",
    "BANKNIFTY": "NSE:BANKNIFTY",
    "CRUDEOIL": "MCX:CRUDEOIL1!",
    "RELIANCE": "NSE:RELIANCE",
    "SBIN": "NSE:SBIN"
}

# --- TRADINGVIEW WIDGET (The Magic Part) ---
st.markdown(f"### 📈 {symbol} Live Chart")

# ഈ വിഡ്ജറ്റ് ആണ് ട്രേഡിംഗ് വ്യൂവിന്റെ അതേ ലുക്ക് നിനക്ക് തരുന്നത്
tv_widget = f"""
<div class="tradingview-widget-container" style="height:100%;width:100%">
  <div id="tradingview_chart"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
  <script type="text/javascript">
  new TradingView.widget({{
    "autosize": true,
    "symbol": "{tv_symbols[symbol]}",
    "interval": "5",
    "timezone": "Asia/Kolkata",
    "theme": "dark",
    "style": "1",
    "locale": "en",
    "toolbar_bg": "#f1f3f6",
    "enable_publishing": false,
    "hide_top_toolbar": false,
    "hide_legend": false,
    "save_image": false,
    "container_id": "tradingview_chart"
  }});
  </script>
</div>
"""

# Displaying the widget
components.html(tv_widget, height=600)

st.sidebar.divider()
st.sidebar.info("Use the tools inside the chart to add Indicators and Trendlines.")
