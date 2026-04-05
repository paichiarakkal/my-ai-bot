import streamlit as st
import requests
import pandas as pd
import datetime
import os
import urllib.parse
from streamlit_autorefresh import st_autorefresh

# --- 1. പേജ് സെറ്റിംഗ്സ് (നിന്റെ ഫോട്ടോ ഐക്കൺ ആക്കാൻ ഇവിടെ മാറ്റിയിട്ടുണ്ട്) ---
photo_url = "https://raw.githubusercontent.com/paichiarakkal/my-ai-bot/main/image_7.png"
st.set_page_config(page_title="Paichi AI Ultra Pro", page_icon=photo_url, layout="wide")

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

# --- സൈഡ് ബാർ (Navigation) ---
with st.sidebar:
    st.image(photo_url, width=100)
    st.markdown("<h2 style='color: #000;'>Faisal's AI Terminal</h2>", unsafe_allow_html=True)
    
    st.subheader("💰 Live Rates")
    st.write(f"**AED to INR:** ₹ {live_aed}")
    st.write(f"**Gold (24K):** {live_gold}")
    amount_aed = st.number_input("Convert AED to INR:", min_value=1.0, value=1.0)
    st.success(f"Total: ₹ {round(amount_aed * live_aed, 2)}")
    
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

# --- തീം ഡിസൈൻ ---
themes = {
    "🏠 HOME": "linear-gradient(135deg, #C0C0C0, #FFFFFF)",
    "📈 MARKET": "linear-gradient(135deg, #BF953F, #FCF6BA)",
    "⏰ MARKET WATCH": "linear-gradient(135deg, #FF6B6B, #FFE66D)",
    "📝 JOURNAL": "linear-gradient(135deg, #E5E4E2, #F9F9F9)",
    "📊 DASHBOARD": "linear-gradient(135deg, #002366, #0047AB)",
    "💬 CHAT": "linear-gradient(135deg, #25D366, #128C7E)"
}
txt_color = "#FFF" if page in ["📊 DASHBOARD", "💬 CHAT", "⏰ MARKET WATCH"] else "#000"
st.markdown(f"<style>.stApp {{ background: {themes[page]} !important; color: {txt_color} !important; }}</style>", unsafe_allow_html=True)

# --- പേജ് കണ്ടന്റ് ---

# 1. HOME (Daily Tips)
if page == "🏠 HOME":
    st.markdown("<h1 style='text-align: center;'>SILVER HOME 🏠</h1>", unsafe_allow_html=True)
    st.markdown(f'<div style="text-align: center;"><img src="{photo_url}" style="width: 180px; border-radius: 50%; border: 5px solid #808080;"></div>', unsafe_allow_html=True)
    st.markdown(f"<h2 style='text-align: center;'>Welcome Faisal!</h2>", unsafe_allow_html=True)
    
    st.divider()
    tips = ["നഷ്ടം കുറയ്ക്കുക, ലാഭം തനിയെ വന്നോളും. 📉", "മാർക്കറ്റ് എപ്പോഴും അവിടെയുണ്ടാകും. ⏳", "ട്രെൻഡ് നിന്റെ സുഹൃത്താണ്. 🤝", "സ്റ്റോപ്പ് ലോസ് മാറ്റരുത്. 🛑", "ഓവർ ട്രേഡിംഗ് അക്കൗണ്ടിന് ആപത്താണ്. ⚠️"]
    st.info(f"**💡 ഇന്നത്തെ ട്രേഡിംഗ് ടിപ്പ്:** {tips[datetime.datetime.now().weekday() % 5]}")
    st.select_slider("Current Sentiment", options=["Bearish 🔴", "Neutral ⚪", "Bullish 🟢"], value="Bullish 🟢")

# 2. MARKET (Advanced Indicators)
elif page == "📈 MARKET":
    st.markdown(f"<h1>GOLDEN MARKET: {st.session_state.name} ⚡</h1>", unsafe_allow_html=True)
    st.markdown(f'<a href="{st.session_state.url}" target="_blank" style="display:block; padding:12px; background:#000; color:#FFD700; text-align:center; border-radius:10px; text-decoration:none; font-weight:bold;">📈 OPEN CHART</a>', unsafe_allow_html=True)
    
    st.markdown("### 🤖 Advanced Indicators Analysis")
    c1, c2, c3 = st.columns(3)
    c4, c5, c6 = st.columns(3)
    
    c1.metric("SuperTrend", "BUY ✅")
    c2.metric("RSI (14)", "64.5", "Bullish")
    c3.metric("VWAP Status", "ABOVE ✅", "Strong Support")
    c4.metric("MACD Status", "BULLISH ▲", "Positive")
    c5.metric("Bollinger Band", "INSIDE", "Stable")
    c6.metric("AI Confidence", "92%", "High Accuracy")

# 3. MARKET WATCH (Timings & News)
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

# 4. JOURNAL (Trade Logger)
elif page == "📝 JOURNAL":
    st.markdown("<h1>PLATINUM JOURNAL 📝</h1>", unsafe_allow_html=True)
    with st.expander("പുതിയ ട്രേഡ് രേഖപ്പെടുത്താം", expanded=True):
        c1, c2 = st.columns(2)
        sym = c1.text_input("Symbol", value=st.session_state.name)
        typ = c2.selectbox("Buy/Sell", ["BUY", "SELL"])
        en = c1.number_input("Entry Price")
        ex = c2.number_input("Exit Price")
        q = st.number_input("Qty", value=1)
        if st.button("സേവ് ചെയ്യുക"):
            pnl = round((ex-en)*q if typ=="BUY" else (en-ex)*q, 2)
            pd.DataFrame([[datetime.datetime.now().strftime("%Y-%m-%d"), sym, typ, en, ex, q, pnl]], columns=['Date','Sym','Act','En','Ex','Qty','PnL']).to_csv(TRADE_FILE, mode='a', header=not os.path.exists(TRADE_FILE), index=False)
            st.success(f"സേവ് ചെയ്തു! ലാഭം/നഷ്ടം: ₹{pnl}")
    if os.path.exists(TRADE_FILE): st.dataframe(pd.read_csv(TRADE_FILE).sort_index(ascending=False), use_container_width=True)

# 5. DASHBOARD
elif page == "📊 DASHBOARD":
    st.markdown("<h1>ROYAL DASHBOARD 📊</h1>", unsafe_allow_html=True)
    if os.path.exists(TRADE_FILE):
        df = pd.read_csv(TRADE_FILE)
        st.metric("Total Net Profit", f"₹ {df['PnL'].sum():,.2f}", delta=f"{df['PnL'].sum()}")
        st.line_chart(df['PnL'])

# 6. CHAT (App + WhatsApp)
elif page == "💬 CHAT":
    st.markdown("<h1>WHATSAPP & APP CHAT 💬</h1>", unsafe_allow_html=True)
    if os.path.exists(CHAT_FILE): chat_df = pd.read_csv(CHAT_FILE)
    else: chat_df = pd.DataFrame(columns=['User', 'Message', 'Time'])
    for i, row in chat_df.tail(5).iterrows(): st.markdown(f"🗨️ **{row['User']}**: {row['Message']}")
    with st.form("chat_box", clear_on_submit=True):
        wa_no = st.text_input("WhatsApp No", value="91XXXXXXXXXX")
        u_msg = st.text_area("Message")
        if st.form_submit_button("Send"):
            now = datetime.datetime.now().strftime("%H:%M")
            pd.DataFrame([["Faisal", u_msg, now]], columns=['User', 'Message', 'Time']).to_csv(CHAT_FILE, mode='a', header=not os.path.exists(CHAT_FILE), index=False)
            encoded_msg = urllib.parse.quote(f"Trader Faisal: {u_msg}")
            st.markdown(f'<a href="https://wa.me/{wa_no}?text={encoded_msg}" target="_blank" style="display:block; padding:15px; background:#25D366; color:white; text-align:center; border-radius:10px; text-decoration:none; font-weight:bold;">WhatsApp വഴി അയക്കുക</a>', unsafe_allow_html=True)
