import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
import plotly.express as px
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh
from fpdf import FPDF
import re
import urllib.parse
import threading
from streamlit_calendar import calendar

# --- CONFIG & SETTINGS ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"
WA_PHONE, WA_API_KEY = "971551347989", "7463030"
USERS = {"faisal": "faisal147", "shabana": "shabana123", "admin": "paichi786"}

# --- STREAMLIT UI & THEME ---
st.set_page_config(page_title="PAICHI EXPENSES v2.7", layout="wide")
st_autorefresh(interval=60000, key="auto_refresh")

st.markdown("""<style>
    .stApp { background: linear-gradient(135deg, #1A0521, #310062, #0D0214); color: #fff; }
    [data-testid="stSidebar"] { background: rgba(0,0,0,0.9) !important; }
    .stButton>button { background-color: #FFD700; color: #000; border-radius: 10px; font-weight: bold; width: 100%; transition: 0.3s; }
    .stButton>button:hover { background-color: #FFF; color: #000; box-shadow: 0px 0px 10px #FFD700; }
    .balance-banner { background: rgba(255, 255, 255, 0.07); padding: 25px; border-radius: 15px; border-left: 10px solid #FFD700; margin-bottom: 25px; text-align: center; box-shadow: 0px 4px 15px rgba(0,0,0,0.3); }
    .purple-box { background: rgba(255, 255, 255, 0.05); padding: 20px; border-radius: 25px; border: 2px solid rgba(255, 215, 0, 0.3); text-align: center; margin-bottom: 20px; }
    .category-box { background: rgba(255, 255, 255, 0.08); padding: 15px; border-radius: 15px; text-align: center; border-bottom: 4px solid #FFD700; margin-bottom: 15px; }
    .alert-banner { background-color: #ff4d4d; color: white; padding: 10px; border-radius: 10px; text-align: center; font-weight: bold; margin-bottom: 20px; }
    h1, h2, h3, p, label { color: white !important; font-weight: bold !important; }
    .stDataFrame { background: white; border-radius: 10px; color: black; }
</style>""", unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth, st.session_state.user = False, ""

# --- DYNAMIC APP SETTINGS (ആപ്പിൽ നിന്ന് തത്സമയം മാറ്റാൻ) ---
if 'custom_alert_text' not in st.session_state: 
    st.session_state.custom_alert_text = "rent 9000, kuri 12500, expenses 7500"
if 'low_limit' not in st.session_state: 
    st.session_state.low_limit = 5000

# --- HELPER FUNCTIONS ---
def send_whatsapp_auto(msg):
    threading.Thread(target=lambda: requests.get(f"https://api.callmebot.com/whatsapp.php?phone={WA_PHONE}&text={urllib.parse.quote(msg)}&apikey={WA_API_KEY}", timeout=10)).start()

def parse_mixed_dates(date_series):
    parsed = []
    for val in date_series:
        dt = pd.to_datetime(str(val).strip(), errors='coerce')
        if not pd.isna(dt) and dt.year == 2026 and dt.month < 4: dt = datetime(2026, dt.day, dt.month)
        if pd.isna(dt): dt = pd.to_datetime(str(val).strip(), dayfirst=True, errors='coerce')
        parsed.append(dt)
    return pd.Series(parsed)

@st.cache_data(ttl=10)
def load_data():
    try:
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
        df.columns = df.columns.str.strip()
        df['Date'] = parse_mixed_dates(df['Date'])
        df['Debit'] = pd.to_numeric(df['Debit'], errors='coerce').fillna(0)
        df['Credit'] = pd.to_numeric(df['Credit'], errors='coerce').fillna(0)
        return df
    except: return pd.DataFrame()

# --- AUTH LOGIN ---
if not st.session_state.auth:
    st.title("🔐 PAICHI EXPENSES LOGIN")
    u, p = st.text_input("Username").lower(), st.text_input("Password", type="password")
    if st.button("LOGIN") and USERS.get(u) == p:
        st.session_state.auth, st.session_state.user = True, u
        st.rerun()
    elif p: st.error("Access Denied!")
else:
    df = load_data()
    t_in, t_out = (df['Credit'].sum(), df['Debit'].sum()) if not df.empty else (0.0, 0.0)
    bal = t_in - t_out
    
    # ⚙️ SIDEBAR SETTINGS (ആപ്പിൽ നിന്ന് സ്വന്തമായി അടിച്ചു നൽകാൻ)
    with st.sidebar.expander("⚙️ Alert & Expense Settings"):
        st.session_state.custom_alert_text = st.text_area("Custom Alert Message (നിങ്ങൾക്ക് ഇഷ്ടമുള്ളത് ടൈപ്പ് ചെയ്യുക)", value=st.session_state.custom_alert_text)
        st.session_state.low_limit = st.number_input("Low Balance Limit (₹)", value=st.session_state.low_limit)
    
    # ⚠️ അലേർട്ട് സിസ്റ്റം (നിങ്ങൾ ടൈപ്പ് ചെയ്യുന്ന സന്ദേശം കാണിക്കും)
    if bal < st.session_state.low_limit:
        st.markdown(f'<div class="alert-banner">⚠️ ശ്രദ്ധിക്കുക: അക്കൗണ്ട് ബാലൻസ് കുറവാണ് {st.session_state.custom_alert_text} (₹{bal:,.2f})! അത്യാവശ്യ കാര്യങ്ങൾക്കായി ഫണ്ട് സൂക്ഷിക്കുക.</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="balance-banner"><span style="font-size:20px; color:#E0B0FF;">Available Balance</span><br><span style="font-size:40px; color:#FFD700; font-weight:bold;">₹{bal:,.2f}</span></div>', unsafe_allow_html=True)
    
    menu = ["💰 Add Entry", "📅 Calendar", "📊 Report", "🔍 History", "🤝 Debt Tracker"]
    if st.session_state.user != "shabana": menu.insert(0, "🏠 Dashboard")
    page = st.sidebar.radio("Menu", menu)
    if st.sidebar.button("Logout"): st.session_state.auth = False; st.rerun()

    # --- DASHBOARD ---
    if page == "🏠 Dashboard" and not df.empty:
        st.title("Financial Overview")
        st.markdown(f'<div class="purple-box"><h2 style="color:#00FF00;">Total Credit: ₹{t_in:,.2f}</h2><h2 style="color:#FF3131;">Total Debit: ₹{t_out:,.2f}</h2></div>', unsafe_allow_html=True)
