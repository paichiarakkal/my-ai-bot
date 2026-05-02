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
        text = pytesseract.image_to_string(thresh, lang='eng')  # malayalam Tesseract data optional
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
# New Google Apps Script Web App (replaces old Google Form)
SCRIPT_API = "https://script.google.com/macros/s/AKfycbxQthUew_HsYckROL5zXA4oLxUVMBxiSInPrw_ZNqGf1XG6PGMyU7LYZtpYFbXTSSGf/exec"

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
    # typ: 'debit' or 'credit'
    typ_param = "debit" if typ.lower() == "debit" else "credit"
    encoded_item = urllib.parse.quote(item)
    url = f"{SCRIPT_API}?item={encoded_item}&amount={amount}&type={typ_param}"
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

    # ---------- PAGE: Add Entry (with OCR & Apps Script) ----------
    if page == "💰 Add Entry":
        st.title("New Entry & Bill 📸 + OCR 🧠")
        v_raw = speech_to_text(language='ml', key='v_entry')
        with st.form("entry_fm", clear_on_submit=True):
            it = st.text_input("Item Name", value=v_raw if v_raw else "")
            cat = st.text_input("Category (Optional)")
            am_input = st.text_input("Amount")
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            bill = st.file_uploader("Upload Bill Photo (OCR will detect amount)", type=['jpg','jpeg','png'])

            if bill:
                with st.spinner("Reading bill..."):
                    raw_text, detected_amount = extract_text_from_bill(bill)
                    if detected_amount:
                        st.info(f"💰 Detected amount: ₹{detected_amount}")
                        am_input = detected_amount
                    with st.expander("📝 Extracted Text"):
                        st.code(raw_text[:500])

            if st.form_submit_button("SAVE TRANSACTION"):
                if it and am_input:
                    try:
                        am = float(am_input)
                        link = upload_bill(bill) if bill else ""
                        display_name = f"[{curr_user.capitalize()}] {cat if cat else 'Others'}: {it}"
                        if link:
                            display_name += f" (Bill: {link})"
                        # Send to Google Apps Script
                        typ_str = "debit" if ty == "Debit" else "credit"
                        result = add_to_sheet(display_name, am, typ_str, source="App")
                        if "Saved successfully" in result or "OK" in result:
                            new_bal = balance - am if ty == "Debit" else balance + am
                            wa_msg = f"✅ *Paichi Entry*\n👤 {curr_user.capitalize()}\n💰 ₹{am} - {it}\n💳 *Balance: ₹{new_bal:,.2f}*"
                            threading.Thread(target=send_wa, args=(wa_msg,)).start()
                            st.success("Entry Saved!")
                            st.rerun()
                        else:
                            st.error(f"Sheet error: {result}")
                    except:
                        st.error("Check Amount!")

    # ---------- PAGE: Debt Tracker (with Apps Script) ----------
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
                        if "Lent" in t:
                            # Lent => credit to balance? Actually debt tracker: Lent means you gave money, so it's a credit? We'll keep as per original logic: Lent -> Debit? Wait, original code: d, c = (am,0) if "Lent" else (0,am) -> Lent treated as Debit? Actually careful: In original, "Lent" means you gave money -> that is a Debit (money goes out). "Borrowed" means you received money -> Credit. We'll follow same.
                            typ = "debit"
                            debt_desc = f"Lent to {n}"
                        else:
                            typ = "credit"
                            debt_desc = f"Borrowed from {n}"
                        display_name = f"[DEBT-{curr_user.capitalize()}] {debt_desc}"
                        result = add_to_sheet(display_name, am, typ, source="App")
                        if "Saved successfully" in result or "OK" in result:
                            new_bal = balance - am if typ=="debit" else balance + am
                            wa_msg = f"🤝 *Debt Update*\n👤 {n}\n💰 ₹{am} ({t})\n💳 *Balance: ₹{new_bal:,.2f}*"
                            threading.Thread(target=send_wa, args=(wa_msg,)).start()
                            st.success("Debt Saved!")
                            st.rerun()
                        else:
                            st.error(f"Sheet error: {result}")
                    except:
                        st.error("Check Amount!")

    # ---------- PAGE: Trading Advisor (unchanged) ----------
    elif page == "📊 Trading Advisor" and curr_user != "shabana":
        st.title("🛢️ Market Tracker")
        for name, sym in {"Crude Oil": "CL=F", "Nifty 50": "^NSEI"}.items():
            try:
                val = yf.Ticker(sym).history(period="1d")['Close'].iloc[-1]
                if "Crude" in name:
                    val *= 83.5
                st.markdown(f'<div class="purple-box"><h3>{name}</h3><h1 style="color:#00FF00 !important;">₹{val:,.2f}</h1></div>', unsafe_allow_html=True)
            except:
                pass

    # ---------- PAGE: Auto Import (unchanged) ----------
    elif page == "📥 Auto Import" and curr_user != "shabana":
        st.title("📥 Bank Statement Import (CSV)")
        st.markdown("Upload CSV with columns: `Date`, `Description`, `Amount`, `Type` (Debit/Credit)")
        uploaded = st.file_uploader("Choose CSV file", type=["csv"])
        if uploaded:
            try:
                df_import = pd.read_csv(uploaded)
                required = ['Date','Description','Amount','Type']
                if all(col in df_import.columns for col in required):
                    st.dataframe(df_import.head())
                    if st.button("✅ Import these transactions"):
                        count = 0
                        for _, row in df_import.iterrows():
                            try:
                                date = row['Date']
                                desc = row['Description']
                                amount = float(row['Amount'])
                                typ = row['Type'].lower()
                                # Use Apps Script for each entry
                                typ_param = "debit" if typ == "debit" else "credit"
                                add_to_sheet(f"[Auto-{curr_user}] {desc}", amount, typ_param)
                                count += 1
                            except:
                                pass
                        st.success(f"Imported {count} entries!")
                        send_wa(f"📥 {curr_user} imported {count} bank transactions.")
                        st.rerun()
                else:
                    st.error("CSV must have columns: Date, Description, Amount, Type")
            except Exception as e:
                st.error(f"Error: {e}")

    # ---------- PAGE: Monthly Reports (unchanged) ----------
    elif page == "📈 Monthly Reports" and curr_user != "shabana":
        st.title("📊 Monthly Financial Report")
        if df_main.empty:
            st.warning("No data available.")
        else:
            df_report = df_main.copy()
            df_report['Credit'] = pd.to_numeric(df_report['Credit'], errors='coerce').fillna(0)
            df_report['Debit'] = pd.to_numeric(df_report['Debit'], errors='coerce').fillna(0)
            if 'Date' in df_report.columns:
                df_report['Month'] = pd.to_datetime(df_report['Date']).dt.to_period('M').astype(str)
                monthly = df_report.groupby('Month').agg({'Credit':'sum', 'Debit':'sum'}).reset_index()
                monthly['Balance'] = monthly['Credit'] - monthly['Debit']
                fig_line = px.line(monthly, x='Month', y=['Credit','Debit','Balance'], title="Monthly Trend", markers=True)
                st.plotly_chart(fig_line, use_container_width=True)
                fig_bar = px.bar(monthly, x='Month', y=['Credit','Debit'], barmode='group', title="Credit vs Debit per Month")
                st.plotly_chart(fig_bar, use_container_width=True)
                st.subheader("Month-wise Summary")
                st.dataframe(monthly.style.format({'Credit':'₹{:.2f}','Debit':'₹{:.2f}','Balance':'₹{:.2f}'}))
            else:
                st.error("Date column missing")

    # ---------- PAGE: Dashboard (simple) ----------
    elif page == "🏠 Dashboard" and curr_user != "shabana":
        st.title("Dashboard")
        if not df_main.empty and 'Category' in df_main.columns:
            cat_summary = df_main.groupby('Category')['Amount'].sum().reset_index()
            fig = px.pie(cat_summary, names='Category', values='Amount', title="Expense by Category")
            st.plotly_chart(fig)
        else:
            st.info("No category data yet.")

    elif page == "📊 Report" and curr_user != "shabana":
        st.title("Report")
        st.dataframe(df_main)

    elif page == "🔍 History" and curr_user != "shabana":
        st.title("History")
        st.dataframe(df_main.iloc[::-1], use_container_width=True)

    # Logout button
    if st.sidebar.button("Logout"):
        st.session_state.auth = False
        st.rerun()
