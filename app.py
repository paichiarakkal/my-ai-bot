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

# --- 1. CONFIG & SETTINGS ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"
WA_PHONE = "971551347989"
WA_API_KEY = "7463030"
USERS = {"faisal": "faisal147", "shabana": "shabana123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI DASHBOARD v8.0", layout="wide")
st_autorefresh(interval=60000, key="auto_refresh")

# --- 2. 🎨 CLEAN MODERN CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f6; }
    [data-testid="stMetricValue"] { color: #2c3e50 !important; font-size: 28px !important; }
    .main-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .stButton>button {
        background: #3498db;
        color: white;
        border-radius: 8px;
        height: 50px;
        font-weight: bold;
    }
    h1, h2, h3 { color: #2c3e50 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FUNCTIONS ---
def send_wa(msg):
    url = f"https://api.callmebot.com/whatsapp.php?phone={WA_PHONE}&text={urllib.parse.quote(msg)}&apikey={WA_API_KEY}"
    try: requests.get(url, timeout=10)
    except: pass

def get_data():
    try:
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
        df.columns = df.columns.str.strip()
        df['Debit'] = pd.to_numeric(df['Debit'], errors='coerce').fillna(0)
        df['Credit'] = pd.to_numeric(df['Credit'], errors='coerce').fillna(0)
        return df
    except: return pd.DataFrame()

# --- 4. AUTHENTICATION ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<div style='text-align:center; padding:50px;'><h1>🏦 PAICHI LOGIN</h1></div>", unsafe_allow_html=True)
        u = st.text_input("Username").lower()
        p = st.text_input("Password", type="password")
        if st.button("LOGIN"):
            if USERS.get(u) == p:
                st.session_state.auth, st.session_state.user = True, u
                st.rerun()
            else: st.error("Invalid Credentials!")
else:
    # --- 5. MAIN DASHBOARD ---
    df = get_data()
    
    with st.sidebar:
        st.title(f"Hi, {st.session_state.user.capitalize()}")
        menu = st.radio("Navigation", ["📊 Dashboard", "➕ Add Entry", "📜 History"])
        if st.button("Logout"):
            st.session_state.auth = False
            st.rerun()

    if menu == "📊 Dashboard":
        st.markdown("## 📈 Financial Overview")
        
        if not df.empty:
            ti = df['Credit'].sum()
            te = df['Debit'].sum()
            bal = ti - te
            
            # ടോപ്പ് മെട്രിക്സ്
            c1, c2, c3 = st.columns(3)
            with c1: st.metric("Total Income", f"₹{ti:,.2f}")
            with c2: st.metric("Total Expense", f"₹{te:,.2f}", delta=f"-₹{te:,.2f}", delta_color="inverse")
            with c3: st.metric("Current Balance", f"₹{bal:,.2f}")

            # ഗ്രാഫുകൾ
            st.markdown("---")
            col_left, col_right = st.columns(2)
            
            with col_left:
                st.subheader("Daily Spending")
                fig_bar = px.bar(df.tail(10), x=df.columns[0], y='Debit', color_discrete_sequence=['#3498db'])
                st.plotly_chart(fig_bar, use_container_width=True)
                
            with col_right:
                st.subheader("Income vs Expense")
                fig_pie = px.pie(values=[ti, te], names=['Income', 'Expense'], color_discrete_sequence=['#2ecc71', '#e74c3c'])
                st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("ഷീറ്റിൽ ഡാറ്റയൊന്നുമില്ല. ഒരു എൻട്രി ചേർക്കൂ!")

    elif menu == "➕ Add Entry":
        st.markdown("## ➕ New Transaction")
        with st.form("new_entry", clear_on_submit=True):
            desc = st.text_input("Description")
            cat = st.text_input("Category")
            amt = st.number_input("Amount", min_value=0.0, step=1.0)
            kind = st.selectbox("Type", ["Debit", "Credit"])
            
            if st.form_submit_button("SAVE"):
                d, c = (amt, 0) if kind == "Debit" else (0, amt)
                full_desc = f"[{st.session_state.user}] {cat}: {desc}"
                requests.post(FORM_API, data={
                    "entry.1044099436": datetime.now().strftime("%Y-%m-%d"),
                    "entry.2013476337": full_desc,
                    "entry.1460982454": d,
                    "entry.1221658767": c
                })
                st.success("സേവ് ആയി!")
                # വാട്സാപ്പ് അയക്കുന്നു
                wa_msg = f"✅ *New Entry*\n👤 User: {st.session_state.user}\n💰 Amount: ₹{amt}\n📝 {cat}: {desc}"
                threading.Thread(target=send_wa, args=(wa_msg,)).start()

    elif menu == "📜 History":
        st.markdown("## 📜 Transaction History")
        st.dataframe(df.iloc[::-1], use_container_width=True)
