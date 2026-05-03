import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import yfinance as yf
import random, re, urllib.parse, threading, base64, io, tempfile
import plotly.express as px
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh
from PIL import Image
import pytesseract
import cv2
import numpy as np

# ---------- 0. OCR Helper ----------
def extract_text_from_bill(image_file):
    try:
        image = Image.open(image_file)
        img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
        thresh = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        text = pytesseract.image_to_string(thresh, lang='eng')
        lines = text.split('\n')
        possible_amount = None
        for line in lines:
            match = re.search(r'[₹]?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', line)
            if match:
                possible_amount = match.group(1).replace(',', '')
                break
        return text, possible_amount
    except:
        return "", None

# ---------- 1. CONFIG & SETTINGS ----------
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"

# നിങ്ങളുടെ പുതിയ ഗൂഗിൾ സ്ക്രിപ്റ്റ് ലിങ്ക് ഇവിടെ കൃത്യമായി ചേർത്തിട്ടുണ്ട്
SCRIPT_API = "https://script.google.com/macros/s/AKfycbxECJKAJftU73C54rtnIUwj-HFPL8Ltjl77d1ry3Yms9pPjTYpkt-9uObNgDYH-npIy/exec"

WA_PHONE, WA_API_KEY = "+971551347989", "7463030"
IMGBB_API_KEY = "7b08945ff15a43258cc137387e6038d5" 

USERS = {"faisal": "faisal147", "shabana": "shabana123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI AI PRO v13.0", layout="wide")
st_autorefresh(interval=60000, key="auto_refresh")

# ---------- 2. STYLING ----------
def apply_style(colors):
    st.markdown(f"""<style>
        @keyframes grad {{ 0% {{background-position: 0% 50%;}} 50% {{background-position: 100% 50%;}} 100% {{background-position: 0% 50%;}} }}
        .stApp {{ background: linear-gradient(-45deg, {colors}); background-size: 400% 400%; animation: grad 15s ease infinite; color: white; }}
        [data-testid="stSidebar"] {{ background: rgba(0, 0, 0, 0.7) !important; backdrop-filter: blur(20px); border-right: 1px solid rgba(255, 215, 0, 0.1); }}
        .purple-box {{ background: rgba(0, 0, 0, 0.2); padding: 25px; border-radius: 20px; border: 1px solid rgba(255,215,0,0.3); backdrop-filter: blur(10px); text-align: center; margin-bottom: 20px; }}
        h1, h2, h3, p, label {{ color: white !important; font-weight: bold !important; }}
        .stButton>button {{ background: #FFD700; color: black; border-radius: 12px; font-weight: bold; width: 100%; height: 45px; }}
    </style>""", unsafe_allow_html=True)

# ---------- 3. UTILITIES ----------
def upload_bill(file):
    try:
        img_data = base64.b64encode(file.getvalue())
        res = requests.post("https://api.imgbb.com/1/upload", data={"key": IMGBB_API_KEY, "image": img_data})
        if res.json().get('success'):
            return res.json()['data']['url']
        return ""
    except:
        return ""

def send_wa(msg):
    try:
        requests.get(f"https://api.callmebot.com/whatsapp.php?phone={WA_PHONE}&text={urllib.parse.quote(msg)}&apikey={WA_API_KEY}", timeout=10)
    except:
        pass

def get_data():
    try:
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
        df.columns = df.columns.str.strip()
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'])
        return df
    except:
        return pd.DataFrame()

def add_to_sheet(item, amount, typ, source="App"):
    """Send entry to Google Apps Script Web App"""
    typ_param = "d" if typ.lower() == "debit" else "c"
    encoded_item = urllib.parse.quote(item)
    url = f"{SCRIPT_API}?item={encoded_item}&amount={amount}&type={typ_param}&user={source}"
    try:
        r = requests.get(url, timeout=10)
        return r.text
    except Exception as e:
        return f"Error: {e}"

# ---------- 4. LOGIN & AUTH ----------
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    apply_style("#0f0c29, #302b63, #24243e")
    st.markdown("<h1 style='text-align:center;'>🚀 PAICHI AI PRO v13.0</h1>", unsafe_allow_html=True)
    u = st.text_input("Username").lower()
    p = st.text_input("Password", type="password")
    if st.button("LOG IN") and USERS.get(u) == p:
        st.session_state.auth = True
        st.session_state.user = u
        st.rerun()
else:
    curr_user = st.session_state.user
    if curr_user == "shabana":
        menu = ["💰 Add Entry", "🤝 Debt Tracker"]
    else:
        menu = ["📊 Trading Advisor", "🏠 Dashboard", "💰 Add Entry", "📊 Report", "🔍 History", "🤝 Debt Tracker", "📥 Auto Import", "📈 Monthly Reports"]
    page = st.sidebar.radio("Menu", menu)
    
    apply_style({
        "📊 Trading Advisor":"#0f0c29, #302b63",
        "🏠 Dashboard":"#1a1a00, #4d4d00",
        "💰 Add Entry":"#41295a, #2f0743",
        "📊 Report":"#004d40, #002424",
        "🔍 History":"#1e3c72, #2a5298",
        "🤝 Debt Tracker":"#4b1212, #2d0b0b",
        "📥 Auto Import":"#2b2d42, #8d99ae",
        "📈 Monthly Reports":"#006d77, #83c5be"
    }.get(page, "#2D0844"))

    df_main = get_data()
    balance = 0
    if not df_main.empty:
        credit = pd.to_numeric(df_main['Credit'], errors='coerce').fillna(0).sum()
        debit = pd.to_numeric(df_main['Debit'], errors='coerce').fillna(0).sum()
        balance = credit - debit

    st.markdown(f'<div class="purple-box"><p style="opacity:0.8;">CURRENT AVAILABLE BALANCE</p><h1 style="color:#FFD700 !important; font-size:40px;">₹{balance:,.2f}</h1></div>', unsafe_allow_html=True)

    if page == "💰 Add Entry":
        st.title("New Entry & Bill 📸")
        v_raw = speech_to_text(language='ml', key='v_entry')
        with st.form("entry_fm", clear_on_submit=True):
            it = st.text_input("Item Name", value=v_raw if v_raw else "")
            cat = st.text_input("Category (Optional)")
            am_input = st.text_input("Amount")
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            bill = st.file_uploader("Upload Bill", type=['jpg','jpeg','png'])

            if st.form_submit_button("SAVE TRANSACTION"):
                if it and am_input:
                    try:
                        am = float(am_input)
                        link = upload_bill(bill) if bill else ""
                        display_name = f"{cat if cat else 'Others'}: {it}"
                        if link:
                            display_name += f" (Bill: {link})"
                        
                        result = add_to_sheet(display_name, am, ty, source=curr_user.capitalize())
                        if "Success" in result or "OK" in result:
                            st.success("Saved Successfully!")
                            st.rerun()
                        else:
                            st.error(f"Error: {result}")
                    except:
                        st.error("Check Amount!")

    elif page == "🤝 Debt Tracker":
        st.title("Debt Management 🤝")
        with st.form("debt_fm", clear_on_submit=True):
            n = st.text_input("Person Name")
            a_input = st.text_input("Amount")
            t = st.selectbox("Category", ["Borrowed (കടം വാങ്ങിയത്)", "Lent (കടം കൊടുത്തത്)"])
            if st.form_submit_button("SAVE DEBT"):
                if n and a_input:
                    try:
                        am = float(a_input)
                        typ = "Debit" if "Lent" in t else "Credit"
                        display_name = f"DEBT: {n} ({t})"
                        result = add_to_sheet(display_name, am, typ, source=curr_user.capitalize())
                        if "Success" in result or "OK" in result:
                            st.success("Debt Entry Saved!")
                            st.rerun()
                    except:
                        st.error("Check Amount!")

    elif page == "📊 Trading Advisor" and curr_user != "shabana":
        st.title("🛢️ Market Tracker")
        for name, sym in {"Crude Oil": "CL=F", "Nifty 50": "^NSEI"}.items():
            try:
                val = yf.Ticker(sym).history(period="1d")['Close'].iloc[-1]
                if "Crude" in name: val *= 83.5
                st.markdown(f'<div class="purple-box"><h3>{name}</h3><h1 style="color:#00FF00 !important;">₹{val:,.2f}</h1></div>', unsafe_allow_html=True)
            except: pass

    elif page == "🏠 Dashboard" and curr_user != "shabana":
        st.title("Dashboard")
        if not df_main.empty:
            st.dataframe(df_main.head(10))

    if st.sidebar.button("Logout"):
        st.session_state.auth = False
        st.rerun()
