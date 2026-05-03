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
# ബാലൻസ് കാണിക്കാൻ ഈ CSV_URL പ്രധാനമാണ്
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"

# നിങ്ങളുടെ പുതിയ ഗൂഗിൾ സ്ക്രിപ്റ്റ് ലിങ്ക്
SCRIPT_API = "https://script.google.com/macros/s/AKfycbzaMZqBexe6UBDvpMagsXe8AcqigTIV_gQMR80tAckp0ZxQtTLEqaB3Rjq1qzl1y8Me/exec"

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
def get_data():
    try:
        # ഷീറ്റിൽ നിന്ന് ഫ്രഷ് ഡാറ്റ എടുക്കാൻ random ഉപയോഗിക്കുന്നു
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
        df.columns = df.columns.str.strip()
        # Credit, Debit കോളങ്ങൾ നമ്പറുകളാണെന്ന് ഉറപ്പുവരുത്തുന്നു
        df['Credit'] = pd.to_numeric(df['Credit'], errors='coerce').fillna(0)
        df['Debit'] = pd.to_numeric(df['Debit'], errors='coerce').fillna(0)
        return df
    except:
        return pd.DataFrame()

def add_to_sheet(item, amount, typ, source="App"):
    # ഗൂഗിൾ സ്ക്രിപ്റ്റിലേക്ക് ഡാറ്റ അയക്കുന്നു
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
    # മെനു സെറ്റിംഗ്സ്
    if curr_user == "shabana":
        menu = ["💰 Add Entry", "🤝 Debt Tracker"]
    else:
        menu = ["📊 Trading Advisor", "🏠 Dashboard", "💰 Add Entry", "📊 Report", "🔍 History", "🤝 Debt Tracker"]
    
    page = st.sidebar.radio("Menu", menu)
    apply_style("#2D0844") # ഡിഫോൾട്ട് സ്റ്റൈൽ

    # --- ബാലൻസ് കണക്കാക്കുന്ന ഭാഗം ---
    df_main = get_data()
    balance = 0
    if not df_main.empty:
        total_credit = df_main['Credit'].sum()
        total_debit = df_main['Debit'].sum()
        balance = total_credit - total_debit

    # ബാലൻസ് ബോക്സ്
    st.markdown(f'<div class="purple-box"><p style="opacity:0.8;">CURRENT AVAILABLE BALANCE</p><h1 style="color:#FFD700 !important; font-size:40px;">₹{balance:,.2f}</h1></div>', unsafe_allow_html=True)

    if page == "💰 Add Entry":
        st.title("New Entry & Bill 📸")
        v_raw = speech_to_text(language='ml', key='v_entry')
        with st.form("entry_fm", clear_on_submit=True):
            it = st.text_input("Item Name", value=v_raw if v_raw else "")
            am_input = st.text_input("Amount")
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            if st.form_submit_button("SAVE TRANSACTION"):
                if it and am_input:
                    try:
                        result = add_to_sheet(it, float(am_input), ty, source=curr_user.capitalize())
                        st.success("Entry Saved!")
                        st.rerun()
                    except:
                        st.error("Check Amount!")

    elif page == "🔍 History":
        st.title("History")
        if not df_main.empty:
            st.dataframe(df_main.iloc[::-1], use_container_width=True)

    if st.sidebar.button("Logout"):
        st.session_state.auth = False
        st.rerun()
