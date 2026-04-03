import streamlit as st
import requests
import numpy as np
import pandas as pd
import datetime
import os
from sklearn.linear_model import LinearRegression
from streamlit_autorefresh import st_autorefresh

# 1. പേജ് സെറ്റിംഗ്സ് & തീം
st.set_page_config(page_title="Paichi AI Trader Pro", layout="wide")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #B38728, #AA771C); color: #000; }
    section[data-testid="stSidebar"] { background: linear-gradient(180deg, #A9A9A9, #C0C0C0, #808080) !important; }
    div[data-testid="stSidebar"] *, div[data-testid="stWidgetLabel"] p { color: #000 !important; font-weight: bold !important; }
    .main-title { color: #FFF; font-size: 38px; font-weight: 800; text-align: center; text-shadow: 2px 2px 4px #000; }
    div[data-testid="stMetricValue"] > div { color: #FFF !important; font-weight: 800; }
</style>
""", unsafe_allow_html=True)

st_autorefresh(interval=2000, key="faisal_v5_refresh")

# 2. സേവിംഗ് ഫംഗ്ഷൻ
def save_trade(symbol, action, entry_p, exit_p, qty, pnl):
    file = 'trade_history_v2.csv'
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    df_new = pd.DataFrame([[date, symbol, action, entry_p, exit_p, qty, pnl]], 
                          columns=['Date', 'Item', 'Type', 'Entry', 'Exit', 'Qty', 'P&L'])
    if not os.path.isfile(file): 
        df_new.to_csv(file, index=False)
    else: 
        df_new.to_csv(file, mode='a', header=False, index=False)

def get_analysis(symbol):
    try:
        res = requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1m&range=1d", headers={'User-Agent': 'Mozilla/5.0'}).json()
        data = res['chart']['result'][0]
        p = data['meta']['regularMarketPrice']
        close = [c for c in data['indicators']['quote'][0]['close'] if c is not None]
        ai_p = float(LinearRegression().fit(np.arange(5).reshape(-1, 1), np.array(close[-5:]).reshape(-1,1)).predict([[5]])[0][0]) if len(close)>5 else 0
        return {"p": p, "t": "BUY 🟢" if p > np.mean(close[-5:]) else "SELL 🔴", "ai": ai_p}
    except: return None

# 3. സിൽവർ സൈഡ് ബാർ
with st.sidebar:
    st.title("🚀 Paichi Trader")
    aed = st.number_input("AED Rate", value=1.0)
    st.success(f"₹ {aed * 22.75:.2f}")
    st.divider()
    cat = st.radio("MENU:", ["MARKET", "JOURNAL & HISTORY"])
    
    if cat == "MARKET":
        sub_cat = st.selectbox("Category:", ["INDEX", "COMMODITY", "GOLD"])
        opts = {"INDEX": [("^NSEI", "NIFTY 50"), ("^NSEBANK", "BANK NIFTY")], "COMMODITY": [("CL=F", "CRUDE OIL MCX", 93.5)], "GOLD": [("GC=F", "GOLD 1G", 2.56)]}
        sel_name = st.selectbox("Select Item:", [i[1] for i in opts[sub_cat]])
        sel_data = next(i for i in opts[sub_cat] if i[1] == sel_name)

# 4. മെയിൻ പേജ് ലോജിക്
st.markdown('<p class="main-title">🚀 Paichi AI Trader</p>', unsafe_allow_html=True)

if cat == "MARKET":
    data = get_analysis(sel_data[0])
    if data:
        m = sel_data[2] if len(sel_data) > 2 else 1
        st.subheader(f"📍 {sel_data[1]}")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Live Price", f"₹{data['p']*m:.2f}")
        c2.markdown(f"<div style='background:{'#1B5E20' if 'BUY' in data['t'] else '#B71C1C'};padding:10px;border-radius:8px;color:#FFF;text-align:center;font-weight:bold;'>{data['t']}</div>", unsafe_allow_html=True)
        c3.metric("Status", "Active")
        c4.metric("AI Predict", f"₹{data['ai']*m:.2f}", delta=f"{(data['ai']-data['p'])*m:.2f}")

elif cat == "JOURNAL & HISTORY":
    st.subheader("📝 Trading Journal & History")
    with st.expander("Add New Trade"):
        col_a, col_b = st.columns(2)
        s = col_a.text_input("Stock/Index Name", value="Nifty")
        a = col_b.selectbox("Action", ["BUY", "SELL"])
        
        entry_p = col_a.number_input("Entry Price", value=0.0)
        exit_p = col_b.number_input("Exit Price", value=0.0)
        qty = st.number_input("Quantity", value=1, step=1)
        
        # ലളിതമായ ലാഭക്കണക്ക്: Exit - Entry
        pnl = (exit_p - entry_p) * qty
            
        if st.button("Save to History"):
            save_trade(s, a, entry_p, exit_p, qty, pnl)
            st.success(f"Saved! Result: ₹{pnl:.2f}")
    
    if os.path.isfile('trade_history_v2.csv'):
        df = pd.read_csv('trade_history_v2.csv')
        st.dataframe(df, use_container_width=True)
        st.metric("Total Net P&L", f"₹ {df['P&L'].sum():.2f}")
