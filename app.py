import streamlit as st
import requests
import numpy as np
import pandas as pd
import datetime
import os
import plotly.express as px
from sklearn.linear_model import LinearRegression
from streamlit_autorefresh import st_autorefresh
from googletrans import Translator # മലയാളം മാറ്റാൻ ഇത് വേണം

# 1. പേജ് സെറ്റിംഗ്സ് & തീം
st.set_page_config(page_title="Paichi AI Trader Pro", layout="wide")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #B38728, #AA771C); color: #000; }
    section[data-testid="stSidebar"] { background: linear-gradient(180deg, #A9A9A9, #C0C0C0, #808080) !important; }
    div[data-testid="stSidebar"] *, div[data-testid="stWidgetLabel"] p { color: #000 !important; font-weight: bold !important; }
    .main-title { color: #FFF; font-size: 38px; font-weight: 800; text-align: center; text-shadow: 2px 2px 4px #000; }
</style>
""", unsafe_allow_html=True)

st_autorefresh(interval=10000, key="faisal_mal_news_v1") # പത്ത് സെക്കൻഡിൽ പുതുക്കാം

FILE_NAME = 'trade_history_v2.csv'
translator = Translator()

# 2. ലൈവ് മലയാളം ന്യൂസ് ഫംഗ്ഷൻ
def get_live_news_malayalam():
    try:
        url = "https://query1.finance.yahoo.com/v1/finance/search?q=Nifty,Crude%20Oil&quotesCount=0&newsCount=5"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).json()
        news_list = [item['title'] for item in res['news']]
        full_news = " | ".join(news_list)
        
        # ഇംഗ്ലീഷ് വാർത്ത മലയാളത്തിലേക്ക് മാറ്റുന്നു
        translated = translator.translate(full_news, src='en', dest='ml')
        return translated.text
    except:
        return "മാർക്കറ്റ് വാർത്തകൾ അപ്‌ഡേറ്റ് ചെയ്യുന്നു... ദയവായി കാത്തിരിക്കുക!"

# 3. ഡാറ്റാ ഫംഗ്ഷനുകൾ
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
        close = [c for c in data['indicators']['quote'][0]['close'] if c is not None]
        ai_p = float(LinearRegression().fit(np.arange(5).reshape(-1, 1), np.array(close[-5:]).reshape(-1,1)).predict([[5]])[0][0]) if len(close)>5 else 0
        return {"p": p, "t": "BUY 🟢" if p > np.mean(close[-5:]) else "SELL 🔴", "ai": ai_p}
    except: return None

# --- മലയാളം ന്യൂസ് ടിക്കർ ---
news_mal = get_live_news_malayalam()
st.markdown(f"""
    <div style="background-color: #000; color: #BF953F; padding: 12px; font-weight: bold; border-bottom: 2px solid #BF953F; font-family: sans-serif;">
        <marquee scrollamount="5">📢 വാർത്തകൾ: {news_mal}</marquee>
    </div>
""", unsafe_allow_html=True)

# 4. സൈഡ് ബാർ
with st.sidebar:
    st.title("🚀 Paichi Trader")
    aed = st.number_input("AED Rate", value=1.0)
    st.success(f"₹ {aed * 22.75:.2f}")
    st.divider()
    cat = st.radio("MENU:", ["MARKET", "JOURNAL", "DASHBOARD"])

# 5. മെയിൻ കണ്ടന്റ്
st.markdown('<p class="main-title">🚀 Paichi AI Trader</p>', unsafe_allow_html=True)

if cat == "MARKET":
    sub_cat = st.selectbox("വിഭാഗം:", ["INDEX", "COMMODITY", "GOLD"])
    opts = {"INDEX": [("^NSEI", "NIFTY 50"), ("^NSEBANK", "BANK NIFTY")], 
            "COMMODITY": [("CL=F", "CRUDE OIL MCX", 93.5)], 
            "GOLD": [("GC=F", "GOLD 1G", 2.56)]}
    sel_name = st.selectbox("ഐറ്റം സെലക്ട് ചെയ്യുക:", [i[1] for i in opts[sub_cat]])
    sel_data = next(i for i in opts[sub_cat] if i[1] == sel_name)
    
    data = get_analysis(sel_data[0])
    if data:
        m = sel_data[2] if len(sel_data) > 2 else 1
        st.subheader(f"📍 {sel_data[1]}")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("ലൈവ് വില", f"₹{data['p']*m:.2f}")
        c2.markdown(f"<div style='background:{'#1B5E20' if 'BUY' in data['t'] else '#B71C1C'};padding:10px;border-radius:8px;color:#FFF;text-align:center;font-weight:bold;'>{data['t']}</div>", unsafe_allow_html=True)
        c3.metric("സ്റ്റാറ്റസ്", "Active")
        c4.metric("AI പ്രവചനം", f"₹{data['ai']*m:.2f}")

elif cat == "JOURNAL":
    st.subheader("📝 ട്രേഡിംഗ് ജേണൽ")
    with st.expander("പുതിയ ട്രേഡ് ചേർക്കുക"):
        col_a, col_b = st.columns(2)
        s = col_a.text_input("ഐറ്റം", value="Nifty")
        a = col_b.selectbox("Action", ["BUY", "SELL"])
        en = col_a.number_input("Entry Price", value=0.0)
        ex = col_b.number_input("Exit Price", value=0.0)
        q = col_a.number_input("Quantity", value=1, step=1)
        mood = col_b.selectbox("നിങ്ങളുടെ മൂഡ്", ["Calm", "Happy", "Fear", "Greedy"])
        pnl = (ex - en) * q
        if st.button("സേവ് ചെയ്യുക"):
            save_trade(s, a, en, ex, q, pnl, mood)
            st.success(f"സേവ് ചെയ്തു! ലാഭം/നഷ്ടം: ₹{pnl}")

    if os.path.isfile(FILE_NAME):
        df = pd.read_csv(FILE_NAME)
        st.dataframe(df, use_container_width=True)
        st.metric("ആകെ ലാഭം/നഷ്ടം", f"₹ {df['P&L'].sum():.2f}")
        
        if st.button("🗑️ അവസാനം ചേർത്തത് മാറ്റുക"):
            df[:-1].to_csv(FILE_NAME, index=False)
            st.rerun()

elif cat == "DASHBOARD":
    st.subheader("📊 പെർഫോമൻസ് ഡാഷ്ബോർഡ്")
    if os.path.isfile(FILE_NAME):
        df = pd.read_csv(FILE_NAME)
        st.plotly_chart(px.bar(df, x='Date', y='P&L', color='P&L', title="P&L ഗ്രാഫ്"), use_container_width=True)
        
        c1, c2 = st.columns(2)
        if 'Mood' in df.columns:
            c1.plotly_chart(px.pie(df, names='Mood', title="സൈക്കോളജി ചാർട്ട്"), use_container_width=True)
        c2.plotly_chart(px.pie(df, names='Item', values='P&L', title="ഐറ്റം തിരിച്ചുള്ള ലാഭം"), use_container_width=True)
    else:
        st.info("ഡാറ്റ ലഭ്യമല്ല.")
