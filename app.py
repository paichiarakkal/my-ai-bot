import streamlit as st
import requests
import numpy as np
import pandas as pd
import datetime
import os
import plotly.express as px
from sklearn.linear_model import LinearRegression
from streamlit_autorefresh import st_autorefresh
from mtranslate import translate # മലയാളം വാർത്തകൾക്ക് ഇത് ആവശ്യമാണ്

# 1. പേജ് സെറ്റിംഗ്സ് & തീം
st.set_page_config(page_title="Paichi AI Trader Pro", layout="wide")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #B38728, #AA771C); color: #000; }
    section[data-testid="stSidebar"] { background: linear-gradient(180deg, #A9A9A9, #C0C0C0, #808080) !important; }
    div[data-testid="stSidebar"] *, div[data-testid="stWidgetLabel"] p { color: #000 !important; font-weight: bold !important; }
    .main-title { color: #FFF; font-size: 38px; font-weight: 800; text-align: center; text-shadow: 2px 2px 4px #000; }
    /* Visual Alert Style */
    .target-hit { background-color: #1B5E20; color: white; padding: 20px; border-radius: 10px; text-align: center; font-size: 24px; font-weight: bold; margin-bottom: 20px; border: 5px solid #FFD700; animation: blinker 1s linear infinite; }
    @keyframes blinker { 50% { opacity: 0.5; } }
    .crude-box { background: #000; color: #BF953F; padding: 15px; border-radius: 10px; border-left: 5px solid #FFD700; }
</style>
""", unsafe_allow_html=True)

# 8 സെക്കൻഡിൽ ആപ്പ് പുതുക്കും
st_autorefresh(interval=8000, key="faisal_ultimate_v1")

FILE_NAME = 'trade_history_v2.csv'

# 2. ഫംഗ്ഷനുകൾ
def get_live_news_malayalam():
    try:
        url = "https://query1.finance.yahoo.com/v1/finance/search?q=Crude%20Oil,Nifty&quotesCount=0&newsCount=5"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).json()
        news_list = [item['title'] for item in res['news']]
        full_news = "  🔥  ".join(news_list)
        return translate(full_news, "ml", "en")
    except:
        return "മാർക്കറ്റ് വാർത്തകൾ അപ്‌ഡേറ്റ് ചെയ്യുന്നു..."

def save_trade(symbol, action, entry_p, exit_p, qty, pnl, mood):
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    df_new = pd.DataFrame([[date, symbol, action, entry_p, exit_p, qty, pnl, mood]], 
                          columns=['Date', 'Item', 'Type', 'Entry', 'Exit', 'Qty', 'P&L', 'Mood'])
    if not os.path.isfile(FILE_NAME): df_new.to_csv(FILE_NAME, index=False)
    else: df_new.to_csv(FILE_NAME, mode='a', header=False, index=False)

def get_analysis(symbol):
    try:
        res = requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1m&range=1d", headers={'User-Agent': 'Mozilla/5.0'}).json()
        data = res['chart']['result'][0]
        p = data['meta']['regularMarketPrice']
        prev_close = data['meta']['previousClose']
        change = ((p - prev_close) / prev_close) * 100
        close = [c for c in data['indicators']['quote'][0]['close'] if c is not None]
        ai_p = float(LinearRegression().fit(np.arange(5).reshape(-1, 1), np.array(close[-5:]).reshape(-1,1)).predict([[5]])[0][0]) if len(close)>5 else p
        return {"p": p, "c": change, "t": "BUY 🟢" if p > np.mean(close[-5:]) else "SELL 🔴", "ai": ai_p}
    except: return None

# --- മലയാളം ന്യൂസ് ടിക്കർ ---
news_mal = get_live_news_malayalam()
st.markdown(f"""
    <div style="background-color: #000; color: #BF953F; padding: 12px; font-weight: bold; border-bottom: 2px solid #BF953F;">
        <marquee scrollamount="5">📢 വാർത്തകൾ: {news_mal}</marquee>
    </div>
""", unsafe_allow_html=True)

# 4. സൈഡ് ബാർ
with st.sidebar:
    st.title("🚀 Paichi Trader Pro")
    aed = st.number_input("AED Rate", value=1.0)
    st.success(f"₹ {aed * 22.75:.2f}")
    st.divider()
    cat = st.radio("MENU:", ["CRUDE FOCUS", "MARKET", "JOURNAL", "DASHBOARD"])
    st.divider()
    st.subheader("🎯 Profit Alert")
    target_p = st.number_input("Target Price (₹)", value=0.0)
    st.write("📅 US Inventory: Every Wednesday 8:00 PM")

# 5. മെയിൻ കണ്ടന്റ്
st.markdown('<p class="main-title">🚀 Paichi AI Trader</p>', unsafe_allow_html=True)

# --- വിഷ്വൽ അലേർട്ട് ലോജിക് ---
def check_alert(current_price, target):
    if target > 0 and current_price >= target:
        st.markdown(f'<div class="target-hit">🎉 ടാർഗെറ്റ് എത്തി! വില: ₹{current_price:.2f} <br> പ്രോഫിറ്റ് ബുക്ക് ചെയ്യാം! 💰</div>', unsafe_allow_html=True)
        st.balloons()

if cat == "CRUDE FOCUS":
    st.subheader("🛢️ Crude Oil Special Tracker")
    data = get_data = get_analysis("CL=F")
    if data:
        live_p = data['p'] * 93.5 # MCX ഏകദേശ നിരക്ക്
        check_alert(live_p, target_p)
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown(f"""<div class="crude-box">
                <h3>📍 CRUDE OIL MCX</h3>
                <h1 style="font-size: 50px;">₹{live_p:.2f}</h1>
                <p style="color: {'#00FF00' if data['c'] > 0 else '#FF0000'};">Change: {data['c']:.2f}%</p>
            </div>""", unsafe_allow_html=True)
        with col2:
            st.metric("AI Prediction", f"₹{data['ai']*93.5:.2f}")
            st.info("Trend: " + data['t'])

elif cat == "MARKET":
    sub_cat = st.selectbox("Category:", ["INDEX", "GOLD"])
    opts = {"INDEX": [("^NSEI", "NIFTY 50"), ("^NSEBANK", "BANK NIFTY")], 
            "GOLD": [("GC=F", "GOLD 1G", 2.56)]}
    sel_name = st.selectbox("Select Item:", [i[1] for i in opts[sub_cat]])
    sel_data = next(i for i in opts[sub_cat] if i[1] == sel_name)
    
    data = get_analysis(sel_data[0])
    if data:
        m = sel_data[2] if len(sel_data) > 2 else 1
        live_price = data['p'] * m
        check_alert(live_price, target_p)
        
        st.subheader(f"📍 {sel_data[1]}")
        c1, c2, c3 = st.columns(3)
        c1.metric("Live Price", f"₹{live_price:.2f}")
        c2.markdown(f"<div style='background:{'#1B5E20' if 'BUY' in data['t'] else '#B71C1C'};padding:10px;border-radius:8px;color:#FFF;text-align:center;font-weight:bold;'>{data['t']}</div>", unsafe_allow_html=True)
        c3.metric("AI Predict", f"₹{data['ai']*m:.2f}")

elif cat == "JOURNAL":
    st.subheader("📝 Trading Journal")
    with st.expander("Add New Trade"):
        col_a, col_b = st.columns(2)
        s = col_a.text_input("Item Name", value="Crude Oil")
        a = col_b.selectbox("Action", ["BUY", "SELL"])
        en = col_a.number_input("Entry Price", value=0.0)
        ex = col_b.number_input("Exit Price", value=0.0)
        q = col_a.number_input("Quantity", value=1, step=1)
        mood = col_b.selectbox("Mood", ["Calm", "Happy", "Fear", "Greedy"])
        pnl = (ex - en) * q
        if st.button("Save Trade"):
            save_trade(s, a, en, ex, q, pnl, mood)
            st.success(f"Saved! Profit: ₹{pnl}")

    if os.path.isfile(FILE_NAME):
        df = pd.read_csv(FILE_NAME)
        st.dataframe(df, use_container_width=True)
        st.metric("Total P&L", f"₹ {df['P&L'].sum():.2f}")

elif cat == "DASHBOARD":
    st.subheader("📊 Performance & AI Coach")
    if os.path.isfile(FILE_NAME):
        df = pd.read_csv(FILE_NAME)
        st.plotly_chart(px.bar(df, x='Date', y='P&L', color='P&L', title="P&L Trend"), use_container_width=True)
        
        st.divider()
        st.subheader("🤖 AI Trading Coach")
        if 'Mood' in df.columns:
            m = df['Mood'].mode()[0]
            if m == "Fear": st.warning("⚠️ ഫൈസൽ, പേടി ഒഴിവാക്കി സ്ട്രാറ്റജിയിൽ ഉറച്ചു നിൽക്കൂ!")
            elif m == "Greedy": st.error("🛑 അമിത ലാഭത്തിന് ശ്രമിക്കരുത്, കൃത്യസമയത്ത് ബുക്ക് ചെയ്യുക.")
            elif m == "Happy": st.success("✅ മികച്ച ഡിസിപ്ലിൻ! ഇതേ രീതി തുടരുക.")
        
        c1, c2 = st.columns(2)
        c1.plotly_chart(px.pie(df, names='Mood', title="Psychology Chart"), use_container_width=True)
        c2.plotly_chart(px.pie(df, names='Item', values='P&L', title="Profit by Item"), use_container_width=True)
