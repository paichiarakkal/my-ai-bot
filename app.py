import streamlit as st
import pandas as pd
import requests
import json
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
CSV_URL = "https://docs.google.com/spreadsheets/d/1Ocd6zjmBuQOtOcWBAJZUxhRJjqxRfRgKCvBQTIrJTIY/export?format=csv"

# നിങ്ങൾ തന്ന പുതിയ ആപ്പ് സ്ക്രിപ്റ്റ് ലിങ്ക് ഇവിടെ കൃത്യമായി കണക്ട് ചെയ്തിരിക്കുന്നു
WEBAPP_URL = "https://script.google.com/macros/s/AKfycbx32NCrmb5UhcyEIFVhoO3mZzTjYnKuLm_MPjaNiJztGkj-fiOvlSTsXcZ_BCUKRxKWAg/exec"

# WhatsApp API Config (CallMeBot)
WA_PHONE = "971551347989"
WA_API_KEY = "7463030"

USERS = {"faisal": "faisal147", "shabana": "shabana123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI TRADING PRO v8.5", layout="wide")
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

def send_to_sheet_direct(script, debit, credit):
    # പുതിയ ഡയറക്ട് ആപ്പ് സ്ക്രിപ്റ്റ് വഴി സെക്യൂർ ആയി ഷീറ്റിലേക്ക് പോസ്റ്റ് ചെയ്യുന്നു
    payload = {"script": script, "debit": debit, "credit": credit}
    try:
        res = requests.post(WEBAPP_URL, data=json.dumps(payload), headers={"Content-Type": "application/json"}, timeout=15)
        if res.status_code == 200:
            return True
    except:
        pass
    return False

def get_totals():
    try:
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
        df.columns = df.columns.str.strip()
        t_profit = pd.to_numeric(df['Credit'], errors='coerce').fillna(0).sum()
        t_loss = pd.to_numeric(df['Debit'], errors='coerce').fillna(0).sum()
        return t_profit, t_loss, (t_profit - t_loss)
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
    t_profit, t_loss, net_p_and_l = get_totals()
    
    st.markdown(f'''<div class="balance-banner">
        <span style="font-size:20px; color: #00FFCC;">Net Trading P&L Balance</span><br>
        <span style="font-size:40px; color:#FFD700; font-weight:bold;">₹{net_p_and_l:,.2f}</span>
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
            <h2 style="color: #00FF00;">Total Profits (Credit): ₹{t_profit:,.2f}</h2>
            <h2 style="color: #FF3131;">Total Losses (Debit): ₹{t_loss:,.2f}</h2>
        </div>""", unsafe_allow_html=True)

    elif page == "💰 Add Trade":
        st.title("Log New Trade 📈")
        
        with st.form("trade_form", clear_on_submit=True):
            strike_price = st.text_input("Strike Price / Script Name (e.g., Nifty 22000 CE)")
            am_str = st.text_input("Amount (തുക)")
            ty = st.radio("Result Type", ["Profit (Credit)", "Loss (Debit)"], horizontal=True)
            
            if st.form_submit_button("SAVE TRADE & NOTIFY"):
                try:
                    am = float(am_str.strip().replace(',', ''))
                    if strike_price and am > 0:
                        c_val, d_val = (am, "") if "Profit" in ty else ("", am)
                        
                        # ഡാറ്റ നേരിട്ട് ആപ്പ് സ്ക്രിപ്റ്റിലേക്ക് തള്ളുന്നു
                        success = send_to_sheet_direct(strike_price, d_val, c_val)
                        
                        status_icon = "🟢" if "Profit" in ty else "🔴"
                        msg = f"{status_icon} *Paichi Trade Entry*\n📝 Script: {strike_price}\n💰 P&L: ₹{am} ({ty})\n👤 Trader: {curr_user}"
                        threading.Thread(target=send_whatsapp_auto, args=(msg,)).start()
                        
                        st.success("Trade Logged & WhatsApp Notification Sent! ✅")
                    else: st.error("വിവരങ്ങൾ പൂർണ്ണമായി നൽകുക!")
                except: st.error("തുക കൃത്യമായി നമ്പർ ആയി നൽകുക!")

    elif page == "📊 Report":
        st.title("Profit Analysis")
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
        df.columns = df.columns.str.strip()
        if 'Credit' in df.columns and not df[df['Credit'] > 0].empty:
            df['Credit'] = pd.to_numeric(df['Credit'], errors='coerce').fillna(0)
            fig = px.pie(df[df['Credit'] > 0], values='Credit', names='Script', hole=0.4, title="Profit Distribution")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No profit data available for chart analysis.")

    elif page == "🔍 History":
        st.title("Trade Log History")
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
        pdf_bytes = create_pdf(df)
        if pdf_bytes: st.download_button("📥 Download PDF Report", pdf_bytes, "Trading_Report.pdf", "application/pdf")
        st.dataframe(df.iloc[::-1], use_container_width=True)
