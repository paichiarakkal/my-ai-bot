import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import yfinance as yf
import random
import plotly.express as px
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh
from fpdf import FPDF
import io
import re
import urllib.parse
import threading

# --- 1. CONFIG & SETTINGS ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"
WA_PHONE = "+971551347989" 
WA_API_KEY = "7463030"
USERS = {"faisal": "faisal147", "shabana": "shabana123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI AI ANIMATED v5.3", layout="wide")
st_autorefresh(interval=60000, key="auto_refresh")

if 'auth' not in st.session_state: st.session_state.auth = False

# --- 2. 🎨 AI DYNAMIC ANIMATION ENGINE ---
def apply_ai_animation(color_set):
    st.markdown(f"""
        <style>
        /* Smooth Background Animation */
        @keyframes gradientAnimation {{
            0% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
            100% {{ background-position: 0% 50%; }}
        }}
        .stApp {{
            background: linear-gradient(-45deg, {color_set});
            background-size: 400% 400%;
            animation: gradientAnimation 12s ease infinite;
            color: #fff;
            transition: all 0.8s ease-in-out;
        }}
        [data-testid="stSidebar"] {{ background: rgba(0,0,0,0.85) !important; }}
        .balance-banner {{ 
            background: rgba(255, 255, 255, 0.1); 
            backdrop-filter: blur(10px);
            padding: 20px; 
            border-radius: 20px; 
            border: 1px solid rgba(255,215,0,0.4); 
            text-align: center; 
            margin-bottom: 25px; 
        }}
        .purple-box {{ 
            background: rgba(0, 0, 0, 0.25); 
            padding: 20px; 
            border-radius: 25px; 
            border: 1px solid rgba(255,255,255,0.1); 
            text-align: center; 
            margin-bottom: 20px; 
            backdrop-filter: blur(12px); 
        }}
        h1, h2, h3, p, label {{ color: white !important; font-weight: bold !important; }}
        .stButton>button {{ 
            background-color: #FFD700; 
            color: black; 
            border-radius: 12px; 
            font-weight: bold; 
            border: none;
            transition: 0.3s;
        }}
        .stButton>button:hover {{ transform: scale(1.02); background-color: #fff; }}
        </style>
        """, unsafe_allow_html=True)

# --- 3. 📊 ENGINES ---
def send_wa(msg):
    url = f"https://api.callmebot.com/whatsapp.php?phone={WA_PHONE}&text={urllib.parse.quote(msg)}&apikey={WA_API_KEY}"
    try: requests.get(url, timeout=10)
    except: pass

def get_total_balance():
    try:
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
        df.columns = df.columns.str.strip()
        ti = pd.to_numeric(df['Credit'], errors='coerce').fillna(0).sum()
        te = pd.to_numeric(df['Debit'], errors='coerce').fillna(0).sum()
        return ti - te
    except: return 0.0

def process_voice(text):
    if not text: return "", None, ""
    raw = text.lower()
    nums = re.findall(r'\d+', raw)
    amt = float(nums[0]) if nums else None
    desc = re.sub(r'\d+', '', raw).strip()
    cat = "Food" if any(x in raw for x in ["food", "ഭക്ഷണം"]) else "Shop" if any(x in raw for x in ["shop", "കട"]) else "Others"
    return cat, amt, desc

def get_triple_advisor():
    try:
        symbols = {"Nifty 50": "^NSEI", "Bank Nifty": "^NSEBANK", "Crude Fut": "CL=F"}
        results = []
        for name, sym in symbols.items():
            df = yf.Ticker(sym).history(period="2d", interval="5m")
            if df.empty: continue
            last_p = df['Close'].iloc[-1]
            h, l, c = df['High'].iloc[-2], df['Low'].iloc[-2], df['Close'].iloc[-2]
            pivot = (h + l + c) / 3
            if last_p > pivot: signal, color = "🚀 BUY", "#00FF00"
            else: signal, color = "📉 SELL", "#FF3131"
            if name == "Crude Fut": last_p = last_p * 83.5 * 1.15
            results.append({"name": name, "price": last_p, "signal": signal, "color": color})
        return results
    except: return None

# --- 4. APP LOGIC ---
if not st.session_state.auth:
    # Login Page Animation (Deep Dark)
    apply_ai_animation("#0f0c29, #302b63, #24243e")
    st.markdown("<h1 style='text-align:center;'>🔐 PAICHI AI</h1>", unsafe_allow_html=True)
    with st.container():
        u = st.text_input("Username").lower()
        p = st.text_input("Password", type="password")
        if st.button("LOGIN"):
            if USERS.get(u) == p:
                st.session_state.auth, st.session_state.user = True, u
                st.rerun()
            else: st.error("Access Denied!")
else:
    curr_user = st.session_state.user
    
    # Sidebar Navigation
    if curr_user == "shabana":
        page = st.sidebar.radio("Menu", ["💰 Add Entry", "🤝 Debt Tracker"])
    else:
        page = st.sidebar.radio("Menu", ["📊 Advisor", "🏠 Dashboard", "💰 Add Entry", "📊 Report", "🔍 History", "🤝 Debt Tracker"])

    # --- PAGE WISE ANIMATED COLORS ---
    if page == "📊 Advisor": apply_ai_animation("#0f0c29, #302b63, #24243e") # Space Blue
    elif page == "🏠 Dashboard": apply_ai_animation("#1a1a00, #4D4D00, #000000") # Dark Gold
    elif page == "💰 Add Entry": apply_ai_animation("#41295a, #2F0743, #000000") # Royal Purple
    elif page == "📊 Report": apply_ai_animation("#004d40, #002424, #000000") # Forest Teal
    elif page == "🔍 History": apply_ai_animation("#1e3c72, #2a5298, #000000") # Ocean Blue
    elif page == "🤝 Debt Tracker": apply_ai_animation("#4b1212, #2d0b0b, #000000") # Midnight Red

    balance = get_total_balance()
    st.markdown(f"""<div class="balance-banner">
        <span style="font-size:14px; opacity:0.8;">CURRENT AVAILABLE BALANCE</span><br>
        <span style="font-size:36px; color:#FFD700; font-weight:900;">₹{balance:,.2f}</span>
    </div>""", unsafe_allow_html=True)

    if st.sidebar.button("Logout"):
        st.session_state.auth = False; st.rerun()

    # --- PAGES ---
    if page == "📊 Advisor":
        st.title("Smart Advisor")
        markets = get_triple_advisor()
        if markets:
            for m in markets:
                st.markdown(f"""<div class="purple-box" style="border-top: 4px solid {m['color']};">
                    <h3 style="color:#E0B0FF !important;">{m["name"]}</h3>
                    <h1 style="color:{m["color"]} !important; font-size:45px;">{m["signal"]}</h1>
                    <h2 style="color:#FFD700 !important;">₹{m["price"]:,.0f}</h2>
                </div>""", unsafe_allow_html=True)

    elif page == "🏠 Dashboard":
        st.title("Financial Overview")
        try:
            df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
            st.plotly_chart(px.bar(df.tail(10), x=df.columns[0], y='Debit', template="plotly_dark", color_discrete_sequence=['#FFD700']), use_container_width=True)
        except: st.error("Data error")

    elif page == "💰 Add Entry":
        st.title("New Entry 🎙️")
        v_raw = speech_to_text(language='ml', key='v_new')
        cat_v, amt_v, desc_v = process_voice(v_raw)
        with st.form("entry_form", clear_on_submit=True):
            it = st.text_input("Item", value=desc_v)
            am = st.text_input("Amount", value=str(int(amt_v)) if amt_v else "")
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            if st.form_submit_button("SAVE"):
                if it and am:
                    requests.post(FORM_API, data={"entry.1044099436": datetime.now().strftime("%Y-%m-%d"), "entry.2013476337": f"[{curr_user.capitalize()}] {it}", "entry.1460982454": am if ty=="Debit" else 0, "entry.1221658767": am if ty=="Credit" else 0})
                    threading.Thread(target=send_wa, args=(f"✅ *Entry Saved*\n💰 ₹{am} - {it}",)).start()
                    st.success("Saved! ✅"); st.rerun()

    elif page == "📊 Report":
        st.title("Analysis")
        try:
            df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
            st.plotly_chart(px.pie(df[df['Debit']>0], values='Debit', names='Item', hole=0.4, template="plotly_dark"), use_container_width=True)
        except: st.write("No report data")

    elif page == "🔍 History":
        st.title("History")
        try:
            df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
            st.dataframe(df.iloc[::-1], use_container_width=True)
        except: st.write("Empty history")

    elif page == "🤝 Debt Tracker":
        st.title("Debt Tracker")
        st.info("Debt records are updated in the main ledger.")
        # Debt form logic goes here
