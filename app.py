import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
import plotly.express as px
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh
from fpdf import FPDF
import io
import re
import urllib.parse

# --- 1. CONFIG & SETTINGS ---
# ✅ പുതിയ ഗൂഗിൾ ഷീറ്റ് CSV ലിങ്ക് ഇവിടെ കൃത്യമായി അപ്ഡേറ്റ് ചെയ്തു ഭായ്
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTo343-OatGv9gB4uC6P-V0v9wlyHTjgwDwRiY/pub?gid=0&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"

WA_PHONE = "971551347989"
WA_API_KEY = "7463030"

USERS = {"faisal": "faisal147", "shabana": "shabana123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI EXPENSES v2.7", layout="wide")
st_autorefresh(interval=60000, key="auto_refresh")

# Session State Initialization
if 'auth' not in st.session_state: st.session_state.auth = False
if 'user' not in st.session_state: st.session_state.user = ""
if 'tasks' not in st.session_state: st.session_state.tasks = []
if 'journal' not in st.session_state: st.session_state.journal = []

# --- 2. 🎨 PREMIUM DESIGN ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #1A0521, #4B0082, #0D0214); color: #fff; }
    [data-testid="stSidebar"] { background: rgba(0,0,0,0.85) !important; }
    .stButton>button { background-color: #FFD700; color: #000; border-radius: 10px; font-weight: bold; width: 100%; }
    .balance-banner { background: rgba(255, 255, 255, 0.05); padding: 25px; border-radius: 15px; border-left: 10px solid #FFD700; margin-bottom: 25px; text-align: center; }
    .purple-box { background: rgba(255, 255, 255, 0.05); padding: 20px; border-radius: 25px; border: 2px solid rgba(255, 215, 0, 0.3); text-align: center; margin-bottom: 20px; }
    .category-box { background: rgba(255, 255, 255, 0.08); padding: 15px; border-radius: 15px; text-align: center; border-bottom: 4px solid #FFD700; margin-bottom: 15px; }
    .growth-card { background: rgba(255, 255, 255, 0.07); padding: 20px; border-radius: 15px; border-left: 5px solid #E0B0FF; margin-bottom: 15px; }
    h1, h2, h3, p, label { color: white !important; font-weight: bold !important; }
    .stDataFrame { background: white; border-radius: 10px; color: black; }
    </style>
    """, unsafe_allow_html=True)

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

def get_category_totals():
    try:
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
        df.columns = df.columns.str.strip()
        df['Debit'] = pd.to_numeric(df['Debit'], errors='coerce').fillna(0)
        
        def extract_cat(item_str):
            item_str = str(item_str)
            if 'total' in item_str.lower():
                return None
            if ':' in item_str:
                part = item_str.split(':')[0]
                if ']' in part:
                    return part.split(']')[1].strip().capitalize()
                return part.strip().capitalize()
            return "Others"
            
        df['Extracted_Category'] = df['Item'].apply(extract_cat)
        df = df.dropna(subset=['Extracted_Category'])
        cat_summary = df.groupby('Extracted_Category')['Debit'].sum().to_dict()
        return cat_summary
    except:
        return {}

def process_voice(text):
    if not text: return "Others", "", ""
    raw = text.lower().replace('.', '').replace(',', '')
    nums = re.findall(r'\d+', raw)
    amt = nums[0] if nums else ""
    desc = re.sub(r'\d+', '', raw).strip()
    category = "Others"
    if any(x in raw for x in ["food", "ഭക്ഷണം", "ചായ"]): category = "Food"
    elif any(x in raw for x in ["shop", "കട"]): category = "Shop"
    elif any(x in raw for x in ["fish", "മീൻ"]): category = "Fish"
    elif any(x in raw for x in ["travel", "യാത്ര"]): category = "Travel"
    return category, amt, desc

def create_pdf(df):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(190, 10, txt="PAICHI FINANCE REPORT", ln=True, align='C')
        pdf.ln(10)
        cols = df.columns.tolist()
        pdf.set_font("Arial", 'B', 10)
        for col in cols: pdf.cell(38, 10, txt=str(col), border=1)
        pdf.ln()
        pdf.set_font("Arial", size=9)
        for _, row in df.iterrows():
            for col in cols:
                val = str(row[col]).encode('ascii', 'ignore').decode('ascii')
                pdf.cell(38, 10, txt=val, border=1)
            pdf.ln()
        return pdf.output(dest='S').encode('latin-1')
    except: return None

def parse_mixed_dates(date_series):
    parsed_dates = []
    for val in date_series:
        val_str = str(val).strip()
        dt = pd.NaT
        try:
            dt = pd.to_datetime(val_str, errors='coerce')
            if not pd.isna(dt) and dt.year == 2026 and dt.month < 4:
                dt = datetime(2026, dt.day, dt.month)
        except: pass
        if pd.isna(dt):
            try: dt = pd.to_datetime(val_str, dayfirst=True, errors='coerce')
            except: pass
        parsed_dates.append(dt)
    return pd.Series(parsed_dates)

# --- 4. APP MAIN ---
if not st.session_state.auth:
    st.title("🔐 PAICHI EXPENSES LOGIN")
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
        menu_options = ["💰 Add Entry", "📊 Report", "🔍 History", "🤝 Debt Tracker"]
    else: 
        menu_options = ["🏠 Dashboard", "💰 Add Entry", "📊 Report", "🔍 History", "🤝 Debt Tracker", "✨ Growth & Organizer"]

    page = st.sidebar.radio("Menu", menu_options)
    if st.sidebar.button("Logout"): 
        st.session_state.auth = False
        st.rerun()

    # --- PAGES ---
    if page == "🏠 Dashboard":
        st.title("Financial Overview")
        st.markdown(f"""<div class="purple-box">
            <h2 style="color: #00FF00;">Total Credit: ₹{t_in:,.2f}</h2>
            <h2 style="color: #FF3131;">Total Debit: ₹{t_out:,.2f}</h2>
        </div>""", unsafe_allow_html=True)
        
        st.subheader("🗂️ Categorywise Expense Breakdown")
        cat_data = get_category_totals()
        if cat_data:
            cols = st.columns(3)
            for idx, (c_name, c_amount) in enumerate(cat_data.items()):
                if c_amount > 0 and c_name:
                    with cols[idx % 3]:
                        st.markdown(f"""<div class="category-box">
                            <span style="font-size:16px; color:#aaa;">Total {c_name}</span><br>
                            <span style="font-size:24px; color:#FFF; font-weight:bold;">₹{c_amount:,.2f}</span>
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
                    payload = {
                        "entry.1044099436": datetime.now().strftime("%Y-%m-%d"), 
                        "entry.2013476337": f"[{curr_user.capitalize()}] {cat}: {it}", 
                        "entry.1460982454": d, 
                        "entry.1221658767": c
                    }
                    send_to_google_async(payload)
                    send_whatsapp_auto(f"✅ *Paichi Entry*\n📝 Item: {it}\n💰 Amt: ₹{am}\n👤 User: {curr_user}")
                    st.success("Saved! ✅")
                except: st.error("Error! Please enter a valid number for amount.")

    elif page == "📊 Report" or page == "🔍 History":
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
        df.columns = df.columns.str.strip()
        df['Date'] = parse_mixed_dates(df['Date'])
        df = df[(df['Date'].dt.year == 2026) & (df['Date'].dt.month >= 4)]
        df['Month'] = df['Date'].dt.strftime('%B %Y')
        df = df.dropna(subset=['Month'])
        months = df.sort_values(by='Date', ascending=False)['Month'].unique()

        if page == "📊 Report":
            st.title("Monthly Expense Analysis")
            if len(months) == 0: st.warning("No data found in Google Sheets for April 2026 onwards!")
            else:
                sel_month = st.selectbox("Select Month", months)
                monthly_df = df[df['Month'] == sel_month].copy()
                monthly_df['Debit'] = pd.to_numeric(monthly_df['Debit'], errors='coerce').fillna(0)
                monthly_df['Credit'] = pd.to_numeric(monthly_df['Credit'], errors='coerce').fillna(0)
                m_total_debit = monthly_df['Debit'].sum()
                m_total_credit = monthly_df['Credit'].sum()
                m_savings = m_total_credit - m_total_debit
                
                col1, col2, col3 = st.columns(3)
                with col1: st.markdown(f'<div class="purple-box"><h3 style="color: #00FF00;">{sel_month} Total Credit</h3><h1 style="color: #00FF00;">₹{m_total_credit:,.2f}</h1></div>', unsafe_allow_html=True)
                with col2: st.markdown(f'<div class="purple-box"><h3 style="color: #FF3131;">{sel_month} Total Expense</h3><h1 style="color: #FF3131;">₹{m_total_debit:,.2f}</h1></div>', unsafe_allow_html=True)
                with col3: st.markdown(f'<div class="purple-box"><h3 style="color: #FFD700;">{sel_month} Net Savings</h3><h1 style="color: #FFD700;">₹{m_savings:,.2f}</h1></div>', unsafe_allow_html=True)

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
            if len(months) == 0: st.warning("No transactions found from April 2026 onwards!")
            else:
                sel_hist_month = st.selectbox("Select Month for History", months, key="history_month_select")
                filtered_history = df[df['Month'] == sel_hist_month].copy()
                clean_hist_df = filtered_history.drop(columns=['Month'], errors='ignore')
                csv_hist_data = clean_hist_df.to_csv(index=False).encode('utf-8')
                
                col_pdf, col_csv = st.columns(2)
                with col_pdf:
                    pdf_bytes = create_pdf(clean_hist_df)
                    if pdf_bytes: st.download_button(f"📄 Download {sel_hist_month} PDF", pdf_bytes, f"History_{sel_hist_month.replace(' ', '_')}.pdf", "application/pdf")
                with col_csv: st.download_button(label=f"📥 Download {sel_hist_month} CSV (Excel)", data=csv_hist_data, file_name=f"History_{sel_hist_month.replace(' ', '_')}.csv", mime="text/csv")
                clean_hist_df['Date'] = clean_hist_df['Date'].dt.strftime('%d/%m/%Y')
                st.dataframe(clean_hist_df.iloc[::-1], use_container_width=True)

    elif page == "🤝 Debt Tracker":
        st.title("Debt Management")
        with st.form("debt_form"):
            n, a = st.text_input("Name"), st.number_input("Amount", min_value=0.0)
            t = st.selectbox("Category", ["vagiyade", "koduthade"])
            if st.form_submit_button("SAVE"):
                d, c = (0, a) if "Borrowed" in t else (a, 0)
                payload = {
                    "entry.1044099436": datetime.now().strftime("%Y-%m-%d"), 
                    "entry.2013476337": f"[{curr_user.capitalize()}] DEBT: {t} - {n}", 
                    "entry.1460982454": d, 
                    "entry.1221658767": c
                }
                send_to_google_async(payload)
                st.success("Saved! ✅")

    # --- 🌟 NEW PAGE: PERSONAL GROWTH & ORGANIZER 🌟 ---
    elif page == "✨ Growth & Organizer":
        st.title("Personal Growth & Organizer ✨")
        tab1, tab2, tab3 = st.tabs(["🔮 Manifestation Journal", "📅 Alerts & Important Dates", "✅ Daily Tasks"])
        
        with tab1:
            st.subheader("28 Days Magic & Manifestation Tracker")
            with st.form("journal_form", clear_on_submit=True):
                gratitude = st.text_area("Today I am grateful for (ഇന്ന് ഞാൻ നന്ദി പറയുന്ന കാര്യങ്ങൾ)...")
                affirmation = st.text_input("My Daily Affirmation (ഇന്നത്തെ അഫിർമേഷൻ)...")
                if st.form_submit_button("Save Journal Entry"):
                    if gratitude or affirmation:
                        st.session_state.journal.append({
                            "date": datetime.now().strftime("%d/%m/%Y %I:%M %p"),
                            "gratitude": gratitude,
                            "affirmation": affirmation
                        })
                        st.success("Journal Saved for Today Magic Practice! 🌟")
            
            if st.session_state.journal:
                st.write("### 📖 Past Journal Entries")
                for j in reversed(st.session_state.journal):
                    st.markdown(f"""<div class="growth-card">
                        <span style='color: #FFD700;'>🕒 {j['date']}</span><br>
                        <b>🙏 Grateful for:</b> {j['gratitude']}<br>
                        <b>💪 Affirmation:</b> {j['affirmation']}
                    </div>""", unsafe_allow_html=True)

        with tab2:
            st.subheader("🔔 Critical Notifications & Dates Tracker")
            st.markdown("""
            <div class="growth-card" style="border-left: 5px solid #FF3131;">
                <span style="color:#FF3131; font-size:18px; font-weight:bold;">⚠️ Upcoming Exam Result Alerts:</span><br>
                <ul>
                    <li>Kerala Plus 2 Examination Results 2026</li>
                    <li>CBSE Board Results 2026</li>
                    <li>NEET UG 2026 Result Updates</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            with st.form("reminder_form", clear_on_submit=True):
                rem_title = st.text_input("Add Custom Alert/Reminder (Passport Expiry, Meeting, etc.)")
                rem_date = st.date_input("Target Date")
                if st.form_submit_button("Add Alert"):
                    if rem_title:
                        st.success(f"Alert Added: '{rem_title}' for {rem_date.strftime('%d/%m/%Y')}")

        with tab3:
            st.subheader("✅ My Daily To-Do List")
            new_task = st.text_input("Enter a new task (ചെയ്യേണ്ട കാര്യം ടൈപ്പ് ചെയ്യുക):")
            if st.button("Add Task"):
                if new_task:
                    st.session_state.tasks.append({"task": new_task, "done": False})
                    st.rerun()
            
            if st.session_state.tasks:
                st.write("---")
                for idx, t in enumerate(st.session_state.tasks):
                    col_check, col_text = st.columns([0.1, 0.9])
                    with col_check:
                        is_done = st.checkbox("", value=t['done'], key=f"task_{idx}")
                        if is_done != t['done']:
                            st.session_state.tasks[idx]['done'] = is_done
                            st.rerun()
                    with col_text:
                        if t['done']: st.markdown(f"<del style='color: #666;'>{t['task']}</del> ✅", unsafe_allow_html=True)
                        else: st.markdown(f"<b>{t['task']}</b>", unsafe_allow_html=True)
                
                if st.button("Clear Completed Tasks"):
                    st.session_state.tasks = [t for t in st.session_state.tasks if not t['done']]
                    st.rerun()
