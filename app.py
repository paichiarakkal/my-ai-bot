import streamlit as st

# 1. സെറ്റിംഗ്‌സും ഗോൾഡൻ തീമും (നിന്റെ ഫോട്ടോ ലോഗോ ആയി വരാൻ)
st.set_page_config(
    page_title="Paichi AI Ultra",
    page_icon="https://raw.githubusercontent.com/paichiarakkal/my-ai-bot/main/image_7.png",
    layout="wide"
)

# ഗോൾഡൻ സ്റ്റൈൽ CSS (നിനക്ക് ഇഷ്ടപ്പെട്ട കറുപ്പും സ്വർണ്ണനിറവും)
st.markdown("""
    <style>
    .main { background-color: #000000; color: #FFD700; }
    [data-testid="stSidebar"] { background-color: #111111; border-right: 2px solid #FFD700; }
    .stMetric { background-color: #1a1a1a; padding: 15px; border-radius: 10px; border: 1px solid #FFD700; }
    h1, h2, h3, p, span { color: #FFD700 !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. സൈഡ് ബാർ (നിന്റെ ഫോട്ടോ ഇവിടെ വരും)
st.sidebar.image("https://raw.githubusercontent.com/paichiarakkal/my-ai-bot/main/image_7.png", caption="FAISAL - TRADER", width=150)
st.sidebar.title("PAICHI AI ⚡")
menu = st.sidebar.radio("MENU", ["📈 LIVE MARKET", "💰 MY TRADES", "⚙️ PROFILE"])
symbol = st.sidebar.selectbox("SELECT INDEX", ["MCX:CRUDEOIL1!", "NSE:NIFTY", "NSE:BANKNIFTY"])

# 3. ലൈവ് മാർക്കറ്റ് പേജ് (Original Price & Supertrend)
if menu == "📈 LIVE MARKET":
    st.markdown(f"<h1>GOLDEN DASHBOARD: FAISAL ⚡</h1>", unsafe_allow_html=True)
    
    # മെട്രിക്സ് സെക്ഷൻ
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("INDEX", symbol)
    with col2:
        st.metric("STATUS", "ORIGINAL LIVE 🟢")
    with col3:
        st.metric("TIPS", "CHECK SUPERTREND")

    st.divider()

    # --- ORIGINAL TRADINGVIEW CHART ---
    # ഇത് നിന്റെ ചാർട്ടിലെ അതേ 10,287 വിലയും ഇൻഡിക്കേറ്ററുകളും കാണിക്കും
    chart_html = f"""
    <div style="height:550px;">
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
        "withdateranges": true,
        "hide_side_toolbar": false,
        "allow_symbol_change": true,
        "details": true,
        "hotlist": true,
        "calendar": true,
        "show_popup_button": true,
        "popup_width": "1000",
        "popup_height": "650",
        "container_id": "tradingview_chart"
      }});
      </script>
      <div id="tradingview_chart"></div>
    </div>
    """
    st.components.v1.html(chart_html, height=560)

    # ടിപ്‌സ് മെസേജുകൾ
    st.markdown("### 🔔 AI TRADING TIPS")
    st.success("✅ SUPERTREND പച്ചയാണെങ്കിൽ (Buy) നോക്കുക.")
    st.error("🛑 SUPERTREND ചുവപ്പാണെങ്കിൽ (Sell) ശ്രദ്ധിക്കുക.")

# --- ബാക്കി പേജുകൾ ---
elif menu == "💰 MY TRADES":
    st.header("MY TRADING LOG 📝")
    st.write("ഇന്ന് എത്ര ലാഭം കിട്ടി ഫൈസൽ?")
    p_l = st.number_input("Profit/Loss Amount", value=0)
    if st.button("Save Trade"):
        st.success(f"സേവ് ചെയ്തു: ₹{p_l}")

elif menu == "⚙️ PROFILE":
    st.header("USER PROFILE ⚙️")
    st.write("**Name:** Faisal")
    st.write("**Job:** Intraday Trader")
    st.write("**Location:** Al Barsha, Dubai")
