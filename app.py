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
import urllib.parse, re

# --- 1. CONFIG & SETTINGS ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"
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
    .stDataFrame { background: white; border-radius: 10px; color: black; }
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth, st.session_state.user = False, ""

# --- 3. 📊 SMART ENGINES ---
def send_whatsapp_auto(msg):
    try: requests.get(f"https://api.callmebot.com/whatsapp.php?phone={WA_PHONE}&text={urllib.parse.quote(msg)}&apikey={WA_API_KEY}", timeout=10)
    except: pass

def send_to_google_async(data):
    try: requests.post(FORM_API, data=data, timeout=10)
    except: pass

def load_filtered_df():
    try:
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,99999)}")
        df.columns = df.columns.str.strip()
        parsed = []
        for val in df['Date']:
            v_str, dt = str(val).strip(), pd.NaT
            try:
                dt = pd.to_datetime(v_str, errors='coerce')
                if not pd.isna(dt) and dt.year == 2026 and dt.month < 4:
                    dt = datetime(2026, dt.day, dt.month)
            except: pass
            if pd.isna(dt):
                try: dt = pd.to_datetime(v_str, dayfirst=True, errors='coerce')
                except: pass
            parsed.append(dt)
        df['Date'] = pd.Series(parsed)
        return df[(df['Date'].dt.year == 2026) & (df['Date'].dt.month >= 4)].copy()
    except: return pd.DataFrame()

def get_totals():
    try:
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
        df.columns = df.columns.str.strip()
        t_in = pd.to_numeric(df['Credit'], errors='coerce').fillna(0).sum()
        t_out = pd.to_numeric(df['Debit'], errors='coerce').fillna(0).sum()
        return t_in, t_out, (t_in - t_out)
    except: return 0.0, 0.0, 0.0

def process_voice(text):
    if not text: return "Others", "", ""
    raw = text.lower().replace('.', '').replace(',', '')
    nums = re.findall(r'\d+', raw)
    cat = "Food" if any(x in raw for x in ["food", "ഭക്ഷണം", "ചായ"]) else ("Shop" if any(x in raw for x in ["shop", "കട"]) else "Others")
    return cat, (nums[0] if nums else ""), re.sub(r'\d+', '', raw).strip()

def get_triple_advisor():
    try:
        symbols, results = {"Nifty 50": "^NSEI", "Bank Nifty": "^NSEBANK", "Crude Fut": "CL=F"}, []
        for name, sym in symbols.items():
            df = yf.Ticker(sym).history(period="5d", interval="5m")
            if df.empty: continue
            last_p = df['Close'].iloc[-1]
            pivot = (df['High'].iloc[-2] + df['Low'].iloc[-2] + df['Close'].iloc[-2]) / 3
            delta = df['Close'].diff()
            rsi = 100 - (100 / (1 + (delta.where(delta > 0, 0).rolling(14).mean() / -delta.where(delta < 0, 0).rolling(14).mean()).iloc[-1]))
            sig, col = ("🚀 BUY", "#00FF00") if last_p > pivot and rsi > 55 else (("📉 SELL", "#FF3131") if last_p < pivot and rsi < 45 else ("⚖️ WAIT", "#FFFF00"))
            if name == "Crude Fut": last_p *= 83.5 * 1.15
            results.append({"name": name, "price": last_p, "signal": sig, "color": col})
        return results
    except: return None

def create_pdf(df):
    try:
        pdf = FPDF()
        pdf.add_page(); pdf.set_font("Arial", 'B', 16)
        pdf.cell(190, 10, txt="PAICHI FINANCE REPORT", ln=True, align='C'); pdf.ln(10)
        pdf.set_font("Arial", 'B', 10)
        for col in df.columns: pdf.cell(38, 10, txt=str(col), border=1)
        pdf.ln(); pdf.set_font("Arial", size=9)
        for _, row in df.iterrows():
            for col in df.columns: pdf.cell(38, 10, txt=str(row[col]).encode('ascii', 'ignore').decode('ascii'), border=1)
            pdf.ln()
        return pdf.output(dest='S').encode('latin-1')
    except: return None

# --- 4. 🔔 NOTIFIER ---
def check_for_new_entries():
    try:
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,99999)}")
        df.columns = df.columns.str.strip()
        if 'last_row_count' not in st.session_state:
            st.session_state.last_row_count = len(df)
            return
        if len(df) > st.session_state.last_row_count:
            for _, row in df.iloc[st.session_state.last_row_count:].iterrows():
                item = str(row.get('Item', ''))
                if any(x in item for x in ["[WhatsApp]", "[Faisal]", "[Shabana]"]):
                    amt = pd.to_numeric(row.get('Amount', 0), errors='coerce')
                    if amt == 0 or pd.isna(amt):
                        amt = pd.to_numeric(row.get('Debit', 0), errors='coerce') or pd.to_numeric(row.get('Credit', 0), errors='coerce') or 0
                    send_whatsapp_auto(f"🔔 *New Entry Detected*\n📝 {item}\n💰 Amount: ₹{amt}")
            st.session_state.last_row_count = len(df)
    except: pass

check_for_new_entries()

# --- 5. APP MAIN ---
if not st.session_state.auth:
    st.title("🔐 PAICHI FINANCE LOGIN")
    u, p = st.text_input("Username").lower(), st.text_input("Password", type="password")
    if st.button("LOGIN") and USERS.get(u) == p:
        st.session_state.auth, st.session_state.user = True, u
        st.rerun()
    elif st.button("LOGIN"): st.error("Access Denied!")
else:
    curr_user = st.session_state.user
    t_in, t_out, balance = get_totals()
    st.markdown(f'<div class="balance-banner"><span style="font-size:20px; color: #E0B0FF;">Available Balance</span><br><span style="font-size:40px; color:#FFD700; font-weight:bold;">₹{balance:,.2f}</span></div>', unsafe_allow_html=True)

    menu_options = ["💰 Add Entry", "📊 Report", "🔍 History"] if curr_user == "shabana" else ["📊 Advisor", "🏠 Dashboard", "💰 Add Entry", "📊 Report", "🔍 History", "🤝 Debt Tracker"]
    page = st.sidebar.radio("Menu", menu_options)
    if st.sidebar.button("Logout"): st.session_state.auth = False; st.rerun()

    if page == "📊 Advisor":
        st.title("🚀 Smart Trading Terminal")
        markets = get_triple_advisor()
        if markets:
            for m in markets:
                st.markdown(f'<div class="purple-box" style="border-color: {m["color"]} !important;"><h2 style="color:#E0B0FF !important;">{m["name"]}</h2><h1 style="color:{m["color"]} !important; font-size:55px;">{m["signal"]}</h1><h1 style="color:#FFD700 !important; font-size:50px;">₹{m["price"]:,.0f}</h1></div>', unsafe_allow_html=True)

    elif page == "🏠 Dashboard":
        st.title("Financial Overview")
        st.markdown(f'<div class="purple-box"><h2 style="color: #00FF00;">Total Credit: ₹{t_in:,.2f}</h2><h2 style="color: #FF3131;">Total Debit: ₹{t_out:,.2f}</h2></div>', unsafe_allow_html=True)

    elif page == "💰 Add Entry":
        st.title("Smart Voice Entry 🎙️")
        v_cat, v_amt, v_desc = process_voice(speech_to_text(language='ml', key='voice_v8'))
        with st.form("entry_form", clear_on_submit=True):
            it, am_str = st.text_input("Description", value=v_desc), st.text_input("Amount", value=str(v_amt))
            cat = st.selectbox("Category", ["Food", "Shop", "Fish", "Travel", "Rent", "Others"], index=["Food", "Shop", "Fish", "Travel", "Rent", "Others"].index(v_cat))
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            if st.form_submit_button("SAVE & NOTIFY"):
                try:
                    am = float(am_str.strip().replace(',', ''))
                    send_to_google_async({"entry.1044099436": datetime.now().strftime("%Y-%m-%d"), "entry.2013476337": f"[{curr_user.capitalize()}] {cat}: {it}", "entry.1460982454": am if ty == "Debit" else 0, "entry.1221658767": 0 if ty == "Debit" else am})
                    send_whatsapp_auto(f"✅ *Paichi Entry*\n📝 Item: {it}\n💰 Amt: ₹{am}\n👤 User: {curr_user}")
                    st.success("Saved! ✅"); st.session_state.last_row_count += 1
                except: st.error("Error!")

    elif page in ["📊 Report", "🔍 History"]:
        df = load_filtered_df()
        if df.empty:
            st.warning("No data found from April 2026 onwards!")
        else:
            df['Month'] = df['Date'].dt.strftime('%B %Y')
            months = df.sort_values(by='Date', ascending=False)['Month'].unique()
            sel_month = st.selectbox("Select Month", months, key=f"month_{page}")
            m_df = df[df['Month'] == sel_month].copy()
            m_df['Debit'] = pd.to_numeric(m_df['Debit'], errors='coerce').fillna(0)
            m_df['Credit'] = pd.to_numeric(m_df['Credit'], errors='coerce').fillna(0)
            
            clean_df = m_df.drop(columns=['Month'], errors='ignore')
            csv_data = clean_df.to_csv(index=False).encode('utf-8')

            if page == "📊 Report":
                st.title("Monthly Expense Analysis")
                deb, cred = m_df['Debit'].sum(), m_df['Credit'].sum()
                c1, c2, c3 = st.columns(3)
                c1.markdown(f'<div class="purple-box"><h3 style="color: #00FF00;">Total Credit</h3><h1 style="color: #00FF00;">₹{cred:,.2f}</h1></div>', unsafe_allow_html=True)
                c2.markdown(f'<div class="purple-box"><h3 style="color: #FF3131;">Total Expense</h3><h1 style="color: #FF3131;">₹{deb:,.2f}</h1></div>', unsafe_allow_html=True)
                c3.markdown(f'<div class="purple-box"><h3 style="color: #FFD700;">Net Savings</h3><h1 style="color: #FFD700;">₹{cred-deb:,.2f}</h1></div>', unsafe_allow_html=True)

                if deb > 0:
                    m_df['Category_Label'] = m_df['Item'].apply(lambda x: x.split(':')[0] if ':' in x else 'Others')
                    st.plotly_chart(px.pie(m_df[m_df['Debit'] > 0], values='Debit', names='Category_Label', hole=0.4, title=f"{sel_month} Expense Split"), use_container_width=True)
                
                st.download_button("📥 Download Excel/CSV Report", csv_data, f"Report_{sel_month.replace(' ', '_')}.csv", "text/csv")
            else:
                st.title("Transaction History")
                col_pdf, col_csv = st.columns(2)
                with col_pdf:
                    p_bytes = create_pdf(clean_df)
                    if p_bytes: st.download_button(f"📄 Download PDF", p_bytes, f"History_{sel_month.replace(' ', '_')}.pdf", "application/pdf")
                with col_csv:
                    st.download_button("📥 Download CSV (Excel)", csv_data, f"History_{sel_month.replace(' ', '_')}.csv", "text/csv")

            clean_df['Date'] = clean_df['Date'].dt.strftime('%d/%m/%Y')
            st.dataframe(clean_df.iloc[::-1], use_container_width=True)

    elif page == "🤝 Debt Tracker":
        st.title("Debt Management")
        with st.form("debt_form"):
            n, a = st.text_input("Name"), st.number_input("Amount", min_value=0.0)
            t = st.selectbox("Category", ["Borrowed", "Lent"])
            if st.form_submit_button("SAVE"):
                send_to_google_async({"entry.1044099436": datetime.now().strftime("%Y-%m-%d"), "entry.2013476337": f"[{curr_user.capitalize()}] DEBT: {t} - {n}", "entry.1460982454": 0 if "Borrowed" in t else a, "entry.1221658767": a if "Borrowed" in t else 0})
                st.success("Saved! ✅"); st.session_state.last_row_count += 1
