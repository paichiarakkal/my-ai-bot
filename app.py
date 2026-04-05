import streamlit as st
import requests
import pandas as pd
import datetime
import os
from streamlit_autorefresh import st_autorefresh

# 1. പേജ് സെറ്റിംഗ്സ്
st.set_page_config(page_title="Paichi AI Ultra Pro", layout="wide")

# ഫയലുകൾ
TRADE_FILE = 'trade_journal_vfinal.csv'
CHAT_FILE = 'community_chat.csv'

# --- ലൈവ് ഡാറ്റ & മീറ്റർ ലോജിക് ---
def get_live_data():
    try:
        res = requests.get("https://query1.finance.yahoo.com/v8/finance/chart/AEDINR=X?interval=1m&range=1d", headers={'User-Agent': 'Mozilla/5.0'}).json()
        aed = res['chart']['result'][0]['meta']['regularMarketPrice']
        return aed, "₹ 7,680/gm"
    except: return 22.80, "₹ 7,680/gm"

live_aed, live_gold = get_live_data()

# --- സൈഡ് ബാർ ---
with st.sidebar:
    photo_url = "https://raw.githubusercontent.com/paichiarakkal/my-ai-bot/main/image_7.png"
    st.image(photo_url, width=100)
    st.markdown("<h2 style='color: #000;'>Faisal's AI Terminal</h2>", unsafe_allow_html=True)
    
    st.subheader("💰 Live Rates")
    st.write(f"**AED to INR:** ₹ {live_aed}")
    amount_aed = st.number_input("Convert AED:", min_value=1.0, value=1.0)
    st.success(f"₹ {round(amount_aed * live_aed, 2)} INR")
    
    st.divider()
    page = st.radio("Menu:", ["🏠 HOME", "📈 MARKET", "📝 JOURNAL", "📊 DASHBOARD", "💬 CHAT"])
    st.divider()

# --- കളർ തീം ---
themes = {
    "🏠 HOME": "linear-gradient(135deg, #C0C0C0, #FFFFFF)",
    "📈 MARKET": "linear-gradient(135deg, #BF953F, #FCF6BA)",
    "📝 JOURNAL": "linear-gradient(135deg, #E5E4E2, #F9F9F9)",
    "📊 DASHBOARD": "linear-gradient(135deg, #002366, #0047AB)",
    "💬 CHAT": "linear-gradient(135deg, #2C3E50, #4CA1AF)"
}
txt_color = "#FFF" if page in ["📊 DASHBOARD", "💬 CHAT"] else "#000"
st.markdown(f"<style>.stApp {{ background: {themes[page]} !important; color: {txt_color} !important; }}</style>", unsafe_allow_html=True)

# --- പേജ് കണ്ടന്റ് ---

# 1. HOME (Market Sentiment Meter)
if page == "🏠 HOME":
    st.markdown("<h1 style='text-align: center;'>SILVER HOME 🏠</h1>", unsafe_allow_html=True)
    st.markdown(f'<div style="text-align: center;"><img src="{photo_url}" style="width: 150px; border-radius: 50%; border: 4px solid #808080;"></div>', unsafe_allow_html=True)
    
    st.markdown("### 📊 Market Sentiment Meter")
    sentiment = 75 # ഇത് പിന്നീട് ലൈവ് ആക്കാം
    st.select_slider("Current Sentiment", options=["Bearish 🔴", "Neutral ⚪", "Bullish 🟢"], value="Bullish 🟢")
    st.progress(sentiment)
    st.write(f"മാർക്കറ്റ് ഇപ്പോൾ **{sentiment}% Bullish** ആണ്. ബൈ സൈഡ് അവസരങ്ങൾ നോക്കാം!")

# 2. MARKET (AI Indicators)
elif page == "📈 MARKET":
    st.markdown("<h1>GOLDEN MARKET ⚡</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    c1.metric("SuperTrend", "BUY ✅")
    c2.metric("RSI (14)", "64.5")
    st.info("AI നിർദ്ദേശം: ട്രെൻഡ് പോസിറ്റീവ് ആണ്.")

# 3. JOURNAL
elif page == "📝 JOURNAL":
    st.markdown("<h1>PLATINUM JOURNAL 📝</h1>", unsafe_allow_html=True)
    # പഴയ ജേണൽ കോഡ് ഇവിടെ ഉപയോഗിക്കാം

# 4. DASHBOARD
elif page == "📊 DASHBOARD":
    st.markdown("<h1>ROYAL DASHBOARD 📊</h1>", unsafe_allow_html=True)
    st.metric("Total Profit", "₹ 2,350")

# 5. COMMUNITY CHAT (പുതിയ ഫീച്ചർ)
elif page == "💬 CHAT":
    st.markdown("<h1>COMMUNITY CHAT 💬</h1>", unsafe_allow_html=True)
    
    # ചാറ്റ് ലോഡ് ചെയ്യുന്നു
    if os.path.exists(CHAT_FILE): chat_df = pd.read_csv(CHAT_FILE)
    else: chat_df = pd.DataFrame(columns=['User', 'Message', 'Time'])

    with st.container():
        st.write("---")
        for i, row in chat_df.tail(10).iterrows():
            st.markdown(f"**{row['User']}**: {row['Message']}  *({row['Time']})*")
        st.write("---")

    with st.form("chat_form", clear_on_submit=True):
        u_name = st.text_input("നിന്റെ പേര്", value="Faisal")
        u_msg = st.text_input("സന്ദേശം ടൈപ്പ് ചെയ്യുക...")
        if st.form_submit_button("Send"):
            now = datetime.datetime.now().strftime("%H:%M")
            new_chat = pd.DataFrame([[u_name, u_msg, now]], columns=['User', 'Message', 'Time'])
            new_chat.to_csv(CHAT_FILE, mode='a', header=not os.path.exists(CHAT_FILE), index=False)
            st.rerun()
