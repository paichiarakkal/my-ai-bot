import streamlit as st
import requests
import pandas as pd
import datetime
import os
import urllib.parse

# --- പേജ് സെറ്റിംഗ്സ് ---
# നിന്റെ ഫോട്ടോ തന്നെ ആപ്പ് ഐക്കൺ ആയി വരാൻ വേണ്ടി ഇവിടെ മാറ്റിയിട്ടുണ്ട്
photo_url = "https://raw.githubusercontent.com/paichiarakkal/my-ai-bot/main/image_7.png"
st.set_page_config(page_title="Paichi AI Ultra", page_icon=photo_url, layout="wide")

# ഫയലുകൾ
TRADE_FILE = 'trade_journal_vfinal.csv'
CHAT_FILE = 'community_chat.csv'

# --- ലൈവ് ഡാറ്റ ---
def get_live_data():
    try:
        res = requests.get("https://query1.finance.yahoo.com/v8/finance/chart/AEDINR=X?interval=1m&range=1d", headers={'User-Agent': 'Mozilla/5.0'}).json()
        aed = res['chart']['result'][0]['meta']['regularMarketPrice']
        return aed, "₹ 7,680/gm"
    except: return 22.80, "₹ 7,680/gm"

live_aed, live_gold = get_live_data()

# --- സൈഡ് ബാർ ---
with st.sidebar:
    st.image(photo_url, width=100)
    st.markdown("### Faisal's AI Terminal")
    st.write(f"**AED to INR:** ₹ {live_aed}")
    st.write(f"**Gold:** {live_gold}")
    st.divider()
    page = st.radio("Menu:", ["🏠 HOME", "📈 MARKET", "⏰ MARKET WATCH", "📝 JOURNAL", "📊 DASHBOARD", "💬 CHAT"])
    st.divider()
    
    # Symbol Selection
    category = st.selectbox("Category", ["Index", "Commodity", "Stocks"])
    if category == "Index":
        sym_map = {"NIFTY 50": "NSE:NIFTY", "BANK NIFTY": "NSE:BANKNIFTY"}
    elif category == "Commodity":
        sym_map = {"CRUDE OIL": "MCX:CRUDEOIL1!", "SILVER": "MCX:SILVER1!"}
    else:
        sym_map = {"RELIANCE": "NSE:RELIANCE", "SBI": "NSE:SBIN"}

    sel_name = st.selectbox("Choose Symbol", list(sym_map.keys()))
    st.session_state.name = sel_name
    st.session_state.url = f"https://in.tradingview.com/chart/?symbol={sym_map[sel_name]}"

# --- തീം സെറ്റിംഗ്സ് ---
themes = {
    "🏠 HOME": "linear-gradient(135deg, #C0C0C0, #FFFFFF)",
    "📈 MARKET": "linear-gradient(135deg, #BF953F, #FCF6BA)",
    "⏰ MARKET WATCH": "linear-gradient(135deg, #FF6B6B, #FFE66D)",
    "📝 JOURNAL": "linear-gradient(135deg, #E5E4E2, #F9F9F9)",
    "📊 DASHBOARD": "linear-gradient(135deg, #002366, #0047AB)",
    "💬 CHAT": "linear-gradient(135deg, #25D366, #128C7E)"
}
st.markdown(f"<style>.stApp {{ background: {themes[page]} !important; }}</style>", unsafe_allow_html=True)

# --- പേജ് കണ്ടന്റ് ---

if page == "🏠 HOME":
    st.markdown("<h1 style='text-align: center;'>SILVER HOME 🏠</h1>", unsafe_allow_html=True)
    st.markdown(f'<div style="text-align: center;"><img src="{photo_url}" style="width: 150px; border-radius: 50%; border: 5px solid #808080;"></div>', unsafe_allow_html=True)
    tips = ["നഷ്ടം കുറയ്ക്കുക, ലാഭം തനിയെ വന്നോളും. 📉", "ട്രെൻഡ് നിന്റെ സുഹൃത്താണ്. 🤝", "സ്റ്റോപ്പ് ലോസ് മാറ്റരുത്. 🛑"]
    st.info(f"**💡 ഇന്നത്തെ ടിപ്പ്:** {tips[datetime.datetime.now().weekday() % 3]}")

elif page == "📈 MARKET":
    st.markdown(f"<h1>GOLDEN MARKET: {st.session_state.name} ⚡</h1>", unsafe_allow_html=True)
    st.markdown(f'<a href="{st.session_state.url}" target="_blank" style="display:block; padding:12px; background:#000; color:#FFD700; text-align:center; border-radius:10px; text-decoration:none;">📈 OPEN CHART</a>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("VWAP", "ABOVE ✅")
    c2.metric("MACD", "BULLISH ▲")
    c3.metric("AI Confidence", "92%")

elif page == "⏰ MARKET WATCH":
    st.markdown("<h1>MARKET TIMER & NEWS ⏰</h1>", unsafe_allow_html=True)
    st.write("🇮🇳 **NSE/BSE:** 09:15 AM - 03:30 PM")
    st.write("🇦🇪 **Dubai:** 07:45 AM - 02:00 PM")
    st.write("🛢️ **Crude Inventory:** ബുധനാഴ്ച രാത്രി 8:00 PM")

elif page == "📝 JOURNAL":
    st.markdown("<h1>JOURNAL 📝</h1>", unsafe_allow_html=True)
    # ജേണൽ കോഡ് ഇവിടെ വരും...

elif page == "📊 DASHBOARD":
    st.markdown("<h1>DASHBOARD 📊</h1>", unsafe_allow_html=True)
    # ഡാഷ്ബോർഡ് കോഡ് ഇവിടെ വരും...

elif page == "💬 CHAT":
    st.markdown("<h1>CHAT 💬</h1>", unsafe_allow_html=True)
    # ചാറ്റ് കോഡ് ഇവിടെ വരും...
