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

# --- 1. CONFIG & SETTINGS ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"

USERS = {"faisal": "faisal147", "shabana": "shabana123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI PURPLE GOLD v4.3", layout="wide")
st_autorefresh(interval=60000, key="auto_refresh")

# --- 2. 🎨 PREMIUM DESIGN ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #2D0844, #4B0082, #1A0521);
        color: #fff;
    }
    [data-testid="stSidebar"] { background: rgba(0,0,0,0.85) !important; }
    .stButton>button {
        background-color: #FFD700; color: #000; border-radius: 10px; font-weight: bold;
    }
    .balance-banner {
        background: rgba(255, 215, 0, 0.1);
        padding: 15px; border-radius: 15px; border-left: 5px solid #FFD700;
        margin-bottom: 25px; text-align: center;
    }
    .purple-box {
        background: rgba(255, 255, 255, 0.05);
        padding: 20px; border-radius: 25px; border: 2px solid rgba(255, 215, 0, 0.3);
        text-align: center; margin-bottom: 20px;
    }
    h1, h2, h3, p, label { color: white !important; font-weight: bold !important; }
    .stDataFrame { background: white; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False
if 'user' not in st.session_state: st.session_state.user = ""

# --- 3. 📊 SMART ENGINES ---

def get_total_balance():
    try:
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
        df.columns = df.columns.str.strip()
        total_in = pd.to_numeric(df['Credit'], errors='coerce').fillna(0).sum()
        total_out = pd.to_numeric(df['Debit'], errors='coerce').fillna(0).sum()
        return total_in - total_out
    except: return 0.0

def process_voice(text):
    if not text: return "Others", None, ""
    raw_text = text.lower()
    nums = re.findall(r'\d+', raw_text)
    amount = float(nums[0]) if nums else None
    clean_desc = re.sub(r'\d+', '', raw_text).strip()
    
    category = "Others"
    if any(x in raw_text for x in ["food", "ഭക്ഷണം", "ഹോട്ടൽ", "ചായ", "tea", "coffee"]): category = "Food"
    elif any(x in raw_text for x in ["shop", "കട", "സാധനം", "ഡ്രസ്സ്", "dress"]): category = "Shop"
    elif any(x in raw_text for x in ["fish", "മീൻ"]): category = "Fish"
    elif any(x in raw_text for x in ["travel", "യാത്ര", "ബസ്", "പെട്രോൾ"]): category = "Travel"
    elif any(x in raw_text for x in ["chicken", "ചിക്കൻ"]): category = "Chicken"
    elif any(x in raw_text for x in ["rent", "വാടക"]): category = "Rent"
    # Trading ഇവിടെ ഒഴിവാക്കി
    
    return category, amount, clean_desc

def create_pdf(df):
    try:
        pdf = FPDF()
        pdf.add_page(); pdf.set_font("Arial", 'B', 16)
        pdf.cell(190, 10, txt="PAICHI FINANCE REPORT", ln=True, align='C'); pdf.ln(10)
        cols = df.columns.tolist()
        pdf.set_font("Arial", 'B', 10)
        for col in cols: pdf.cell(38, 10, txt=str(col), border=1)
        pdf.ln(); pdf.set_font("Arial", size=9)
        for i, row in df.iterrows():
            for col in cols:
                val = str(row[col]).encode('ascii', 'ignore').decode('ascii')
                pdf.cell(38, 10, txt=val, border=1)
            pdf.ln()
        return pdf.output(dest='S').encode('latin-1')
    except: return None

def get_triple_advisor():
    try:
        symbols = {"Nifty 50": "^NSEI", "Bank Nifty": "^NSEBANK", "Crude Fut": "CL=F"}
        results = []
        for name, sym in symbols.items():
            df = yf.Ticker(sym).history(period="5d", interval="5m")
            if df.empty: continue
            last_p = df['Close'].iloc[-1]
            h, l, c = df['High'].iloc[-2], df['Low'].iloc[-2], df['Close'].iloc[-2]
            pivot = (h + l + c) / 3
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rsi = 100 - (100 / (1 + (gain / loss).iloc[-1]))
            if last_p > pivot and rsi > 55: signal, color = "🚀 BUY", "#00FF00"
            elif last_p < pivot and rsi < 45: signal, color = "📉 SELL", "#FF3131"
            else: signal, color = "⚖️ WAIT", "#FFFF00"
            if name == "Crude Fut": last_p = last_p * 83.5 * 1.15
            results.append({"name": name, "price": last_p, "signal": signal, "rsi": rsi, "color": color})
        return results
    except: return None

# --- 4. APP LOGIC ---
if not st.session_state.auth:
    st.title("🔐 PAICHI FINANCE LOGIN")
    u = st.text_input("Username").lower()
    p = st.text_input("Password", type="password")
    if st.button("LOGIN"):
        if USERS.get(u) == p:
            st.session_state.auth, st.session_state.user = True, u
            st.rerun()
        else: st.error("Access Denied!")
else:
    curr_user = st.session_state.user
    
    balance = get_total_balance()
    st.markdown(f"""<div class="balance-banner">
        <span style="font-size:18px; color:#E0B0FF;">Available Balance</span><br>
        <span style="font-size:32px; color:#FFD700;">₹{balance:,.2f}</span>
    </div>""", unsafe_allow_html=True)

    if curr_user == "shabana": page = "💰 Add Entry"
    else: page = st.sidebar.radio("Menu", ["📊 Advisor", "🏠 Dashboard", "💰 Add Entry", "📊 Report", "🔍 History", "🤝 Debt Tracker"])

    if st.sidebar.button("Logout"):
        st.session_state.auth = False; st.rerun()

    # --- PAGES ---
    if page == "📊 Advisor":
        st.title("🚀 Smart Trading Terminal")
        markets = get_triple_advisor()
        if markets:
            for m in markets:
                st.markdown(f"""<div class="purple-box" style="border-color: {m['color']} !important;">
                    <h2 style="color:#E0B0FF !important;">{m["name"]}</h2>
                    <h1 style="color:{m["color"]} !important; font-size:55px;">{m["signal"]}</h1>
                    <h1 style="color:#FFD700 !important; font-size:50px;">₹{m["price"]:,.0f}</h1>
                    <p>RSI: {m["rsi"]:.1f}</p>
                </div>""", unsafe_allow_html=True)

    elif page == "🏠 Dashboard":
        st.title("Financial Overview")
        try:
            df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
            df.columns = df.columns.str.strip()
            total_in = pd.to_numeric(df['Credit'], errors='coerce').fillna(0).sum()
            total_out = pd.to_numeric(df['Debit'], errors='coerce').fillna(0).sum()
            st.markdown(f"""<div class="purple-box">
                <h3>Total Credit: ₹{total_in:,.2f}</h3>
                <h3>Total Debit: ₹{total_out:,.2f}</h3>
            </div>""", unsafe_allow_html=True)
        except: st.error("Data loading error")

    elif page == "💰 Add Entry":
        st.title("Smart Voice Entry 🎙️")
        v_raw = speech_to_text(language='ml', key='voice_final_v5')
        v_cat, v_amt, v_desc = process_voice(v_raw)
        if v_raw: st.info(f"Detected: {v_cat} | Amount: {v_amt}")

        with st.form("entry_form", clear_on_submit=True):
            it = st.text_input("Description", value=v_desc if v_desc else "")
            am = st.number_input("Amount", min_value=0.0, value=v_amt)
            
            # Trading ഒഴിവാക്കിയ ലിസ്റ്റ്
            cat_list = ["Food", "Shop", "Fish", "Travel", "Chicken", "Rent", "Others"]
            cat = st.selectbox("Category", cat_list, index=cat_list.index(v_cat) if v_cat in cat_list else 6)
            
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            if st.form_submit_button("SAVE DATA"):
                if it and am > 0:
                    d, c = (am, 0) if ty == "Debit" else (0, am)
                    full_desc = f"[{curr_user.capitalize()}] {cat}: {it}"
                    requests.post(FORM_API, data={"entry.1044099436": datetime.now().strftime("%Y-%m-%d"), "entry.2013476337": full_desc, "entry.1460982454": d, "entry.1221658767": c})
                    st.success("Saved! ✅"); st.rerun()

    elif page == "📊 Report":
        st.title("Expense Analysis")
        try:
            df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
            df.columns = df.columns.str.strip()
            df['Debit'] = pd.to_numeric(df['Debit'], errors='coerce').fillna(0)
            df['Category'] = df['Item'].apply(lambda x: str(x).split(':')[0] if ':' in str(x) else 'Other')
            report_df = df[df['Debit'] > 0].groupby('Category')['Debit'].sum().reset_index()
            fig = px.pie(report_df, values='Debit', names='Category', hole=0.4)
            st.plotly_chart(fig, use_container_width=True)
        except: st.error("Report generation failed")

    elif page == "🔍 History":
        st.title("Transaction History")
        try:
            df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
            df.columns = df.columns.str.strip()
            pdf_bytes = create_pdf(df)
            if pdf_bytes: st.download_button("📥 Download PDF", pdf_bytes, "Report.pdf", "application/pdf")
            st.dataframe(df.iloc[::-1], use_container_width=True)
        except: st.write("No history found.")

    elif page == "🤝 Debt Tracker":
        st.title("Debt Management")
        with st.form("debt_form"):
            n, a = st.text_input("Name"), st.number_input("Amount", min_value=0.0)
            t = st.selectbox("Category", ["Borrowed", "Lent"])
            if st.form_submit_button("SAVE"):
                d, c = (0, a) if "Borrowed" in t else (a, 0)
                requests.post(FORM_API, data={"entry.1044099436": datetime.now().strftime("%Y-%m-%d"), "entry.2013476337": f"[{curr_user.capitalize()}] DEBT: {t} - {n}", "entry.1460982454": d, "entry.1221658767": c})
                st.success("Debt Saved! ✅")import streamlit as st

def family_vault():
    st.title("🐾 PAICHI PANTHER - Family Vault")
    
    password = st.text_input("പാസ്‌വേഡ് നൽകുക", type="password")
    
    if password == "1234": # നിനക്ക് ഇഷ്ടമുള്ള പാസ്‌വേഡ് മാറ്റാം
        st.success("സ്വാഗതം ഫൈസൽ!")
        st.subheader("സുപ്രധാന രേഖകൾ")
        st.write("- ഫഹിമയുടെ രേഖകൾ")
        st.write("- ഫിസയുടെ രേഖകൾ")
        st.write("- ഷബാനയുടെ രേഖകൾ")
        # ഇവിടെ ഫയലുകൾ അപ്‌ലോഡ് ചെയ്യാനുള്ള ഓപ്ഷനും നൽകാം
    elif password != "":
        st.error("തെറ്റായ പാസ്‌വേഡ്!")

family_vault()
