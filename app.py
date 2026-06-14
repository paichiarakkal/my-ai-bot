import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import yfinance as yf
import random
import plotly.express as px
from streamlit_autorefresh import st_autorefresh
from fpdf import FPDF
import io
import urllib.parse
import threading

# --- 1. CONFIG & SETTINGS ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"

# WhatsApp API Config (CallMeBot)
WA_PHONE = "971551347989"
WA_API_KEY = "7463030"

USERS = {"faisal": "faisal147", "shabana": "shabana123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI TRADING PRO v1.0", layout="wide")
st_autorefresh(interval=60000, key="auto_refresh")

# --- 2. 🎨 PREMIUM DESIGN ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #0F2027, #203A43, #2C5364); color: #fff; }
    [data-testid="stSidebar"] { background: rgba(0,0,0,0.85) !important; }
    .stButton>button { background-color: #00FFCC; color: #000; border-radius: 10px; font-weight: bold; width: 100%; }
    .balance-banner { background: rgba(255, 255, 255, 0.05); padding: 25px; border-radius: 15px; border-left: 10px solid #00FFCC; margin-bottom: 25px; text-align: center; }
    .purple-box { background: rgba(255, 255, 255, 0.05); padding: 20px; border-radius: 25px; border: 2px solid rgba(0, 255, 204, 0.3); text-align: center; margin-bottom: 20px; }
    h1, h2, h3, p, label { color: white !important; font-weight: bold !important; }
    .stDataFrame { background: white; border-radius: 10px; color: black; }
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False
if 'user' not in st.session_state: st.session_state.user = ""

# --- 3. 📊 SMART ENGINES ---

def send_whatsapp_auto(message):
    url = f"https://api.callmebot.com/whatsapp.php?phone={WA_PHONE}&text={urllib.parse.quote(message)}&apikey={WA_API_KEY}"
    try: requests.get(url, timeout=10)
    except: pass

def send_to_google_async(data):
    try: requests.post(FORM_API, data=data, timeout=10)
    except: pass

def get_totals():
    try:
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
        df.columns = df.columns.str.strip()
        t_in = pd.to_numeric(df['Credit'], errors='coerce').fillna(0).sum()
        t_out = pd.to_numeric(df['Debit'], errors='coerce').fillna(0).sum()
        return t_in, t_out, (t_in - t_out)
    except: return 0.0, 0.0, 0.0

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

def create_pdf(df):
    try:
        pdf = FPDF()
        pdf.add_page(); pdf.set_font("Arial", 'B', 16)
        pdf.cell(190, 10, txt="PAICHI TRADING REPORT", ln=True, align='C'); pdf.ln(10)
        cols = df.columns.tolist()
        pdf.set_font("Arial", 'B', 10)
        for col in cols: pdf.cell(38, 10, txt=str(col), border=1)
        pdf.ln(); pdf.set_font("Arial", size=9)
        for _, row in df.iterrows():
            for col in cols:
                val = str(row[col]).encode('ascii', 'ignore').decode('ascii')
                pdf.cell(38, 10, txt=val, border=1)
            pdf.ln()
        return pdf.output(dest='S').encode('latin-1')
    except: return None

# --- 4. APP MAIN ---
if not st.session_state.auth:
    st.title("🔐 PAICHI TRADING LOGIN")
    u = st.text_input("Username").lower()
    p = st.text_input("Password", type="password")
    if st.button("LOGIN"):
        if USERS.get(u) == p:
            st.session_state.auth, st.session_state.user = True, u
            st.rerun()
        else: st.error("Access Denied!")
else:
    curr_user = st.session_state.user
    t_in, t_out, net_profit = get_totals()
    
    st.markdown(f'''<div class="balance-banner">
        <span style="font-size:20px; color: #00FFCC;">Net Trading P&L Balance</span><br>
        <span style="font-size:40px; color:#FFD700; font-weight:bold;">₹{net_profit:,.2f}</span>
    </div>''', unsafe_allow_html=True)

    if curr_user == "shabana": 
        menu_options = ["💰 Add Trade"]
    else: 
        menu_options = ["📊 Advisor", "🏠 Dashboard", "💰 Add Trade", "📊 Report", "🔍 History"]

    page = st.sidebar.radio("Menu", menu_options)
    if st.sidebar.button("Logout"): st.session_state.auth = False; st.rerun()

    # --- PAGES ---
    if page == "📊 Advisor":
        st.title("🚀 Smart Trading Terminal")
        markets = get_triple_advisor()
        if markets:
            for m in markets:
                st.markdown(f"""<div class="purple-box" style="border-color: {m['color']} !important;">
                    <h2 style="color:#00FFCC !important;">{m["name"]}</h2>
                    <h1 style="color:{m["color"]} !important; font-size:55px;">{m["signal"]}</h1>
                    <h1 style="color:#FFD700 !important; font-size:50px;">₹{m["price"]:,.0f}</h1>
                    <p>RSI: {m["rsi"]:.1f}</p>
                </div>""", unsafe_allow_html=True)

    elif page == "🏠 Dashboard":
        st.title("Trading Overview")
        st.markdown(f"""<div class="purple-box">
            <h2 style="color: #00FF00;">Total Profits (Credit): ₹{t_in:,.2f}</h2>
            <h2 style="color: #FF3131;">Total Losses (Debit): ₹{t_out:,.2f}</h2>
        </div>""", unsafe_allow_html=True)

    elif page == "💰 Add Trade":
        st.title("Log New Trade 📈")
        
        with st.form("trade_form", clear_on_submit=True):
            it = st.text_input("Trade Setup / Script Name (e.g., Nifty 22000 CE)")
            am_str = st.text_input("P&L Amount")
            cat = st.selectbox("Segment", ["Nifty Options", "Bank Nifty Options", "Crude Oil", "Equity", "Others"])
            ty = st.radio("Result Type", ["Profit (Credit)", "Loss (Debit)"], horizontal=True)
            
            if st.form_submit_button("SAVE TRADE & NOTIFY"):
                try:
                    am = float(am_str.strip().replace(',', ''))
                    if it and am > 0:
                        d, c = (am, 0) if "Loss" in ty else (0, am)
                        payload = {
                            "entry.1044099436": datetime.now().strftime("%Y-%m-%d"), 
                            "entry.2013476337": f"[{curr_user.capitalize()}] {cat}: {it}", 
                            "entry.1460982454": d, 
                            "entry.1221658767": c
                        }
                        
                        threading.Thread(target=send_to_google_async, args=(payload,)).start()
                        
                        status_icon = "🟢" if "Profit" in ty else "🔴"
                        msg = f"{status_icon} *Paichi Trade Entry*\n📝 Script: {it}\n📂 Segment: {cat}\n💰 P&L: ₹{am}\n👤 Trader: {curr_user}"
                        threading.Thread(target=send_whatsapp_auto, args=(msg,)).start()
                        st.success("Trade Logged & WhatsApp Notification Sent! ✅")
                    else: st.error("വിവരങ്ങൾ പൂർണ്ണമായി നൽകുക!")
                except: st.error("തുക കൃത്യമായി നമ്പർ ആയി നൽകുക!")

    elif page == "📊 Report":
        st.title("Segment Analysis")
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
        df.columns = df.columns.str.strip()
        df['Credit'] = pd.to_numeric(df['Credit'], errors='coerce').fillna(0)
        report_df = df[df['Credit'] > 0].copy()
        if not report_df.empty:
            fig = px.pie(report_df, values='Credit', names='Item', hole=0.4, title="Profit Distribution")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available for chart analysis.")

    elif page == "🔍 History":
        st.title("Trade Log History")
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
        pdf_bytes = create_pdf(df)
        if pdf_bytes: st.download_button("📥 Download PDF Report", pdf_bytes, "Trading_Report.pdf", "application/pdf")
        st.dataframe(df.iloc[::-1], use_container_width=True)
