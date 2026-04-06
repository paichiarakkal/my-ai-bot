import streamlit as st
import pandas as pd
import requests

# 1. സെറ്റിംഗ്‌സും ഗോൾഡൻ തീമും
st.set_page_config(
    page_title="Paichi AI Ultra",
    page_icon="https://raw.githubusercontent.com/paichiarakkal/my-ai-bot/main/image_7.png",
    layout="wide"
)

# ഗോൾഡൻ സ്റ്റൈൽ CSS
st.markdown("""
    <style>
    .main { background-color: #000000; color: #FFD700; }
    .stMetric { background-color: #1a1a1a; padding: 15px; border-radius: 10px; border: 1px solid #FFD700; }
    h1, h2, h3 { color: #FFD700 !important; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# 2. സൈഡ് ബാർ
st.sidebar.image("https://raw.githubusercontent.com/paichiarakkal/my-ai-bot/main/image_7.png", width=120)
st.sidebar.title("PAICHI AI ⚡")
menu = st.sidebar.radio("MENU", ["📈 LIVE MARKET", "💰 MY TRADES", "⚙️ PROFILE"])
symbol = st.sidebar.selectbox("SELECT INDEX", ["MCX:CRUDEOIL1!", "NSE:NIFTY", "NSE:BANKNIFTY"])

# 3. ലൈവ് മാർക്കറ്റ് പേജ്
if menu == "📈 LIVE MARKET":
    st.markdown(f"<h1>GOLDEN DASHBOARD: FAISAL ⚡</h1>", unsafe_allow_html=True)
    
    # മെട്രിക്സ് സെക്ഷൻ (Original Price & Status)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("CURRENT INDEX", symbol)
    with col2:
        st.metric("MARKET STATUS", "LIVE 🟢")
    with col3:
        st.metric("STRATEGY", "SUPERTREND + VWAP")

    st.divider()

    # --- ORIGINAL MCX & NIFTY CHART (TradingView Widget) ---
    # ഇത് നിന്റെ ചാർട്ടിലെ അതേ ഒറിജിനൽ വിലയും ഇൻഡിക്കേറ്ററുകളും കാണിക്കും
    chart_html = f"""
    <div class="tradingview-widget-container" style="height:500px;">
      <div id="tradingview_chart"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({{
        "autosize": true,
        "symbol": "{symbol}",
        "interval": "5",
        "timezone": "Asia/Kolkata",
        "theme": "dark",
        "style": "1",
        "locale": "en",
        "toolbar_bg": "#f1f3f6",
        "enable_publishing": false,
        "hide_top_toolbar": false,
        "withdateranges": true,
        "save_image": false,
        "container_id": "tradingview_chart"
      }});
      </script>
    </div>
    """
    st.components.v1.html(chart_html, height=520)

    # 4. ട്രേഡിംഗ് ടിപ്‌സ് & ഇൻഡിക്കേറ്റർ മെസേജ്
    st.markdown("### 🔔 AI TRADING SIGNALS")
    t1, t2 = st.columns(2)
    with t1:
        st.success("✅ SUPERTREND: Buy Above Green Line")
    with t2:
        st.error("🛑 SUPERTREND: Sell Below Red Line")
    
    st.info("💡 Tip: ക്രൂഡ് ഓയിലിൽ 10,280 ലെവൽ ശ്രദ്ധിക്കുക. വോളിയം കൂടുന്നുണ്ട്.")

# --- പഴയ പേജുകൾ നിലനിർത്തിയിട്ടുണ്ട് ---
elif menu == "💰 MY TRADES":
    st.header("MY TRADING LOG 📝")
    profit = st.number_input("ഇന്നത്തെ ലാഭം/നഷ്ടം നൽകുക", value=0)
    if st.button("Save Entry"):
        st.success(f"സേവ് ചെയ്തു! ഇന്നത്തെ ലാഭം: ₹{profit}")

elif menu == "⚙️ PROFILE":
    st.header("USER SETTINGS ⚙️")
    st.write("**Name:** Faisal")
    st.write("**Role:** Intraday Trader (MCX & Options)")
    st.write("**Base:** Dubai, Al Barsha")
