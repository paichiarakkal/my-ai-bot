st.set_page_config(page_title="Paichi AI", page_icon=photo_url, layout="wide")import streamlit as st
import requests
import pandas as pd
import datetime
import os
import urllib.parse
from streamlit_autorefresh import st_autorefresh

# 1. പേജ് സെറ്റിംഗ്സ്
st.set_page_config(page_title="Paichi AI Ultra Pro", layout="wide")

# ഫയലുകൾ
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

# --- സൈഡ് ബാർ ---
with st.sidebar:
    photo_url = "https://raw.githubusercontent.com/paichiarakkal/my-ai-bot/main/image_7.png"
    st.image(photo_url, width=100)
    st.markdown("<h2 style='color: #000;'>Faisal's AI Terminal</h2>", unsafe_allow_html=True)
    
    st.subheader("💰 Live Rates")
    st.write(f"**AED to INR:** ₹ {live_aed}")
    st.write(f"**Gold:** {live_gold}")
    amount_aed = st.number_input("Convert AED:", min_value=1.0, value=1.0)
    st.success(f"₹ {round(amount_aed * live_aed, 2)} INR")
    
    st.divider()
    page = st.radio("Menu:", ["🏠 HOME", "📈 MARKET", "⏰ MARKET WATCH", "📝 JOURNAL", "📊 DASHBOARD", "💬 CHAT"])
    st.divider()

    # Symbol Selection
    category = st.selectbox("Category", ["Index (Nifty/Sensex)", "Commodity (Crude)", "Nifty 50 Stocks"])
    if category == "Index (Nifty/Sensex)":
        sym_map = {"NIFTY 50": "NSE:NIFTY", "BANK NIFTY": "NSE:BANKNIFTY", "SENSEX": "BSE:SENSEX", "MIDCAP SELECT": "NSE:NIFTY_MID_SELECT"}
    elif category == "Commodity (Crude)":
        sym_map = {"CRUDE OIL": "MCX:CRUDEOIL1!", "SILVER": "MCX:SILVER1!", "NATURAL GAS": "MCX:NATURALGAS1!"}
    else:
        sym_map = {"RELIANCE": "NSE:RELIANCE", "HDFC BANK": "NSE:HDFCBANK", "TATA MOTORS": "NSE:TATAMOTORS", "SBI": "NSE:SBIN"}

    sel_name = st.selectbox("Choose Symbol", list(sym_map.keys()))
    st.session_state.name = sel_name
    st.session_state.url = f"https://in.tradingview.com/chart/?symbol={sym_map[sel_name]}"

# --- തീം സെറ്റിംഗ്സ് ---
themes = {
    "🏠 HOME": "linear-gradient(135deg, #C0C0C0, #FFFFFF)",
    "📈 MARKET": "linear-gradient(135deg, #BF953F, #FCF6BA)",
    "⏰ MARKET WATCH": "linear-gradient(135deg, #FF6B6B, #FFE66D)", # New Color
    "📝 JOURNAL": "linear-gradient(135deg, #E5E4E2, #F9F9F9)",
    "📊 DASHBOARD": "linear-gradient(135deg, #002366, #0047AB)",
    "💬 CHAT": "linear-gradient(135deg, #25D366, #128C7E)"
}
txt_color = "#FFF" if page in ["📊 DASHBOARD", "💬 CHAT", "⏰ MARKET WATCH"] else "#000"
st.markdown(f"<style>.stApp {{ background: {themes[page]} !important; color: {txt_color} !important; }}</style>", unsafe_allow_html=True)

# --- പേജ് കണ്ടന്റ് ---

# 1. HOME
if page == "🏠 HOME":
    st.markdown("<h1 style='text-align: center;'>SILVER HOME 🏠</h1>", unsafe_allow_html=True)
    st.markdown(f'<div style="text-align: center;"><img src="{photo_url}" style="width: 180px; border-radius: 50%; border: 5px solid #808080;"></div>', unsafe_allow_html=True)
    tips = ["നഷ്ടം കുറയ്ക്കുക, ലാഭം തനിയെ വന്നോളും. 📉", "മാർക്കറ്റ് എപ്പോഴും അവിടെയുണ്ടാകും. ⏳", "ട്രെൻഡ് നിന്റെ സുഹൃത്താണ്. 🤝", "സ്റ്റോപ്പ് ലോസ് മാറ്റരുത്. 🛑", "ഓവർ ട്രേഡിംഗ് ഒഴിവാക്കുക. ⚠️"]
    st.info(f"**💡 ഇന്നത്തെ ടിപ്പ്:** {tips[datetime.datetime.now().weekday() % 5]}")
    st.select_slider("Market Sentiment", options=["Bearish 🔴", "Neutral ⚪", "Bullish 🟢"], value="Bullish 🟢")

# 2. MARKET
elif page == "📈 MARKET":
    st.markdown(f"<h1>GOLDEN MARKET: {st.session_state.name} ⚡</h1>")
    st.markdown(f'<a href="{st.session_state.url}" target="_blank" style="display:block; padding:10px; background:#000; color:#FFD700; text-align:center; border-radius:10px; text-decoration:none;">📈 OPEN CHART</a>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("VWAP", "ABOVE ✅")
    c2.metric("MACD", "BULLISH ▲")
    c3.metric("AI Confidence", "92%")

# 3. ⏰ MARKET WATCH (പുതിയ പേജ്)
elif page == "⏰ MARKET WATCH":
    st.markdown("<h1>MARKET TIMER & NEWS ⏰</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🌍 Market Timings")
        st.write("🇮🇳 **NSE/BSE:** 09:15 AM - 03:30 PM")
        st.write("🇦🇪 **Dubai (GST):** 07:45 AM - 02:00 PM")
        st.write("🇺🇸 **US Market:** 07:00 PM - 01:30 AM (IST)")
        st.write("🛢️ **MCX (Crude):** 09:00 AM - 11:30 PM")

    with col2:
        st.subheader("📰 Global News Alert")
        st.warning("⚠️ **US FED Meeting:** വ്യാഴാഴ്ച രാത്രി ശ്രദ്ധിക്കുക!")
        st.info("🛢️ **Crude Inventory:** ബുധനാഴ്ച രാത്രി 8:00 PM (IST)")
        st.error("📉 **Inflation Data:** മാർക്കറ്റിൽ വലിയ വോളറ്റിലിറ്റിക്ക് സാധ്യത!")

# 4. JOURNAL, 5. DASHBOARD, 6. CHAT (പഴയത് പോലെ തന്നെ)
elif page == "📝 JOURNAL":
    st.markdown("<h1>PLATINUM JOURNAL 📝</h1>")
    # ... (പഴയ ജേണൽ കോഡ്)
elif page == "📊 DASHBOARD":
    st.markdown("<h1>ROYAL DASHBOARD 📊</h1>")
    # ... (പഴയ ഡാഷ്‌ബോർഡ് കോഡ്)
elif page == "💬 CHAT":
    st.markdown("<h1>WHATSAPP & APP CHAT 💬</h1>")
    if os.path.exists(CHAT_FILE): chat_df = pd.read_csv(CHAT_FILE)
    else: chat_df = pd.DataFrame(columns=['User', 'Message', 'Time'])
    for i, row in chat_df.tail(5).iterrows(): st.markdown(f"🗨️ **{row['User']}**: {row['Message']}")
    with st.form("chat"):
        wa_no = st.text_input("WhatsApp No", value="91XXXXXXXXXX")
        u_msg = st.text_area("Message")
        if st.form_submit_button("Send"):
            now = datetime.datetime.now().strftime("%H:%M")
            pd.DataFrame([["Faisal", u_msg, now]], columns=['User', 'Message', 'Time']).to_csv(CHAT_FILE, mode='a', header=not os.path.exists(CHAT_FILE), index=False)
            st.markdown(f'<a href="https://wa.me/{wa_no}?text={u_msg}" target="_blank" style="display:block; padding:10px; background:#25D366; color:white; text-align:center; border-radius:10px; text-decoration:none;">Send to WhatsApp</a>', unsafe_allow_html=True)
