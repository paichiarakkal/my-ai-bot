import streamlit as st
import pandas as pd
import requests
import yfinance as yf
import random
import urllib.parse, threading, base64
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh

# --- 1. CONFIG & API SETTINGS ---
# ഷീറ്റിലെ ഡാറ്റ വായിക്കാനുള്ള ലിങ്ക്
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"

# ഫൈസൽ ഇപ്പോൾ ഉണ്ടാക്കിയ പുതിയ ഗൂഗിൾ സ്ക്രിപ്റ്റ് ലിങ്ക്
SCRIPT_API = "https://script.google.com/macros/s/AKfycbyPn_VApxjEsBcVv4kLBSYCwdm0pIdg6aCDPgv1hzlku0peb23grI-euBHRNT5e5KU5/exec"

WA_PHONE, WA_API_KEY = "+971551347989", "7463030"
USERS = {"faisal": "faisal147", "shabana": "shabana123"}

st.set_page_config(page_title="PAICHI AI PRO v12.0", layout="wide")
st_autorefresh(interval=60000, key="paichi_refresh")

# --- 2. 🎨 PREMIUM DARK THEME ---
st.markdown("""<style>
    .stApp { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); color: white; }
    [data-testid="stSidebar"] { background: rgba(0, 0, 0, 0.8) !important; }
    .purple-box { 
        background: rgba(255, 255, 255, 0.05); 
        padding: 25px; 
        border-radius: 15px; 
        border: 1px solid #FFD700; 
        text-align: center; 
        margin-bottom: 20px; 
    }
    h1, h2, h3, p, label { color: white !important; font-weight: bold !important; }
    .stButton>button { 
        background: #FFD700; 
        color: black; 
        font-weight: bold; 
        border-radius: 10px; 
        width: 100%;
        height: 50px;
    }
</style>""", unsafe_allow_html=True)

# --- 3. HELPER FUNCTIONS ---
def get_data():
    try:
        # ഡാറ്റ എപ്പോഴും ലേറ്റസ്റ്റ് ആയി കിട്ടാൻ random വാല്യൂ ചേർക്കുന്നു
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,9999)}")
        df.columns = df.columns.str.strip()
        return df
    except: return pd.DataFrame()

def send_wa(msg):
    try:
        url = f"https://api.callmebot.com/whatsapp.php?phone={WA_PHONE}&text={urllib.parse.quote(msg)}&apikey={WA_API_KEY}"
        requests.get(url, timeout=10)
    except: pass

# --- 4. LOGIN SYSTEM ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h1 style='text-align:center;'>🚀 PAICHI AI PRO</h1>", unsafe_allow_html=True)
    with st.container():
        u = st.text_input("Username").lower()
        p = st.text_input("Password", type="password")
        if st.button("LOG IN"):
            if USERS.get(u) == p:
                st.session_state.auth, st.session_state.user = True, u
                st.rerun()
            else: st.error("യൂസർനെയിം അല്ലെങ്കിൽ പാസ്‌വേഡ് തെറ്റാണ്!")
else:
    curr_user = st.session_state.user
    df_main = get_data()
    
    # ബാലൻസ് കണക്കാക്കുന്നു
    if not df_main.empty:
        credit = pd.to_numeric(df_main['Credit'], errors='coerce').fillna(0).sum()
        debit = pd.to_numeric(df_main['Debit'], errors='coerce').fillna(0).sum()
        balance = credit - debit
    else: balance = 0

    st.markdown(f'<div class="purple-box"><p style="opacity:0.8;">CURRENT BALANCE</p><h1 style="color:#FFD700 !important; font-size:45px;">₹{balance:,.2f}</h1></div>', unsafe_allow_html=True)

    # --- MENU LOGIC ---
    if curr_user == "shabana":
        menu = ["💰 Add Entry", "🤝 Debt Tracker"]
    else:
        menu = ["📊 Market", "💰 Add Entry", "🔍 History", "🤝 Debt Tracker"]
    
    page = st.sidebar.radio("Menu", menu)

    # --- PAGES ---
    if page == "💰 Add Entry":
        st.title("New Entry 🎙️")
        v_raw = speech_to_text(language='ml', key='v_entry')
        with st.form("entry_fm", clear_on_submit=True):
            it = st.text_input("Item Name", value=v_raw if v_raw else "")
            am_input = st.text_input("Amount")
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            
            if st.form_submit_button("SAVE TRANSACTION"):
                if it and am_input:
                    try:
                        am = float(am_input)
                        # പുതിയ സ്ക്രിപ്റ്റിലേക്ക് അയക്കുന്നു
                        display_name = f"[{curr_user.capitalize()}] {it}"
                        text_p = f"{display_name} {am} {ty[0].lower()}"
                        
                        api_url = f"{SCRIPT_API}?text={urllib.parse.quote(text_p)}"
                        res = requests.get(api_url)
                        
                        if res.status_code == 200:
                            st.success(f"Saved: {it} - ₹{am}")
                            threading.Thread(target=send_wa, args=(f"✅ *Paichi Entry*\n👤 {curr_user.capitalize()}\n💰 ₹{am} - {it}",)).start()
                            st.rerun()
                        else: st.error("ഷീറ്റുമായി ബന്ധിപ്പിക്കാൻ കഴിഞ്ഞില്ല!")
                    except: st.error("അമൗണ്ട് കൃത്യമായി നൽകുക!")

    elif page == "📊 Market":
        st.title("🛢️ Crude Oil Live")
        try:
            data = yf.download("CL=F", period="1d", interval="5m", progress=False)
            if not data.empty:
                price = data['Close'].iloc[-1] * 83.5
                st.metric("CURRENT PRICE (INR)", f"₹{price:,.2f}")
                st.line_chart(data['Close'])
            else: st.warning("മാർക്കറ്റ് ഇപ്പോൾ അവധിയാണ്.")
        except: st.error("ഡാറ്റ ലഭ്യമല്ല.")

    elif page == "🔍 History":
        st.title("Transaction History 🔍")
        if not df_main.empty:
            st.dataframe(df_main.iloc[::-1], use_container_width=True)
        else: st.info("ചരിത്രം ലഭ്യമല്ല.")

    elif page == "🤝 Debt Tracker":
        st.title("Debt Management 🤝")
        with st.form("debt_fm", clear_on_submit=True):
            n = st.text_input("Name")
            a_input = st.text_input("Amount")
            t = st.selectbox("Type", ["Borrowed (കടം വാങ്ങിയത്)", "Lent (കടം കൊടുത്തത്)"])
            if st.form_submit_button("SAVE DEBT"):
                if n and a_input:
                    tag = "Lent" if "Lent" in t else "Borrowed"
                    text_p = f"[DEBT-{tag}] {n} {a_input} {'d' if 'Lent' in t else 'c'}"
                    requests.get(f"{SCRIPT_API}?text={urllib.parse.quote(text_p)}")
                    st.success("കടം വിവരങ്ങൾ സേവ് ചെയ്തു!"); st.rerun()

    if st.sidebar.button("Logout"):
        st.session_state.auth = False
        st.rerun()
