import streamlit as st

# പേജ് സെറ്റിംഗ്സ്
st.set_page_config(page_title="Paichi AI Ultra", layout="wide")

# സൈഡ് ബാറിൽ നിന്റെ ഫോട്ടോ വരാൻ (ലിങ്ക് ചെക്ക് ചെയ്യുക)
st.sidebar.image("https://raw.githubusercontent.com/paichiarakkal/my-ai-bot/main/image_7.png", width=150)
st.sidebar.title("PAICHI AI ⚡")

st.markdown("<h1 style='text-align: center; color: #FFD700;'>GOLDEN MARKET: CRUDE OIL ⚡</h1>", unsafe_allow_html=True)

# ഇതാണ് ആ ഒറിജിനൽ ചാർട്ട് വരാനുള്ള കോഡ്
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
    "show_popup_button": true,
    "container_id": "tv_faisal_final"
  });
  </script>
  <div id="tv_faisal_final" style="height:100%;"></div>
</div>
"""

st.components.v1.html(chart_html, height=620)
