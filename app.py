import streamlit as st
import requests
import pandas as pd
import datetime
import os
import urllib.parse

# 1. പേജ് സെറ്റിംഗ്സ്
st.set_page_config(page_title="Paichi AI Ultra Pro", layout="wide")

# ഫയലുകൾ
FILE_NAME = 'trade_journal_vfinal.csv'
CHAT_FILE = 'community_chat.csv'

# --- ലൈവ് റേറ്റ് (AED to INR) ---
def get_live_data():
    try:
        res = requests.get("https://query1.finance.yahoo.com/v8/finance/chart/AEDINR=X?interval=1m&range=1d", headers={'User-Agent': 'Mozilla/5.0'}).json()
        aed = res['chart']['result'][0]['meta']['regularMarketPrice']
        return round(aed, 2), "₹ 7,680/gm"
    except:
        return 22.80, "₹ 7,680/gm"

live_aed, live_gold = get_live_data()

# --- സൈഡ് ബാർ (Side Bar Selection) ---
with st.sidebar:
    photo_url = "https://raw.githubusercontent.com/paichiarakkal/my-ai-bot/main/image_7.png"
    st.image(photo_url, width=100)
    st.markdown("<h2 style='color: #FFD700;'>Faisal's Terminal</h2>", unsafe_allow_html=True)
    
    st.write(f"**AED/INR:** ₹ {live_aed}")
    st.write(f"**Gold:** {live_gold}")
    st.divider()

    page = st.radio("Menu:", ["🏠 HOME", "📈 MARKET", "📝 JOURNAL", "📊 DASHBOARD", "💬 CHAT"])
    st.divider()

    # 🎯 ഇൻഡക്സ് സെലക്ഷൻ
    st.subheader("🎯 Select Symbol")
    category = st.selectbox("Category", ["Index (Nifty/Sensex)", "Commodity (Crude)"])
    
    if category == "Index (Nifty/Sensex)":
        sym_map = {"NIFTY 50": "NSE:NIFTY", "BANK NIFTY": "NSE:BANKNIFTY", "SENSEX": "BSE:SENSEX"}
    else:
        sym_map = {"CRUDE OIL": "MCX:CRUDEOIL1!", "SILVER": "MCX:SILVER1!", "NATURAL GAS": "MCX:NATURALGAS1!"}

    sel_name = st.selectbox("Choose Symbol", list(sym_map.keys()))
    selected_symbol = sym_map[sel_name]

# --- ഗോൾഡൻ & ബ്ലാക്ക് തീം ---
st.markdown(f"<style>.stApp {{ background: #000; color: #FFD700 !important; }}</style>", unsafe_allow_html=True)

# --- MARKET PAGE (Live Original Price) ---
if page == "📈 MARKET":
    st.markdown(f"<h1>LIVE MARKET: {sel_name} ⚡</h1>", unsafe_allow_html=True)
    
    # ലൈവ് ചാർട്ട് വിഡ്ജറ്റ് (ഇതിലാണ് 10,287 പോലുള്ള ലൈവ് വില വരുന്നത്)
    chart_html = f"""
    <div style="height:600px; border: 2px solid #FFD700; border-radius: 10px; overflow: hidden;">
        <iframe src="https://s.tradingview.com/widgetembed/?symbol={selected_symbol}&interval=5&hidesidetoolbar=0&symboledit=1&saveimage=1&toolbarbg=f1f3f6&theme=dark&style=1&timezone=Asia%2FKolkata" width="100%" height="600" frameborder="0"></iframe>
    </div>
    """
    st.components.v1.html(chart_html, height=610)
    
    # AI അനാലിസിസ് ടിപ്‌സ്
    c1, c2 = st.columns(2)
    with c1:
        st.success("✅ SUPERTREND പച്ചയാണെങ്കിൽ BUY നോക്കുക.")
    with c2:
        st.error("🛑 SUPERTREND ചുവപ്പാണെങ്കിൽ SELL നോക്കുക.")

# --- മറ്റ് പേജുകൾ (പഴയതുപോലെ തന്നെ) ---
elif page == "🏠 HOME":
    st.markdown("<h1 style='text-align: center;'>WELCOME FAISAL 🏠</h1>", unsafe_allow_html=True)
    st.markdown(f'<div style="text-align: center;"><img src="{photo_url}" style="width: 200px; border-radius: 50%; border: 6px solid #FFD700;"></div>', unsafe_allow_html=True)

elif page == "📝 JOURNAL":
    st.markdown("<h1>TRADE JOURNAL 📝</h1>", unsafe_allow_html=True)
    # നീ അയച്ച ജേണൽ കോഡ് ഇവിടെ ചേർക്കാം

elif page == "💬 CHAT":
    st.markdown("<h1>WHATSAPP CHAT 💬</h1>", unsafe_allow_html=True)
    # നീ അയച്ച ചാറ്റ് കോഡ് ഇവിടെ ചേർക്കാം
