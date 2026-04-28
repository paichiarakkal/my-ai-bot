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

st.set_page_config(page_title="PAICHI PREMIUM v5.2", layout="wide")
st_autorefresh(interval=300000, key="auto_refresh")

if 'auth' not in st.session_state: st.session_state.auth = False
if 'shopping_items' not in st.session_state: st.session_state.shopping_items = []

# --- 2. 🎨 DYNAMIC PREMIUM DESIGN ---
def apply_theme(bg_color, accent_color):
    st.markdown(f"""
        <style>
        .stApp {{ background: {bg_color}; color: #fff; transition: 0.5s; }}
        
        /* Sidebar Styling */
        [data-testid="stSidebar"] {{ background: rgba(0,0,0,0.9) !important; border-right: 2px solid {accent_color}; }}
        
        /* Navigation Buttons Custom Colors */
        div.row-widget.stRadio > div {{ background: rgba(255,255,255,0.05); padding: 10px; border-radius: 15px; }}
        
        /* Top Banner Style */
        .gold-box {{ background: linear-gradient(90deg, #FFD700, #BF953F); color: black; padding: 10px; border-radius: 10px; text-align: center; font-weight: bold; box-shadow: 0px 4px 15px rgba(255, 215, 0, 0.3); }}
        .balance-banner {{ background: rgba(255, 255, 255, 0.05); padding: 15px; border-radius: 20px; border: 2px solid {accent_color}; text-align: center; margin-bottom: 20px; }}
        
        h1, h2, h3, p, label {{ color: white !important; font-family: 'Segoe UI', sans-serif; }}
        .stButton>button {{ background: {accent_color}; color: black; border-radius: 12px; font-weight: bold; border: none; }}
        </style>
        """, unsafe_allow_html=True)

# --- 3. ENGINES ---
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

# --- 4. MAIN INTERFACE ---
if not st.session_state.auth:
    apply_theme("linear-gradient(135deg, #1A0521, #000000)", "#FFD700")
    st.markdown("<h2 style='text-align:center;'>🔐 PAICHI LOGIN</h2>", unsafe_allow_html=True)
    u = st.text_input("Username").lower()
    p = st.text_input("Password", type="password")
    if st.button("LOGIN"):
        if USERS.get(u) == p:
            st.session_state.auth, st.session_state.user = True, u
            st.rerun()
        else: st.error("Access Denied!")
else:
    # Sidebar Page Selection
    st.sidebar.markdown(f"<h2 style='color:#FFD700; text-align:center;'>PAICHI v5.2</h2>", unsafe_allow_html=True)
    page = st.sidebar.radio("NAVIGATE", ["🏠 Dashboard", "💰 Add Entry", "🛒 Shopping List", "📊 Report", "🔍 History"])

    # --- DYNAMIC COLOR SWITCHER ---
    # Dashboard -> Gold/Black
    if page == "🏠 Dashboard": apply_theme("linear-gradient(135deg, #1a1a00, #000000)", "#FFD700")
    # Add Entry -> Purple/Black
    elif page == "💰 Add Entry": apply_theme("linear-gradient(135deg, #2D0844, #000000)", "#E0B0FF")
    # Shopping List -> Rose/Pink/Black
    elif page == "🛒 Shopping List": apply_theme("linear-gradient(135deg, #4A0E0E, #000000)", "#FF69B4")
    # Report -> Silver/Grey/Black
    elif page == "📊 Report": apply_theme("linear-gradient(135deg, #2c2c2c, #000000)", "#C0C0C0")
    # History -> Deep Blue/Black
    elif page == "🔍 History": apply_theme("linear-gradient(135deg, #001F3F, #000000)", "#0074D9")

    df_all = get_data()
    g24, g22 = get_gold_rate()
    
    st.markdown(f"""<div class="gold-box">✨ DUBAI GOLD RATE: 24K: AED {g24} | 22K: AED {g22}</div>""", unsafe_allow_html=True)
    
    total_bal = df_all['Credit'].sum() - df_all['Debit'].sum()
    st.markdown(f"""<div class="balance-banner">
        <span style="font-size:14px; opacity:0.8;">CURRENT BALANCE</span><br>
        <span style="font-size:36px; font-weight:bold; color:#FFD700;">₹{total_bal:,.2f}</span>
    </div>""", unsafe_allow_html=True)

    # --- PAGE CONTENT ---
    if page == "🏠 Dashboard":
        st.title("Financial Summary")
        if not df_all.empty:
            df_all['Month'] = df_all['Date'].dt.strftime('%B %Y')
            sel = st.selectbox("Select Month", df_all['Month'].unique().tolist()[::-1])
            m_df = df_all[df_all['Date'].dt.strftime('%B %Y') == sel]
            st.metric("Total Monthly Expense", f"₹{m_df['Debit'].sum():,.2f}")
            st.plotly_chart(px.area(m_df, x='Date', y='Debit', template="plotly_dark", color_discrete_sequence=['#FFD700']), use_container_width=True)

    elif page == "💰 Add Entry":
        st.title("Quick Entry 📝")
        v_raw = speech_to_text(language='ml', key='v_entry')
        with st.form("entry_form", clear_on_submit=True):
            it = st.text_input("What did you spend on?", value=v_raw if v_raw else "")
            cat = st.selectbox("Category", ["Food", "Shop", "Fuel", "Bills", "Others"])
            am = st.number_input("Amount", min_value=0.0)
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            if st.form_submit_button("CONFIRM SAVE"):
                if it and am > 0:
                    d, c = (am, 0) if ty == "Debit" else (0, am)
                    requests.post(FORM_API, data={"entry.1044099436": datetime.now().strftime("%Y-%m-%d"), "entry.2013476337": f"[{st.session_state.user.capitalize()}] {cat}: {it}", "entry.1460982454": d, "entry.1221658767": c})
                    st.balloons()
                    st.success("Transaction recorded!")
                    st.rerun()

    elif page == "🛒 Shopping List":
        st.title("Home Shopping List 🛒")
        s_voice = speech_to_text(language='ml', key='v_shop')
        with st.form("shop_f", clear_on_submit=True):
            n_item = st.text_input("Add New Item", value=s_voice if s_voice else "")
            if st.form_submit_button("ADD"):
                if n_item: st.session_state.shopping_items.append({"item": n_item, "done": False}); st.rerun()
        
        for idx, item in enumerate(st.session_state.shopping_items):
            if not item["done"]:
                if st.checkbox(item["item"], key=f"shop_{idx}"):
                    st.session_state.shopping_items[idx]["done"] = True; st.rerun()
        if st.button("Clear Purchased Items"):
            st.session_state.shopping_items = [i for i in st.session_state.shopping_items if not i["done"]]; st.rerun()

    elif page == "📊 Report":
        st.title("Expense Analytics")
        if not df_all.empty:
            df_all['Month'] = df_all['Date'].dt.strftime('%B %Y')
            sel_m = st.selectbox("Filter by Month", df_all['Month'].unique().tolist()[::-1])
            m_df = df_all[(df_all['Date'].dt.strftime('%B %Y') == sel_m) & (df_all['Debit'] > 0)]
            if not m_df.empty:
                st.plotly_chart(px.pie(m_df, values='Debit', names='Item', hole=0.5, template="plotly_dark"), use_container_width=True)

    elif page == "🔍 History":
        st.title("Transaction Log")
        st.dataframe(df_all.sort_values(by='Date', ascending=False), use_container_width=True)

    if st.sidebar.button("Logout"): st.session_state.auth = False; st.rerun()
