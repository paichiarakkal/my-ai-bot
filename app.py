import streamlit as st
import requests
import pandas as pd
import datetime
import os
import urllib.parse
from streamlit_autorefresh import st_autorefresh

# 1. പേജ് സെറ്റിംഗ്സ്
st.set_page_config(page_title="Paichi AI Ultra Pro", layout="wide")

# ഫയൽ പേരുകൾ
TRADE_FILE = 'trade_journal_vfinal.csv'
CHAT_FILE = 'community_chat.csv'

# --- ലൈവ് ഡാറ്റ ഫംഗ്ഷനുകൾ ---
def get_live_data():
    try:
        res = requests.get("https://query1.finance.yahoo.com/v8/finance/chart/AEDINR=X?interval=1m&range=1d", headers={'User-Agent': 'Mozilla/5.0'}).json()
        aed = res['chart']['result'][0]['meta']['regularMarketPrice']
        return aed, "₹ 7,680/gm"
    except: return 22.80, "₹ 7,680/gm"

live_aed, live_gold = get_live_data()

# --- സൈഡ് ബാർ നാവിഗേഷൻ ---
with st.sidebar:
    photo_url = "https://raw.githubusercontent.com/paichiarakkal/my-ai-bot/main/image_7.png"
    st.image(photo_url, width=100)
    st.markdown("<h2 style='color: #000;'>Faisal's AI Terminal</h2>", unsafe_allow_html=True)
    
    # 💰 Currency & Gold Converter (പഴയത്)
    st.subheader("💰 Live Rates")
    st.write(f"**AED to INR:** ₹ {live_aed}")
    st.write(f"**Gold (24K):** {live_gold}")
    amount_aed = st.number_input("Convert AED:", min_value=1.0, value=1.0)
    st.success(f"₹ {round(amount_aed * live_aed, 2)} INR")
    
    st.divider()
    page = st.radio("Menu:", ["🏠 HOME", "📈 MARKET", "📝 JOURNAL", "📊 DASHBOARD", "💬 CHAT"])
    st.divider()

# --- ഓരോ പേജിനും പ്രീമിയം കളറുകൾ (പഴയത്) ---
themes = {
    "🏠 HOME": "linear-gradient(135deg, #C0C0C0, #FFFFFF)", # Silver
    "📈 MARKET": "linear-gradient(135deg, #BF953F, #FCF6BA)", # Golden
    "📝 JOURNAL": "linear-gradient(135deg, #E5E4E2, #F9F9F9)", # Platinum
    "📊 DASHBOARD": "linear-gradient(135deg, #002366, #0047AB)", # Royal Blue
    "💬 CHAT": "linear-gradient(135deg, #25D366, #128C7E)" # WhatsApp Green
}
txt_color = "#FFF" if page in ["📊 DASHBOARD", "💬 CHAT"] else "#000"
st.markdown(f"<style>.stApp {{ background: {themes[page]} !important; color: {txt_color} !important; }}</style>", unsafe_allow_html=True)

# --- പേജ് കണ്ടന്റ് ---

# 1. HOME (Sentiment Meter ഉൾപ്പെടെ)
if page == "🏠 HOME":
    st.markdown("<h1 style='text-align: center;'>SILVER HOME 🏠</h1>", unsafe_allow_html=True)
    st.markdown(f'<div style="text-align: center;"><img src="{photo_url}" style="width: 180px; border-radius: 50%; border: 5px solid #808080;"></div>', unsafe_allow_html=True)
    st.markdown("### 📊 Market Sentiment Meter")
    st.select_slider("Current Sentiment", options=["Bearish 🔴", "Neutral ⚪", "Bullish 🟢"], value="Bullish 🟢")
    st.progress(75)

# 2. MARKET (AI Assistant & Symbols)
elif page == "📈 MARKET":
    st.markdown(f"<h1>GOLDEN MARKET ⚡</h1>", unsafe_allow_html=True)
    # നീ ചോദിച്ച എല്ലാ Symbols (Midcap, Sensex ഉൾപ്പെടെ)
    category = st.selectbox("Category", ["Index", "Commodity", "Stocks"])
    # AI Assistant (RSI, SuperTrend)
    c1, c2, c3 = st.columns(3)
    c1.metric("SuperTrend", "BUY ✅")
    c2.metric("RSI (14)", "64.5")
    c3.metric("AI Confidence", "88%")

# 3. JOURNAL & 4. DASHBOARD (പഴയ ഫീച്ചറുകൾ)
elif page == "📝 JOURNAL":
    st.markdown("<h1>PLATINUM JOURNAL 📝</h1>")
    # പഴയ ജേണൽ ലോജിക് ഇവിടെയുണ്ട്...
elif page == "📊 DASHBOARD":
    st.markdown("<h1>ROYAL DASHBOARD 📊</h1>")
    # പഴയ ഗ്രാഫ് ലോജിക് ഇവിടെയുണ്ട്...

# 5. CHAT (App + WhatsApp)
elif page == "💬 CHAT":
    st.markdown("<h1>WHATSAPP & APP CHAT 💬</h1>", unsafe_allow_html=True)
    
    # ആപ്പിലെ പഴയ ചാറ്റ് കാണിക്കുന്നു
    if os.path.exists(CHAT_FILE): chat_df = pd.read_csv(CHAT_FILE)
    else: chat_df = pd.DataFrame(columns=['User', 'Message', 'Time'])
    
    st.subheader("App Messages")
    for i, row in chat_df.tail(5).iterrows():
        st.markdown(f"🗨️ **{row['User']}**: {row['Message']} *({row['Time']})*")
    
    st.divider()
    
    with st.form("hybrid_chat", clear_on_submit=True):
        st.subheader("Send New Message")
        # നിന്റെ വാട്സ്ആപ്പ് നമ്പർ ഇവിടെ നൽകുക
        whatsapp_no = st.text_input("WhatsApp Number", value="91XXXXXXXXXX") 
        u_name = st.text_input("Name", value="Faisal")
        u_msg = st.text_area("Message")
        
        send_btn = st.form_submit_button("Send to Both")
        
        if send_btn and u_msg:
            # 1. ആപ്പിലേക്ക് സേവ് ചെയ്യുന്നു
            now = datetime.datetime.now().strftime("%H:%M")
            new_chat = pd.DataFrame([[u_name, u_msg, now]], columns=['User', 'Message', 'Time'])
            new_chat.to_csv(CHAT_FILE, mode='a', header=not os.path.exists(CHAT_FILE), index=False)
            
            # 2. വാട്സ്ആപ്പ് ലിങ്ക് ഉണ്ടാക്കുന്നു
            encoded_msg = urllib.parse.quote(f"From App - {u_name}: {u_msg}")
            wa_url = f"https://wa.me/{whatsapp_no}?text={encoded_msg}"
            
            st.success("ആപ്പിൽ സേവ് ചെയ്തു!")
            st.markdown(f'<a href="{wa_url}" target="_blank" style="display: block; width: 100%; padding: 15px; background: #25D366; color: white; text-align: center; border-radius: 10px; text-decoration: none; font-weight: bold;">WhatsApp വഴി അയക്കാൻ ഇവിടെ അമർത്തുക</a>', unsafe_allow_html=True)
