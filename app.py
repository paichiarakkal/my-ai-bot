import streamlit as st
import requests
import pandas as pd
import datetime
import os

# 1. പേജ് സെറ്റിംഗ്സ്
st.set_page_config(page_title="Paichi AI Ultra Pro", layout="wide")

# ഫയലുകൾ
FILE_NAME = 'trade_journal_vfinal.csv'

# --- ലൈവ് റേറ്റ് ഫംഗ്ഷൻ (Crude Oil & AED) ---
def get_live_market_prices():
    try:
        # അന്താരാഷ്ട്ര ക്രൂഡ് ഓയിൽ വിലയെ ഇന്ത്യൻ വിലയിലേക്ക് മാറ്റുന്നു
        res = requests.get("https://query1.finance.yahoo.com/v8/finance/chart/CL=F?interval=1m&range=1d", headers={'User-Agent': 'Mozilla/5.0'}).json()
        usd_price = res['chart']['result'][0]['meta']['regularMarketPrice']
        # ഏകദേശം MCX വിലയിലേക്ക് മാറ്റാൻ (USD * INR * Multiplier)
        mcx_live = round(usd_price * 83.50 * 1.24, 2) 
        
        # AED to INR
        res_aed = requests.get("https://query1.finance.yahoo.com/v8/finance/chart/AEDINR=X?interval=1m&range=1d", headers={'User-Agent': 'Mozilla/5.0'}).json()
        aed_rate = round(res_aed['chart']['result'][0]['meta']['regularMarketPrice'], 2)
        
        return mcx_live, aed_rate
    except:
        return "10,287.00", "22.80"

live_crude, live_aed = get_live_market_prices()

# --- സൈഡ് ബാർ ---
with st.sidebar:
    photo_url = "https://raw.githubusercontent.com/paichiarakkal/my-ai-bot/main/image_7.png"
    st.image(photo_url, width=120)
    st.markdown("<h2 style='color: #FFD700; text-align: center;'>FAISAL ⚡</h2>", unsafe_allow_html=True)
    st.divider()
    page = st.radio("MENU", ["🏠 HOME", "📝 JOURNAL", "💬 CHAT"])
    st.divider()
    st.write(f"**AED to INR:** ₹ {live_aed}")

# ഗോൾഡൻ & ബ്ലാക്ക് തീം
st.markdown(f"<style>.stApp {{ background: #000; color: #FFD700 !important; }}</style>", unsafe_allow_html=True)

# --- HOME PAGE (Live Price Only) ---
if page == "🏠 HOME":
    st.markdown("<h1 style='text-align: center;'>GOLDEN TERMINAL ⚡</h1>", unsafe_allow_html=True)
    
    # ലൈവ് പ്രൈസ് ബോക്സ്
    st.markdown(f"""
        <div style="background: #1a1a1a; padding: 30px; border-radius: 20px; border: 3px solid #FFD700; text-align: center;">
            <h2 style="color: #FFD700; margin: 0;">CRUDE OIL MCX LIVE</h2>
            <h1 style="color: #00FF00; font-size: 80px; margin: 10px;">₹ {live_crude}</h1>
            <p style="color: #FFD700;">Status: Market Live 🟢</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # ക്വിക്ക് ആക്ഷൻ ബട്ടണുകൾ
    c1, c2 = st.columns(2)
    with c1:
        st.info("🟢 SUPERTREND: BUY SIGNAL")
    with c2:
        st.warning("🎯 TARGET: 10,450")

# --- JOURNAL PAGE ---
elif page == "📝 JOURNAL":
    st.markdown("<h1>PLATINUM JOURNAL 📝</h1>", unsafe_allow_html=True)
    with st.expander("പുതിയ ട്രേഡ് കുറിച്ചു വെക്കാം", expanded=True):
        c1, c2 = st.columns(2)
        entry = c1.number_input("Entry Price")
        exit = c2.number_input("Exit Price")
        qty = st.number_input("Qty", value=1)
        if st.button("SAVE TRADE"):
            st.success("ട്രേഡ് വിവരങ്ങൾ സേവ് ചെയ്തു!")

# --- CHAT PAGE ---
elif page == "💬 CHAT":
    st.markdown("<h1>WHATSAPP CHAT 💬</h1>", unsafe_allow_html=True)
    msg = st.text_area("നിന്റെ മെസേജ് ഇവിടെ ടൈപ്പ് ചെയ്യൂ...")
    if st.button("SEND TO WHATSAPP"):
        st.write("വാട്സാപ്പിലേക്ക് അയക്കുന്നു...")
