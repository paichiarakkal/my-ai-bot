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
import urllib.parse

# --- 1. CONFIG & SETTINGS ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"

WA_PHONE = "971551347989"
WA_API_KEY = "7463030"

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

def process_voice(text):
    if not text: return "Others", "", ""
    raw = text.lower().replace('.', '').replace(',', '')
    nums = re.findall(r'\d+', raw)
    amt = nums[0] if nums else ""
    desc = re.sub(r'\d+', '', raw).strip()
    category = "Others"
    if any(x in raw for x in ["food", "ഭക്ഷണം", "ചായ"]): category = "Food"
    elif any(x in raw for x in ["shop", "കട"]): category = "Shop"
    return category, amt, desc

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
        pdf.cell(190, 10, txt="PAICHI FINANCE REPORT", ln=True, align='C'); pdf.ln(10)
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

# 🔥 തീയതി കൃത്യമാക്കാനും പഴയ മാസങ്ങളെ വെട്ടിമാറ്റാനുമുള്ള മാസ്സ് ഫംഗ്ഷൻ
def parse_mixed_dates(date_series):
    parsed_dates = []
    for val in date_series:
        val_str = str(val).strip()
        dt = pd.NaT
        try:
            # 1. ആദ്യം ഗൂഗിൾ ഫോം ഫോർമാറ്റിൽ (M/D/YYYY) നോക്കുന്നു
            dt = pd.to_datetime(val_str, errors='coerce')
            if not pd.isna(dt) and dt.year == 2026 and dt.month < 4:
                # മാസം ഏപ്രിലിന് താഴെയാണെങ്കിൽ അത് തീയതി മാറി വായിച്ചതാകാം, അത് തിരുത്തുന്നു
                dt = datetime(2026, dt.day, dt.month)
        except:
            pass
            
        if pd.isna(dt):
            try:
                # 2. നടന്നില്ലെങ്കിൽ DD/MM/YYYY രീതിയിൽ നോക്കുന്നു
                dt = pd.to_datetime(val_str, dayfirst=True, errors='coerce')
            except:
                pass
        parsed_dates.append(dt)
    return pd.Series(parsed_dates)

# --- 4. 🔔 NOTIFIER ---
def check_for_new_entries():
    url = f"{CSV_URL}&r={random.randint(1,99999)}"
    try:
        current_df = pd.read_csv(url)
        current_df.columns = current_df.columns.str.strip()
        current_row_count = len(current_df)
        if 'last_row_count' not in st.session_state:
            st.session_state.last_row_count = current_row_count
            return
        if current_row_count > st.session_state.last_row_count:
            new_rows = current_df.iloc[st.session_state.last_row_count:]
            for index, row in new_rows.iterrows():
                item_val = str(row.get('Item', ''))
                if any(x in item_val for x in ["[WhatsApp]", "[Faisal]", "[Shabana]"]):
                    amt = row.get('Amount', 0)
                    if pd.to_numeric(amt, errors='coerce') == 0 or pd.isna(amt):
                        d_val = pd.to_numeric(row.get('Debit', 0), errors='coerce') or 0
                        c_val = pd.to_numeric(row.get('Credit', 0), errors='coerce') or 0
                        amt = d_val if d_val > 0 else c_val
                    send_whatsapp_auto(f"🔔 *New Entry Detected*\n📝 {item_val}\n💰 Amount: ₹{amt}")
            st.session_state.last_row_count = current_row_count
    except: pass

check_for_new_entries()

# --- 5. APP MAIN ---
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
    t_in, t_out, balance = get_totals()
    
    st.markdown(f'''<div class="balance-banner">
        <span style="font-size:20px; color: #E0B0FF;">Available Balance</span><br>
        <span style="font-size:40px; color:#FFD700; font-weight:bold;">₹{balance:,.2f}</span>
    </div>''', unsafe_allow_html=True)

    if curr_user == "shabana": 
        menu_options = ["💰 Add Entry", "📊 Report", "🔍 History"]
    else: 
        menu_options = ["📊 Advisor", "🏠 Dashboard", "💰 Add Entry", "📊 Report", "🔍 History", "🤝 Debt Tracker"]

    page = st.sidebar.radio("Menu", menu_options)
    if st.sidebar.button("Logout"): st.session_state.auth = False; st.rerun()

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
                </div>""", unsafe_allow_html=True)

    elif page == "🏠 Dashboard":
        st.title("Financial Overview")
        st.markdown(f"""<div class="purple-box">
            <h2 style="color: #00FF00;">Total Credit: ₹{t_in:,.2f}</h2>
            <h2 style="color: #FF3131;">Total Debit: ₹{t_out:,.2f}</h2>
        </div>""", unsafe_allow_html=True)

    elif page == "💰 Add Entry":
        st.title("Smart Voice Entry 🎙️")
        v_raw = speech_to_text(language='ml', key='voice_v8')
        v_cat, v_amt, v_desc = process_voice(v_raw)
        with st.form("entry_form", clear_on_submit=True):
            it = st.text_input("Description", value=v_desc)
            am_str = st.text_input("Amount", value=str(v_amt))
            cat = st.selectbox("Category", ["Food", "Shop", "Fish", "Travel", "Rent", "Others"])
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            if st.form_submit_button("SAVE & NOTIFY"):
                try:
                    am = float(am_str.strip().replace(',', ''))
                    d, c = (am, 0) if ty == "Debit" else (0, am)
                    payload = {"entry.1044099436": datetime.now().strftime("%Y-%m-%d"), "entry.2013476337": f"[{curr_user.capitalize()}] {cat}: {it}", "entry.1460982454": d, "entry.1221658767": c}
                    send_to_google_async(payload)
                    send_whatsapp_auto(f"✅ *Paichi Entry*\n📝 Item: {it}\n💰 Amt: ₹{am}\n👤 User: {curr_user}")
                    st.success("Saved! ✅")
                    st.session_state.last_row_count += 1
                except: st.error("Error!")

    elif page == "📊 Report":
        st.title("Monthly Expense Analysis")
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
        df.columns = df.columns.str.strip()
        
        df['Date'] = parse_mixed_dates(df['Date'])
        
        # ⚠️ കടുപ്പമേറിയ ഫിൽട്ടർ: 2026 ഏപ്രിലിന് (Month >= 4) മുൻപുള്ള എല്ലാ തീയതികളെയും ഇവിടെ വെച്ച് ഒഴിവാക്കുന്നു
        df = df[df['Date'].dt.year == 2026]
        df = df[df['Date'].dt.month >= 4]
        
        df['Month'] = df['Date'].dt.strftime('%B %Y')
        df = df.dropna(subset=['Month'])
        
        months = df.sort_values(by='Date', ascending=False)['Month'].unique()
        if len(months) == 0:
            st.warning("No data found in Google Sheets for April 2026 onwards!")
        else:
            sel_month = st.selectbox("Select Month", months)
            monthly_df = df[df['Month'] == sel_month].copy()
            monthly_df['Debit'] = pd.to_numeric(monthly_df['Debit'], errors='coerce').fillna(0)
            monthly_df['Credit'] = pd.to_numeric(monthly_df['Credit'], errors='coerce').fillna(0)
            
            m_total_debit = monthly_df['Debit'].sum()
            m_total_credit = monthly_df['Credit'].sum()
            m_savings = m_total_credit - m_total_debit
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"""<div class="purple-box">
                    <h3 style="color: #00FF00;">{sel_month} Total Credit</h3>
                    <h1 style="color: #00FF00;">₹{m_total_credit:,.2f}</h1>
                </div>""", unsafe_allow_html=True)
            with col2:
                st.markdown(f"""<div class="purple-box">
                    <h3 style="color: #FF3131;">{sel_month} Total Expense</h3>
                    <h1 style="color: #FF3131;">₹{m_total_debit:,.2f}</h1>
                </div>""", unsafe_allow_html=True)
            with col3:
                st.markdown(f"""<div class="purple-box">
                    <h3 style="color: #FFD700;">{sel_month} Net Savings</h3>
                    <h1 style="color: #FFD700;">₹{m_savings:,.2f}</h1>
                </div>""", unsafe_allow_html=True)

            if m_total_debit > 0:
                monthly_df['Category_Label'] = monthly_df['Item'].apply(lambda x: x.split(':')[0] if ':' in x else 'Others')
                fig = px.pie(monthly_df[monthly_df['Debit'] > 0], values='Debit', names='Category_Label', hole=0.4, title=f"{sel_month} Expense Split")
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True)
                
            st.subheader(f"📋 {sel_month} Detailed Transactions")
            clean_table_df = monthly_df.drop(columns=['Month'], errors='ignore')
            
            csv_data = clean_table_df.to_csv(index=False).encode('utf-8')
            st.download_button(label="📥 Download Excel/CSV Report", data=csv_data, file_name=f"Report_{sel_month.replace(' ', '_')}.csv", mime="text/csv")
            
            clean_table_df['Date'] = clean_table_df['Date'].dt.strftime('%d/%m/%Y')
            st.dataframe(clean_table_df.iloc[::-1], use_container_width=True)

    elif page == "🔍 History":
        st.title("Transaction History")
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
        df.columns = df.columns.str.strip()
        
        df['Date'] = parse_mixed_dates(df['Date'])
        
        # ⚠️ ഇവിടെയും 2026 ഏപ്രിലിന് മുൻപുള്ള പഴയ ഡാറ്റകളെ ബ്ലോക്ക് ചെയ്യുന്നു
        df = df[df['Date'].dt.year == 2026]
        df = df[df['Date'].dt.month >= 4]
        
        df['Month'] = df['Date'].dt.strftime('%B %Y')
        df = df.dropna(subset=['Month'])
        
        months = df.sort_values(by='Date', ascending=False)['Month'].unique()
        
        if len(months) == 0:
            st.warning("No transactions found from April 2026 onwards!")
        else:
            sel_hist_month = st.selectbox("Select Month for History", months, key="history_month_select")
            filtered_history = df[df['Month'] == sel_hist_month].copy()
            
            clean_hist_df = filtered_history.drop(columns=['Month'], errors='ignore')
            csv_hist_data = clean_hist_df.to_csv(index=False).encode('utf-8')
            
            col_pdf, col_csv = st.columns(2)
            with col_pdf:
                pdf_bytes = create_pdf(clean_hist_df)
                if pdf_bytes: 
                    st.download_button(f"📄 Download {sel_hist_month} PDF", pdf_bytes, f"History_{sel_hist_month.replace(' ', '_')}.pdf", "application/pdf")
            with col_csv:
                st.download_button(label=f"📥 Download {sel_hist_month} CSV (Excel)", data=csv_hist_data, file_name=f"History_{sel_hist_month.replace(' ', '_')}.csv", mime="text/csv")
            
            clean_hist_df['Date'] = clean_hist_df['Date'].dt.strftime('%d/%m/%Y')
            st.dataframe(clean_hist_df.iloc[::-1], use_container_width=True)

    elif page == "🤝 Debt Tracker":
        st.title("Debt Management")
        with st.form("debt_form"):
            n, a = st.text_input("Name"), st.number_input("Amount", min_value=0.0)
            t = st.selectbox("Category", ["Borrowed", "Lent"])
            if st.form_submit_button("SAVE"):
                d, c = (0, a) if "Borrowed" in t else (a, 0)
                payload = {"entry.1044099436": datetime.now().strftime("%Y-%m-%d"), "entry.2013476337": f"[{curr_user.capitalize()}] DEBT: {t} - {n}", "entry.1460982454": d, "entry.1221658767": c}
                send_to_google_async(payload)
                st.success("Saved! ✅")
                st.session_state.last_row_count += 1
