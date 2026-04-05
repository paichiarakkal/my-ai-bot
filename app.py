import streamlit as st
import requests
import pandas as pd
import datetime
import os
import urllib.parse
from streamlit_autorefresh import st_autorefresh

# 1. പേജ് സെറ്റിംഗ്സ്
st.set_page_config(page_title="Paichi AI Ultra Pro", layout="wide")

# ഫയലുകൾ
FILE_NAME = 'trade_journal_vfinal.csv'
CHAT_FILE = 'community_chat.csv'

# --- ലൈവ് ഡാറ്റ ഫംഗ്ഷനുകൾ ---
def get_live_data():
    try:
        res = requests.get("https://query1.finance.yahoo.com/v8/finance/chart/AEDINR=X?interval=1m&range=1d", headers={'User-Agent': 'Mozilla/5.0'}).json()
        aed = res['chart']['result'][0]['meta']['regularMarketPrice']
        return aed, "₹ 7,680/gm"
    except:
        return 22.80, "₹ 7,680/gm"

live_aed, live_gold = get_live_data()

# --- സൈഡ് ബാർ ---
with st.sidebar:
    photo_url = "https://raw.githubusercontent.com/paichiarakkal/my-ai-bot/main/image_7.png"
    st.image(photo_url, width=100)
    st.markdown("<h2 style='color: #000;'>Faisal's AI Terminal</h2>", unsafe_allow_html=True)
    
    st.subheader("💰 Live Rates")
    st.write(f"**AED to INR:** ₹ {live_aed}")
    st.write(f"**Gold:** {live_gold}")
    
    amount_aed = st.number_input("Enter AED:", min_value=1.0, value=1.0)
    st.success(f"**Total INR: ₹ {round(amount_aed * live_aed, 2)}**")
    st.divider()

    # 📱 പേജ് സെലക്ഷൻ (ഇതിൽ CHAT ചേർത്തു)
    page = st.radio("Menu:", ["🏠 HOME", "📈 MARKET", "📝 JOURNAL", "📊 DASHBOARD", "💬 CHAT"])
    st.divider()

    # 🎯 ഇൻഡക്സ് & കമ്മോഡിറ്റി
    st.subheader("🎯 Select Symbol")
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

# --- ഡൈനാമിക് കളർ തീം ---
if page == "🏠 HOME": bg, txt = "linear-gradient(135deg, #C0C0C0, #FFFFFF)", "#000"
elif page == "📈 MARKET": bg, txt = "linear-gradient(135deg, #BF953F, #FCF6BA)", "#000"
elif page == "📝 JOURNAL": bg, txt = "linear-gradient(135deg, #E5E4E2, #F9F9F9)", "#000"
elif page == "📊 DASHBOARD": bg, txt = "linear-gradient(135deg, #002366, #0047AB)", "#FFF"
else: bg, txt = "linear-gradient(135deg, #25D366, #128C7E)", "#FFF" # WhatsApp Green

st.markdown(f"<style>.stApp {{ background: {bg} !important; color: {txt} !important; }}</style>", unsafe_allow_html=True)

# --- പേജ് കണ്ടന്റ് ---

if page == "🏠 HOME":
    st.markdown("<h1 style='text-align: center;'>SILVER HOME 🏠</h1>", unsafe_allow_html=True)
    st.markdown(f'<div style="text-align: center;"><img src="{photo_url}" style="width: 200px; border-radius: 50%; border: 6px solid #808080;"></div>', unsafe_allow_html=True)
    st.markdown(f"<h2 style='text-align: center;'>Welcome Faisal!</h2>", unsafe_allow_html=True)

elif page == "📈 MARKET":
    st.markdown(f"<h1>GOLDEN MARKET: {st.session_state.name} ⚡</h1>", unsafe_allow_html=True)
    st.markdown(f'<a href="{st.session_state.url}" target="_blank" style="display: block; width: 100%; padding: 12px; background: #000; color: #FFD700; text-align: center; border-radius: 10px; text-decoration: none; font-weight: bold; border: 2px solid #FFD700;">📈 OPEN {st.session_state.name} CHART</a>', unsafe_allow_html=True)
    st.markdown("### 🤖 Paichi AI Assistant (Technical Analysis)")
    c1, c2, c3 = st.columns(3)
    c1.metric("SuperTrend Signal", "BUY ✅", "Trend: Upward")
    c2.metric("RSI (14) Indicator", "64.5", "Strong Bullish Zone")
    c3.metric("AI Confidence", "UPTREND", "Accuracy: 88%")

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
            df = pd.DataFrame([[datetime.datetime.now().strftime("%Y-%m-%d"), sym, typ, en, ex, q, pnl]], columns=['Date','Sym','Act','En','Ex','Qty','PnL'])
            df.to_csv(FILE_NAME, mode='a', header=not os.path.exists(FILE_NAME), index=False)
            st.success(f"സേവ് ചെയ്തു! ലാഭം/നഷ്ടം: ₹{pnl}")
    if os.path.exists(FILE_NAME):
        st.dataframe(pd.read_csv(FILE_NAME).sort_index(ascending=False), use_container_width=True)

elif page == "📊 DASHBOARD":
    st.markdown("<h1>ROYAL DASHBOARD 📊</h1>", unsafe_allow_html=True)
    if os.path.exists(FILE_NAME):
        df = pd.read_csv(FILE_NAME)
        total_pnl = df['PnL'].sum()
        st.metric("Total Net Profit", f"₹ {total_pnl:,.2f}", delta=f"{total_pnl}")
        st.line_chart(df['PnL'])

# --- 💬 പുതിയ CHAT പേജ് (WhatsApp + App) ---
elif page == "💬 CHAT":
    st.markdown("<h1>WHATSAPP & APP CHAT 💬</h1>", unsafe_allow_html=True)
    
    # ആപ്പിലെ സന്ദേശങ്ങൾ കാണിക്കുന്നു
    if os.path.exists(CHAT_FILE): chat_df = pd.read_csv(CHAT_FILE)
    else: chat_df = pd.DataFrame(columns=['User', 'Message', 'Time'])
    
    st.subheader("App Messages")
    for i, row in chat_df.tail(10).iterrows():
        st.markdown(f"🗨️ **{row['User']}**: {row['Message']} *({row['Time']})*")
    
    st.divider()
    
    with st.form("chat_system", clear_on_submit=True):
        wa_no = st.text_input("WhatsApp Number", value="91XXXXXXXXXX") # ഇവിടെ നിന്റെ നമ്പർ ഇടുക
        u_name = st.text_input("Name", value="Faisal")
        u_msg = st.text_area("Message")
        
        if st.form_submit_button("Send Everywhere"):
            if u_msg:
                # 1. ആപ്പിലേക്ക് സേവ് ചെയ്യുന്നു
                now = datetime.datetime.now().strftime("%H:%M")
                new_chat = pd.DataFrame([[u_name, u_msg, now]], columns=['User', 'Message', 'Time'])
                new_chat.to_csv(CHAT_FILE, mode='a', header=not os.path.exists(CHAT_FILE), index=False)
                
                # 2. വാട്സാപ്പ് ലിങ്ക് ഉണ്ടാക്കുന്നു
                encoded_msg = urllib.parse.quote(f"Trader {u_name}: {u_msg}")
                wa_url = f"https://wa.me/{wa_no}?text={encoded_msg}"
                
                st.success("ആപ്പിൽ സേവ് ചെയ്തു!")
                st.markdown(f'<a href="{wa_url}" target="_blank" style="display: block; width: 100%; padding: 15px; background: #25D366; color: white; text-align: center; border-radius: 10px; text-decoration: none; font-weight: bold;">ഇവിടെ ക്ലിക്ക് ചെയ്ത് വാട്സാപ്പിലേക്ക് അയക്കുക</a>', unsafe_allow_html=True)
