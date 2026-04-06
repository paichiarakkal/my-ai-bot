import streamlit as st

# 1. സെറ്റിംഗ്‌സും ലോഗോയും (നിന്റെ ഫോട്ടോ വരാൻ)
st.set_page_config(
    page_title="Paichi AI Ultra",
    page_icon="https://raw.githubusercontent.com/paichiarakkal/my-ai-bot/main/image_7.png",
    layout="wide"
)

# ഗോൾഡൻ സ്റ്റൈൽ CSS (കറുപ്പും സ്വർണ്ണനിറവും)
st.markdown("""
    <style>
    .main { background-color: #000000; color: #FFD700; }
    [data-testid="stSidebar"] { background-color: #111111; border-right: 2px solid #FFD700; }
    .stMetric { background-color: #1a1a1a; padding: 15px; border-radius: 10px; border: 1px solid #FFD700; }
    h1, h2, h3, p, span { color: #FFD700 !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. സൈഡ് ബാർ (നിന്റെ ഫോട്ടോയും മെനുവും)
st.sidebar.image("https://raw.githubusercontent.com/paichiarakkal/my-ai-bot/main/image_7.png", caption="FAISAL - TRADER", width=150)
st.sidebar.title("PAICHI AI ⚡")
menu = st.sidebar.radio("MENU", ["📈 LIVE MARKET", "💰 MY TRADES", "⚙️ PROFILE"])

# 3. ലൈവ് മാർക്കറ്റ് പേജ് (Investing.com Indian Chart)
if menu == "📈 LIVE MARKET":
    st.markdown("<h1>GOLDEN DASHBOARD: FAISAL ⚡</h1>", unsafe_allow_html=True)
    
    # മെട്രിക്സ്
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("MARKET", "MCX INDIA")
    with col2:
        st.metric("STATUS", "LIVE 🟢")
    with col3:
        st.metric("TIPS", "CHECK SUPERTREND")

    st.divider()

    # --- INVESTING.COM INDIAN MARKET CHART ---
    # ഇത് നിന്റെ ആപ്പിനുള്ളിൽ നേരിട്ട് ലോഡ് ആകും (MCX CRUDE)
    investing_chart = """
    <div style="height:550px; width:100%;">
        <iframe src="https://it.widgets.investing.com/live-charts-widget?force_lang=1&s=8849" width="100%" height="500" frameborder="0" allowtransparency="true" marginwidth="0" marginheight="0"></iframe>
        <div style="width:100%;text-align:center;font-size:12px;color:#FFD700;padding-top:5px;">
            <a href="https://www.investing.com/" target="_blank" style="color:#FFD700;text-decoration:none;">MCX Live Price by Investing.com</a>
        </div>
    </div>
    """
    st.components.v1.html(investing_chart, height=560)

    # ടിപ്‌സ് സെക്ഷൻ
    st.markdown("### 🔔 AI TRADING SIGNALS")
    st.success("✅ ചാർട്ടിലെ ഇൻഡിക്കേറ്ററിൽ Buy സിഗ്നൽ വന്നാൽ നോക്കുക.")
    st.error("🛑 ചാർട്ടിൽ Sell സിഗ്നൽ വന്നാൽ ശ്രദ്ധിക്കുക.")

# 4. പഴയ പേജുകൾ (മറ്റുള്ളവ)
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
    st.write("**Base:** Dubai, Al Barsha")
