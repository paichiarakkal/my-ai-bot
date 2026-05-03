import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import yfinance as yf
import random
import re, urllib.parse, threading, base64
import plotly.express as px
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh

# --- 1. CONFIG & SETTINGS ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
SCRIPT_API = "https://script.google.com/macros/s/AKfycbzmbiWOQ-vpyOtaM6n4fosAkHRIaXyno-JyGPbxG9uZIl4W-6QzFy3hVVb-o7ctD7hl/exec"

WA_PHONE, WA_API_KEY = "971551347989", "7463030"
USERS = {"faisal": "faisal147", "shabana": "shabana123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI GOLD v8.0", layout="wide")
st_autorefresh(interval=60000, key="auto_refresh")

# --- 2. 🎨 PREMIUM DESIGN ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #2D0844, #4B0082, #1A0521); color: #fff; }
    [data-testid="stSidebar"] { background: rgba(0,0,0,0.85) !important; }
    .stButton>button { background-color: #FFD700; color: #000; border-radius: 10px; font-weight: bold; width: 100%; }
    .balance-banner { background: rgba(255, 255, 255, 0.05); padding: 25px; border-radius: 15px; border-left: 10px solid #FFD700; margin-bottom: 25px; text-align: center; }
    .purple-box { background: rgba(255, 255, 255, 0.05); padding: 20px; border-radius: 25px; border: 2px solid rgba(255, 215, 0, 0.3); text-align: center; margin-bottom: 20px; }
    h1, h2, h3, p, label { color: white !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. 📊 UTILITIES ---
def get_data():
    try:
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
        df.columns = df.columns.str.strip()
        df['Credit'] = pd.to_numeric(df['Credit'], errors='coerce').fillna(0)
        df['Debit'] = pd.to_numeric(df['Debit'], errors='coerce').fillna(0)
        return df
    except: return pd.DataFrame()

def add_to_sheet(item, amount, typ, user="App"):
    typ_param = "d" if typ.lower() == "debit" else "c"
    url = f"{SCRIPT_API}?item={urllib.parse.quote(item)}&amount={amount}&type={typ_param}&user={user}"
    try: requests.get(url, timeout=10)
    except: pass

# --- 4. MAIN APP ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 PAICHI FINANCE LOGIN")
    u, p = st.text_input("Username").lower(), st.text_input("Password", type="password")
    if st.button("LOGIN") and USERS.get(u) == p:
        st.session_state.auth, st.session_state.user = True, u
        st.rerun()
else:
    curr_user = st.session_state.user
    df_main = get_data()
    
    # ബാലൻസ് കണക്കാക്കുന്നു
    balance = 0
    if not df_main.empty:
        balance = df_main['Credit'].sum() - df_main['Debit'].sum()
    
    st.markdown(f'''<div class="balance-banner">
        <span style="font-size:20px; color: #E0B0FF;">Available Balance</span><br>
        <span style="font-size:40px; color:#FFD700; font-weight:bold;">₹{balance:,.2f}</span>
    </div>''', unsafe_allow_html=True)

    menu = ["💰 Add Entry", "🤝 Debt Tracker"] if curr_user == "shabana" else ["📊 Advisor", "🏠 Dashboard", "💰 Add Entry", "📊 Report", "🔍 History", "🤝 Debt Tracker"]
    page = st.sidebar.radio("Menu", menu)

    # --- 📊 REPORT PAGE ---
    if page == "📊 Report":
        st.title("Expense Analysis 📊")
        if not df_main.empty:
            # ഡെബിറ്റ് (ചെലവ്) ഉള്ള എൻട്രികൾ മാത്രം എടുക്കുന്നു
            expense_df = df_main[df_main['Debit'] > 0].copy()
            if not expense_df.empty:
                # Pie Chart നിർമ്മിക്കുന്നു
                fig = px.pie(expense_df, values='Debit', names='Item', 
                             title="എന്തിനൊക്കെയാണ് പണം ചെലവായത്?",
                             hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu)
                st.plotly_chart(fig, use_container_width=True)
                
                # ഓരോ ഐറ്റത്തിനും എത്ര ചെലവായി എന്ന ലിസ്റ്റ്
                st.subheader("ചെലവുകളുടെ ലിസ്റ്റ്")
                summary = expense_df.groupby('Item')['Debit'].sum().reset_index()
                st.table(summary)
            else:
                st.info("ചെലവുകളുടെ (Debit) വിവരങ്ങൾ ഷീറ്റിൽ ലഭ്യമല്ല.")
        else:
            st.error("ഡാറ്റ ലോഡ് ചെയ്യാൻ കഴിഞ്ഞില്ല!")

    # --- 🔍 HISTORY PAGE ---
    elif page == "🔍 History":
        st.title("Transaction History")
        if not df_main.empty:
            st.dataframe(df_main.iloc[::-1], use_container_width=True)

    # --- 💰 ADD ENTRY PAGE ---
    elif page == "💰 Add Entry":
        st.title("New Entry 🎙️")
        v_raw = speech_to_text(language='ml', key='voice_v8')
        with st.form("entry_form", clear_on_submit=True):
            it = st.text_input("Description", value=v_raw if v_raw else "")
            am_str = st.text_input("Amount")
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            if st.form_submit_button("SAVE"):
                if it and am_str:
                    try:
                        add_to_sheet(it, float(am_str), ty, user=curr_user.capitalize())
                        st.success("Saved! ✅"); st.rerun()
                    except: st.error("Check Amount!")

    # --- 🤝 DEBT TRACKER PAGE ---
    elif page == "🤝 Debt Tracker":
        st.title("Debt Management 🤝")
        with st.form("debt_form", clear_on_submit=True):
            person = st.text_input("Person Name")
            debt_amt = st.text_input("Amount")
            category = st.selectbox("Category", ["Lent (കൊടുത്തത്)", "Borrowed (വാങ്ങിയത്)"])
            if st.form_submit_button("SAVE"):
                ty = "Debit" if "Lent" in category else "Credit"
                add_to_sheet(f"DEBT: {person}", float(debt_amt), ty, user=curr_user.capitalize())
                st.success("Debt Saved! ✅"); st.rerun()

    if st.sidebar.button("Logout"): st.session_state.auth = False; st.rerun()
