import streamlit as st
import requests

# 1. സെറ്റിംഗ്‌സ്
st.set_page_config(page_title="Paichi AI Ultra", layout="wide")

# ഗോൾഡൻ തീം
st.markdown("""
    <style>
    .main { background-color: #000000; color: #FFD700; }
    [data-testid="stSidebar"] { background-color: #111111; border-right: 2px solid #FFD700; }
    .stMetric { background-color: #1a1a1a; padding: 15px; border-radius: 10px; border: 1px solid #FFD700; }
    h1, h2, h3, p, span { color: #FFD700 !important; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# 2. സൈഡ് ബാർ (നിന്റെ ഫോട്ടോ)
st.sidebar.image("https://raw.githubusercontent.com/paichiarakkal/my-ai-bot/main/image_7.png", width=150)
st.sidebar.title("PAICHI AI ⚡")
menu = st.sidebar.radio("MENU", ["📈 LIVE MARKET", "💰 MY TRADES"])

if menu == "📈 LIVE MARKET":
    st.markdown("<h1>GOLDEN DASHBOARD: FAISAL ⚡</h1>", unsafe_allow_html=True)
    
    # മെട്രിക്സ്
    c1, c2, c3 = st.columns(3)
    c1.metric("MARKET", "MCX INDIA")
    c2.metric("STATUS", "LIVE 🟢")
    c3.metric("TIPS", "CHECK SUPERTREND")

    st.divider()

    # --- പുതിയ ചാർട്ട് ലിങ്ക് (ഇത് 404 വരില്ല) ---
    # ട്രേഡിംഗ് വ്യൂവിന്റെ വിഡ്ജറ്റ് തന്നെ നമുക്ക് ഒന്നുകൂടി ക്ലീൻ ആയി കൊടുക്കാം
    chart_html = """
    <div style="height:550px; border: 2px solid #FFD700; border-radius: 10px; overflow: hidden;">
        <iframe src="https://s.tradingview.com/widgetembed/?symbol=MCX%3ACRUDEOIL1!&interval=5&hidesidetoolbar=0&symboledit=1&saveimage=1&toolbarbg=f1f3f6&studies=SuperTrend%40tv-basicstudies&theme=dark&style=1&timezone=Asia%2FKolkata" width="100%" height="550" frameborder="0"></iframe>
    </div>
    """
    st.components.v1.html(chart_html, height=560)

    st.info("💡 ചാർട്ട് വന്നില്ലെങ്കിൽ മുകളിലെ റിഫ്രഷ് ബട്ടൺ ഒന്ന് അമർത്തൂ ഫൈസൽ.")

elif menu == "💰 MY TRADES":
    st.header("MY TRADING LOG 📝")
    st.write("ഇന്ന് എത്ര ലാഭം കിട്ടി?")
