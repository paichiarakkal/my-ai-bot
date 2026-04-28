import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import yfinance as yf
import random
import plotly.express as px
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh
import re
import urllib.parse
import threading

# --- 1. CONFIG ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"
WA_PHONE = "+971551347989"; WA_API_KEY = "7463030"
USERS = {"faisal": "faisal147", "shabana": "shabana123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI PREMIUM v5.1", layout="wide")
st_autorefresh(interval=300000, key="auto_refresh")

if 'auth' not in st.session_state: st.session_state.auth = False
if 'shopping_items' not in st.session_state: st.session_state.shopping_items = []

# --- 2. 📊 ENGINES ---
def get_gold_rate():
    try:
        gold = yf.Ticker("GC=F").history(period="1d")['Close'].iloc[-1]
        r24 = (gold / 31.1035) * 3.67 
        return round(r24, 2), round(r24 * 0.916, 2)
    except: return "N/A", "N/A"

def get_data():
    try:
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
        df.columns = df.columns.str.strip()
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df['Credit'] = pd.to_numeric(df['Credit'], errors='coerce').fillna(0)
        df['Debit'] = pd.to_numeric(df['Debit'], errors='coerce').fillna(0)
        return df
    except: return pd.DataFrame()

# --- 3. 🎨 DYNAMIC COLOR LOGIC ---
def set_page_style(color_gradient):
    st.markdown(f"""
        <style>
        .stApp {{ background: {color_gradient}; color: #fff; }}
        .gold-box {{ background: linear-gradient(90deg, #FFD700, #BF953F); color: black; padding: 10px; border-radius: 10px; text-align: center; font-weight: bold; margin-bottom: 10px; }}
        .balance-banner {{ background: rgba(255, 255, 255, 0.1); padding: 15px; border-radius: 15px; border: 1px solid rgba(255,255,255,0.2); margin-bottom: 25px; text-align: center; }}
        h1, h2, h3, p, label {{ color: white !important; font-weight: bold !important; }}
        </style>
        """, unsafe_allow_html=True)

# --- 4. APP LOGIC ---
if not st.session_state.auth:
    set_page_style("linear-gradient(135deg, #1A0521, #000000)")
    st.markdown("<h2 style='text-align:center;'>🔐 PAICHI LOGIN</h2>", unsafe_allow_html=True)
    u = st.text_input("Username").lower()
    p = st.text_input("Password", type="password")
    if st.button("LOGIN"):
        if USERS.get(u) == p:
            st.session_state.auth, st.session_state.user = True, u
            st.rerun()
        else: st.error("Access Denied!")
else:
    # Sidebar menu
    page = st.sidebar.radio("Menu", ["🏠 Dashboard", "🛒 Shopping List", "💰 Add Entry", "📊 Report", "🔍 History"])
    
    # ഓരോ പേജിനും നിറം നിശ്ചയിക്കുന്നു
    if page == "🏠 Dashboard": set_page_style("linear-gradient(135deg, #001F3F, #000000)") # Royal Blue
    elif page == "🛒 Shopping List": set_page_style("linear-gradient(135deg, #064E3B, #000000)") # Emerald Green
    elif page == "💰 Add Entry": set_page_style("linear-gradient(135deg, #4C1D95, #000000)") # Deep Purple
    elif page == "📊 Report": set_page_style("linear-gradient(135deg, #7F1D1D, #000000)") # Maroon
    elif page == "🔍 History": set_page_style("linear-gradient(135deg, #374151, #000000)") # Dark Grey

    df_all = get_data()
    g24, g22 = get_gold_rate()
    st.markdown(f"""<div class="gold-box">✨ Dubai Gold: 24K: AED {g24} | 22K: AED {g22}</div>""", unsafe_allow_html=True)
    
    total_bal = df_all['Credit'].sum() - df_all['Debit'].sum()
    st.markdown(f"""<div class="balance-banner">
        <span style="font-size:16px; color:#ddd;">TOTAL BALANCE</span><br>
        <span style="font-size:32px; color:#FFD700;">₹{total_bal:,.2f}</span>
    </div>""", unsafe_allow_html=True)

    # --- PAGE CONTENT ---
    if page == "🏠 Dashboard":
        st.title("Monthly Overview")
        if not df_all.empty:
            df_all['Month'] = df_all['Date'].dt.strftime('%B %Y')
            sel_month = st.selectbox("Select Month", df_all['Month'].unique().tolist()[::-1])
            m_df = df_all[df_all['Date'].dt.strftime('%B %Y') == sel_month]
            st.metric("Expense", f"₹{m_df['Debit'].sum():,.2f}")
            st.plotly_chart(px.bar(m_df, x='Date', y='Debit', template="plotly_dark"), use_container_width=True)

    elif page == "🛒 Shopping List":
        st.title("Shopping List 🛒")
        shop_voice = speech_to_text(language='ml', key='sv51')
        with st.form("shop_form", clear_on_submit=True):
            new_item = st.text_input("Add Item", value=shop_voice if shop_voice else "")
            if st.form_submit_button("ADD"):
                if new_item: st.session_state.shopping_items.append({"item": new_item, "done": False}); st.rerun()
        for idx, item in enumerate(st.session_state.shopping_items):
            if not item["done"]:
                if st.checkbox(item["item"], key=f"it_{idx}"):
                    st.session_state.shopping_items[idx]["done"] = True; st.rerun()
        if st.button("Clear Done Items"):
            st.session_state.shopping_items = [i for i in st.session_state.shopping_items if not i["done"]]; st.rerun()

    elif page == "💰 Add Entry":
        st.title("New Entry 📝")
        v_raw = speech_to_text(language='ml', key='ev51')
        with st.form("entry_form", clear_on_submit=True):
            it = st.text_input("Item", value=v_raw if v_raw else "")
            cat = st.selectbox("Category", ["Food", "Shop", "Fuel", "Rent", "Bills", "Others"])
            am = st.number_input("Amount", min_value=0.0)
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            if st.form_submit_button("SAVE"):
                if it and am > 0:
                    d, c = (am, 0) if ty == "Debit" else (0, am)
                    requests.post(FORM_API, data={"entry.1044099436": datetime.now().strftime("%Y-%m-%d"), "entry.2013476337": f"[{st.session_state.user.capitalize()}] {cat}: {it}", "entry.1460982454": d, "entry.1221658767": c})
                    st.success("Saved! ✅"); st.rerun()

    elif page == "📊 Report":
        st.title("Analysis")
        if not df_all.empty:
            df_all['Month'] = df_all['Date'].dt.strftime('%B %Y')
            sel = st.selectbox("Month", df_all['Month'].unique().tolist()[::-1])
            m_df = df_all[(df_all['Date'].dt.strftime('%B %Y') == sel) & (df_all['Debit'] > 0)]
            if not m_df.empty: st.plotly_chart(px.pie(m_df, values='Debit', names='Item', hole=0.4, template="plotly_dark"), use_container_width=True)

    elif page == "🔍 History":
        st.title("History")
        st.dataframe(df_all.sort_values(by='Date', ascending=False), use_container_width=True)

    if st.sidebar.button("Logout"): st.session_state.auth = False; st.rerun()
