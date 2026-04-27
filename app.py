import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import yfinance as yf
import random
import plotly.express as px
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh
import urllib.parse
import threading
import time

# ലോട്ടീ ആനിമേഷൻ ലൈബ്രറി ചെക്ക് ചെയ്യുന്നു
try:
    from streamlit_lottie import st_lottie
    LOTTIE_OK = True
except:
    LOTTIE_OK = False

# --- 1. CONFIG & SETTINGS ---
# നിന്റെ പഴയ ഗൂഗിൾ ഷീറ്റ് URL തന്നെയാണിത്
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"

WA_PHONE = "971551347989"
WA_API_KEY = "7463030"

st.set_page_config(page_title="PAICHI ULTIMATE v7.0", layout="wide")
st_autorefresh(interval=60000, key="auto_refresh")

# --- 2. 🎨 PREMIUM CSS ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(-45deg, #0f0c29, #302b63, #24243e, #000000);
        background-size: 400% 400%;
        animation: gradient 12s ease infinite;
    }
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    .premium-card {
        background: rgba(255, 255, 255, 0.07);
        backdrop-filter: blur(15px);
        border-radius: 20px;
        border: 1px solid rgba(255, 215, 0, 0.3);
        padding: 25px;
        text-align: center;
        margin-bottom: 20px;
    }
    .gold-text {
        background: linear-gradient(90deg, #FFD700, #FFA500);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900;
    }
    .stButton>button {
        background: linear-gradient(135deg, #FFD700 0%, #B8860B 100%);
        color: #000 !important; border-radius: 10px; font-weight: bold; width: 100%;
    }
    h1, h2, h3, p, label { color: white !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. HELPER ENGINES ---
def get_passwords_from_sheet():
    # ഗൂഗിൾ ഷീറ്റിൽ നിന്ന് പാസ്‌വേഡ് ലിസ്റ്റ് വായിക്കുന്നു
    # Default ആയി താഴെയുള്ള പാസ്‌വേഡുകൾ നൽകുന്നു
    creds = {"faisal": "faisal147", "shabana": "shabana123", "admin": "paichi786"}
    try:
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
        # ഷീറ്റിൽ 'Password_Update' എന്ന് തുടങ്ങുന്ന ഡിസ്ക്രിപ്ഷൻ ഉണ്ടോ എന്ന് നോക്കുന്നു
        updates = df[df['Description'].str.contains("Password_Update", na=False)]
        for index, row in updates.iterrows():
            # ഉദാഹരണത്തിന്: "Password_Update: shabana -> newpass123"
            parts = row['Description'].split("->")
            user_part = parts[0].split(":")[1].strip().lower()
            new_pass = parts[1].strip()
            creds[user_part] = new_pass
    except:
        pass
    return creds

def load_lottieurl(url):
    if not LOTTIE_OK: return None
    try:
        r = requests.get(url, timeout=5)
        return r.json() if r.status_code == 200 else None
    except: return None

lottie_panther = load_lottieurl("https://lottie.host/81f9537d-9447-4974-98c4-e86749963721/nQ8Yw2rS6r.json")

# --- 4. APP MAIN ---
if 'auth' not in st.session_state: st.session_state.auth = False

# ഷീറ്റിൽ നിന്ന് പാസ്‌വേഡ് എടുക്കുന്നു
current_users = get_passwords_from_sheet()

if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if LOTTIE_OK and lottie_panther: st_lottie(lottie_panther, height=250)
        st.markdown("<h2 style='text-align:center;'>PAICHI VAULT</h2>", unsafe_allow_html=True)
        u = st.text_input("Username").lower()
        p = st.text_input("Password", type="password")
        
        if st.button("UNLOCK"):
            if current_users.get(u) == p:
                st.session_state.auth, st.session_state.user = True, u
                st.rerun()
            else: st.error("Access Denied!")
else:
    with st.sidebar:
        st.markdown(f"### 🏦 FINANCE HUB")
        page = st.radio("MENU", ["💰 Add Entry", "📊 Trading AI", "📜 History", "🔐 Settings"])
        if st.button("Logout"):
            st.session_state.auth = False
            st.rerun()

    if page == "🔐 Settings":
        st.title("⚙️ Account Settings")
        st.subheader(f"Hi {st.session_state.user.capitalize()}, change your password here:")
        
        new_p = st.text_input("New Password", type="password")
        confirm_p = st.text_input("Confirm New Password", type="password")
        
        if st.button("Update Password Permanent"):
            if new_p == confirm_p and new_p != "":
                # ഗൂഗിൾ ഫോം വഴി ഷീറ്റിലേക്ക് പാസ്‌വേഡ് അപ്‌ഡേറ്റ് അയക്കുന്നു
                pass_desc = f"Password_Update: {st.session_state.user} -> {new_p}"
                requests.post(FORM_API, data={
                    "entry.1044099436": datetime.now().strftime("%Y-%m-%d"), 
                    "entry.2013476337": pass_desc, 
                    "entry.1460982454": 0, 
                    "entry.1221658767": 0
                })
                st.success(f"അടിപൊളി! പുതിയ പാസ്‌വേഡ് ഷീറ്റിൽ സേവ് ആയി. ഇനി എപ്പോൾ തുറന്നാലും '{new_p}' ഉപയോഗിക്കാം.")
                st.balloons()
            else:
                st.error("പാസ്‌വേഡുകൾ തമ്മിൽ ചേരുന്നില്ല!")

    # ബാക്കി ഭാഗങ്ങൾ (Add Entry, Trading AI, History) ഇതിൽ തുടർന്ന് വരും...
