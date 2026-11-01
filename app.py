import streamlit as st
import google.generativeai as genai
import pandas as pd
import requests
from datetime import datetime, timezone
import random
import plotly.express as px
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh
from fpdf import FPDF
import re
import urllib.parse
import threading
import json
from groq import Groq
from streamlit_calendar import calendar

# --- CONFIG & SETTINGS ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"
WA_PHONE, WA_API_KEY = "971551347989", "7463030"
USER_PINS = {"faisal": "1470", "shabana": "1230", "admin": "7860"}
BG_IMAGE_URL = "https://raw.githubusercontent.com/paichiarakkal/paichiarakkal/main/profile.jpg"

# --- STREAMLIT UI SETUP ---
st.set_page_config(page_title="PAICHI EXPENSES v5.0", layout="wide")
st_autorefresh(interval=60000, key="auto_refresh")

st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{ background-image: linear-gradient(rgba(0, 0, 0, 0.75), rgba(0, 0, 0, 0.75)), url("{BG_IMAGE_URL}"); background-size: cover; background-attachment: fixed; }}
    [data-testid="stSidebar"] {{ background: rgba(0, 0, 0, 0.85) !important; }}
    .stButton>button {{ background-color: #FFD700; color: #000; border-radius: 10px; font-weight: bold; width: 100%; }}
    .balance-banner {{ background: rgba(0, 0, 0, 0.7); backdrop-filter: blur(10px); padding: 25px; border-radius: 15px; border-left: 10px solid #FFD700; text-align: center; margin-bottom: 25px; }}
    .purple-box {{ background: rgba(0, 0, 0, 0.7); padding: 20px; border-radius: 25px; border: 2px solid rgba(255, 215, 0, 0.3); text-align: center; margin-bottom: 20px; }}
    .category-box {{ background: rgba(0, 0, 0, 0.7); padding: 15px; border-radius: 15px; text-align: center; border-bottom: 4px solid #FFD700; margin-bottom: 15px; }}
    .alert-banner {{ background-color: #ff4d4d; color: white; padding: 10px; border-radius: 10px; text-align: center; font-weight: bold; margin-bottom: 20px; }}
    .login-card {{ background: rgba(0, 0, 0, 0.8); padding: 25px; border-radius: 20px; max-width: 450px; margin: auto; margin-top: 50px; }}
    h1, h2, h3, p, label {{ color: white !important; font-weight: bold !important; }}
    </style>
""", unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth, st.session_state.user = False, ""
if 'custom_alert_text' not in st.session_state: st.session_state.custom_alert_text = "Shop kuri book"
if 'low_limit' not in st.session_state: st.session_state.low_limit = 6000

# --- HELPER FUNCTIONS ---
def send_whatsapp_auto(msg):
    threading.Thread(target=lambda: requests.get(f"https://api.callmebot.com/whatsapp.php?phone={WA_PHONE}&text={urllib.parse.quote(msg)}&apikey={WA_API_KEY}", timeout=10)).start()

def parse_mixed_dates(date_series):
    parsed = []
    for val in date_series:
        dt = pd.to_datetime(str(val).strip(), errors='coerce')
        if not pd.isna(dt) and dt.year == 2026 and dt.month < 4: dt = datetime(2026, dt.day, dt.month)
        if pd.isna(dt): dt = pd.to_datetime(str(val).strip(), dayfirst=True, errors='coerce')
        parsed.append(dt)
    return pd.Series(parsed)

@st.cache_data(ttl=10)
def load_data():
    try:
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
        df.columns = df.columns.str.strip()
        df['Date'] = parse_mixed_dates(df['Date'])
        df['Debit'] = pd.to_numeric(df['Debit'], errors='coerce').fillna(0)
        df['Credit'] = pd.to_numeric(df['Credit'], errors='coerce').fillna(0)
        return df
    except: return pd.DataFrame()

def create_pdf(df):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(190, 10, txt="PAICHI FINANCE REPORT", ln=True, align='C')
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 10)
        widths = {"Date": 30, "Item": 85, "Debit": 35, "Credit": 35}
        for col in widths: pdf.cell(widths[col], 10, txt=col, border=1, align='C')
        pdf.ln()
        pdf.set_font("Arial", size=9)
        for _, row in df.iterrows():
            if pdf.get_y() > 260: pdf.add_page()
            y_start = pdf.get_y()
            pdf.cell(30, 10, txt=str(row['Date']), border=0)
            x_after_date = pdf.get_x()
            pdf.multi_cell(85, 5, txt=str(row['Item']).encode('ascii', 'ignore').decode('ascii'), border=0)
            h = max(10, pdf.get_y() - y_start)
            pdf.set_xy(x_after_date + 85, y_start)
            pdf.cell(35, h, txt=str(row['Debit']), border=0, align='R')
            pdf.cell(35, h, txt=str(row['Credit']), border=0, align='R')
            pdf.set_xy(10, y_start)
            for w in widths.values(): pdf.cell(w, h, txt="", border=1)
            pdf.set_y(y_start + h)
        return bytes(pdf.output())
    except: return None

# --- GROQ AI AGENT SETUP ---
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
if not GROQ_API_KEY: st.sidebar.error("Groq API Key ലഭ്യമല്ല!")

def add_new_entry(item, amount, category="Others", type="Debit"):
    try:
        payload = {
            "entry.1044099436": datetime.now().strftime("%Y-%m-%d"), 
            "entry.2013476337": f"[{st.session_state.user.capitalize()}] {category}: {item}", 
            "entry.1460982454": amount if type.lower() == "debit" else 0, 
            "entry.1221658767": 0 if type.lower() == "debit" else amount
        }
        requests.post(FORM_API, data=payload, timeout=10)
        send_whatsapp_auto(f"✅ *AI Entry Added*\n📝 Item: {item}\n💰 Amt: ₹{amount}")
        st.cache_data.clear()
        return f"Success: {item} - ₹{amount} ({type})"
    except Exception as e:
        return f"Error: {str(e)}"

tools = [{
    "type": "function",
    "function": {
        "name": "add_new_entry",
        "description": "Add a new expense or income to Google Sheet.",
        "parameters": {
            "type": "object",
            "properties": {
                "item": {"type": "string", "description": "Item name (e.g., Tea, Petrol)"},
                "amount": {"type": "number", "description": "Amount (e.g., 50, 500)"},
                "category": {"type": "string", "description": "Food, Shop, Fish, Travel, Rent, Others"},
                "type": {"type": "string", "enum": ["Debit", "Credit"], "description": "Debit for expense, Credit for income"}
            },
            "required": ["item", "amount"]
        }
    }
}]

# --- 🔒 LOGIN SCREEN ---
if not st.session_state.auth:
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.subheader("🔐 PAICHI EXPENSES LOGIN")
    u = st.selectbox("👤 Select User", ["faisal", "shabana", "admin"]).lower()
    pin = st.text_input("🔑 Enter 4-Digit PIN", type="password", max_chars=4)
    if st.button("UNLOCK APP 🔓"):
        if USER_PINS.get(u) == pin:
            st.session_state.auth, st.session_state.user = True, u
            st.rerun()
        else: st.error("❌ Incorrect PIN!")
    st.markdown('</div>', unsafe_allow_html=True)

else:
    df = load_data()
    t_in, t_out = (df['Credit'].sum(), df['Debit'].sum()) if not df.empty else (0.0, 0.0)
    bal = t_in - t_out
    
    # SIDEBAR SETTINGS
    if st.session_state.user != "shabana":
        with st.sidebar.expander("⚙️ Settings"):
            st.session_state.custom_alert_text = st.text_area("Alert Message", value=st.session_state.custom_alert_text)
            st.session_state.low_limit = st.number_input("Low Balance Limit (₹)", value=st.session_state.low_limit)
    
    if bal < st.session_state.low_limit:
        st.markdown(f'<div class="alert-banner">⚠️ ബാലൻസ് കുറവാണ്: {st.session_state.custom_alert_text} (₹{bal:,.2f})!</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="balance-banner"><span style="font-size:20px; color:#E0B0FF;">Available Balance</span><br><span style="font-size:40px; color:#FFD700;">₹{bal:,.2f}</span></div>', unsafe_allow_html=True)
    
    menu = ["💰 Add Entry", "📅 Calendar", "📊 Report", "🔍 History", "🤝 Debt Tracker", "🤖 AI Chat", "🧠 My AI Buddy"]
    if st.session_state.user != "shabana": menu.insert(0, "🏠 Dashboard")
    page = st.sidebar.radio("Menu", menu)
    if st.sidebar.button("Logout"): st.session_state.auth = False; st.rerun()

    # --- DASHBOARD ---
    if page == "🏠 Dashboard" and not df.empty:
        st.title("Financial Overview")
        st.markdown(f'<div class="purple-box"><h2 style="color:#00FF00;">Credit: ₹{t_in:,.2f}</h2><h2 style="color:#FF3131;">Debit: ₹{t_out:,.2f}</h2></div>', unsafe_allow_html=True)
        def extract_cat(x):
            item_text = str(x).lower()
            if any(w in item_text for w in ["food", "ഭക്ഷണം", "ചായ", "ഹോട്ടൽ", "ബിരിയാണി"]): return "Food"
            elif any(w in item_text for w in ["shop", "കട", "സാധനങ്ങൾ", "സൂപ്പർമാർക്കറ്റ്"]): return "Shop"
            elif any(w in item_text for w in ["fish", "മീൻ", "ഇറച്ചി", "ചിക്കൻ"]): return "Fish"
            elif any(w in item_text for w in ["travel", "യാത്ര", "പെട്രോൾ", "വണ്ടി", "ടാക്സി"]): return "Travel"
            elif any(w in item_text for w in ["rent", "വാടക", "റൂം"]): return "Rent"
            return "Others"
        df['Cat'] = df['Item'].apply(extract_cat)
        cats = df.groupby('Cat')['Debit'].sum().to_dict()
        cols = st.columns(3)
        for idx, (c_name, c_amt) in enumerate(cats.items()):
            if c_amt > 0:
                with cols[idx % 3]: st.markdown(f'<div class="category-box"><span style="color:#aaa;">Total {c_name}</span><br><span style="font-size:24px; color:#FFF;">₹{c_amt:,.2f}</span></div>', unsafe_allow_html=True)

    # --- ADD ENTRY ---
    elif page == "💰 Add Entry":
        st.title("Smart Voice Entry 🎙️")
        v_raw = speech_to_text(language='ml', key='voice_v9')
        v_cat, v_amt, v_desc, v_type = "Others", "", "", "Debit"
        
        if v_raw:
            raw = v_raw.lower().replace('.', '').replace(',', '')
            nums = re.findall(r'\d+', raw)
            v_amt = nums[0] if nums else ""
            v_desc = re.sub(r'\d+', '', raw).strip()
            if any(x in raw for x in ["food", "ഭക്ഷണം", "ചായ", "ഹോട്ടൽ", "ബിരിയാണി"]): v_cat = "Food"
            elif any(x in raw for x in ["shop", "കട"]): v_cat = "Shop"
            elif any(x in raw for x in ["fish", "മീൻ", "ചിക്കൻ"]): v_cat = "Fish"
            elif any(x in raw for x in ["travel", "പെട്രോൾ", "വണ്ടി"]): v_cat = "Travel"
            if any(x in raw for x in ["കിട്ടി", "വന്നു", "തന്നു"]): v_type = "Credit"

        with st.form("entry_form", clear_on_submit=True):
            it = st.text_input("Description", value=v_desc)
            am_str = st.text_input("Amount", value=str(v_amt))
            cat = st.selectbox("Category", ["Food", "Shop", "Fish", "Travel", "Rent", "Others"], index=["Food", "Shop", "Fish", "Travel", "Rent", "Others"].index(v_cat))
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True, index=0 if v_type == "Debit" else 1)
            if st.form_submit_button("SAVE & NOTIFY"):
                try:
                    am = float(am_str.strip().replace(',', ''))
                    payload = {"entry.1044099436": datetime.now().strftime("%Y-%m-%d"), "entry.2013476337": f"[{st.session_state.user.capitalize()}] {cat}: {it}", "entry.1460982454": am if ty=="Debit" else 0, "entry.1221658767": 0 if ty=="Debit" else am}
                    requests.post(FORM_API, data=payload, timeout=10)
                    send_whatsapp_auto(f"✅ *Paichi Entry*\n📝 {it}\n💰 ₹{am}")
                    st.success("Saved! ✅"); st.rerun()
                except: st.error("Error! Valid amount required.")

    # --- CALENDAR ---
    elif page == "📅 Calendar" and not df.empty:
        st.title("P&L Calendar View 📅")
        df_cal = df.dropna(subset=['Date'])
        summary = df_cal.groupby(df_cal['Date'].dt.strftime('%Y-%m-%d')).agg({'Debit': 'sum', 'Credit': 'sum'}).reset_index()
        events = []
        for _, row in summary.iterrows():
            if row['Credit'] > 0: events.append({"title": f" +₹{row['Credit']:,.0f}", "start": row['Date'], "backgroundColor": "#198754"})
            if row['Debit'] > 0: events.append({"title": f" -₹{row['Debit']:,.0f}", "start": row['Date'], "backgroundColor": "#dc3545"})
        
        cal_data = calendar(events=events, options={"headerToolbar": {"left": "prev,next today", "center": "title", "right": "dayGridMonth"}, "initialView": "dayGridMonth"}, key="pnl_calendar")
        
        # തിരുത്തിയ ഭാഗം (callback)
        if cal_data and cal_data.get("callback") == "eventClick":
            event_data = cal_data.get("eventClick", {}).get("event", {})
            dt_click = event_data.get("start", "").split("T")[0]
            if dt_click:
                st.markdown("---"); st.subheader(f"📋 Details for {pd.to_datetime(dt_click).strftime('%d %B %Y')}")
                day_df = df_cal[df_cal['Date'].dt.strftime('%Y-%m-%d') == dt_click].copy()
                if not day_df.empty:
                    day_df['Date'] = day_df['Date'].dt.strftime('%d/%m/%Y')
                    st.dataframe(day_df[['Date', 'Item', 'Debit', 'Credit']], use_container_width=True)

    # --- REPORT & HISTORY ---
    elif (page == "📊 Report" or page == "🔍 History") and not df.empty:
        df_rep = df[(df['Date'].dt.year == 2026) & (df['Date'].dt.month >= 4)].copy()
        df_rep['Month'] = df_rep['Date'].dt.strftime('%B %Y')
        months = df_rep.dropna(subset=['Month']).sort_values(by='Date', ascending=False)['Month'].unique()
        
        if len(months) == 0: st.warning("No data found!")
        else:
            sel_m = st.selectbox("Select Month", months)
            m_df = df_rep[df_rep['Month'] == sel_m].copy()
            m_deb, m_crd = m_df['Debit'].sum(), m_df['Credit'].sum()
            
            if page == "📊 Report":
                st.title("Monthly Expense Analysis")
                c1, c2, c3 = st.columns(3)
                c1.markdown(f'<div class="purple-box"><h3 style="color:#00FF00;">Credit</h3><h1 style="color:#00FF00;">₹{m_crd:,.2f}</h1></div>', unsafe_allow_html=True)
                c2.markdown(f'<div class="purple-box"><h3 style="color:#FF3131;">Expense</h3><h1 style="color:#FF3131;">₹{m_deb:,.2f}</h1></div>', unsafe_allow_html=True)
                c3.markdown(f'<div class="purple-box"><h3 style="color:#FFD700;">Savings</h3><h1 style="color:#FFD700;">₹{m_crd - m_deb:,.2f}</h1></div>', unsafe_allow_html=True)
                
                m_df['Cat'] = m_df['Item'].apply(lambda x: x.split(':')[0] if ':' in str(x) else 'Others')
                st.plotly_chart(px.pie(m_df[m_df['Debit'] > 0], values='Debit', names='Cat', hole=0.4), use_container_width=True)

            clean_df = m_df.drop(columns=['Month'], errors='ignore')
            clean_df['Date'] = clean_df['Date'].dt.strftime('%d/%m/%Y')
            st.dataframe(clean_df.iloc[::-1], use_container_width=True)

    # --- DEBT TRACKER ---
    elif page == "🤝 Debt Tracker":
        st.title("🤝 Debt Tracker")
        st.info("വരും ദിവസങ്ങളിൽ ഇതിലേക്ക് കൂടുതൽ ഫീച്ചറുകൾ വരും!")

    # --- MY AI BUDDY ---
    elif page == "🧠 My AI Buddy":
        st.title("🧠 Your Personal AI Buddy")
        st.write("എന്നോട് എന്തും ചോദിക്കാം. (ഉദാ: 'ഒരു കവിത എഴുതൂ', 'ഇന്ന് എന്ത് പാചകം ചെയ്യണം?')")
        
        if "buddy_messages" not in st.session_state: st.session_state.buddy_messages = []
        
        for msg in st.session_state.buddy_messages:
            with st.chat_message(msg["role"]): st.markdown(msg["content"])
            
        user_input = st.chat_input("Ask me anything...")
        
        if user_input:
            st.session_state.buddy_messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"): st.markdown(user_input)
            
            with st.spinner("ആലോചിക്കുന്നു..."):
                try:
                    client = Groq(api_key=GROQ_API_KEY)
                    system_prompt = "You are a helpful personal AI assistant for a 51-year-old Malayali. Answer their questions in Malayalam in a friendly way. You can help with daily life, cooking, general knowledge, and motivation."
                    
                    messages = [{"role": "system", "content": system_prompt}] + [{"role": m["role"], "content": m["content"]} for m in st.session_state.buddy_messages[-4:]]
                    
                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=messages,
                        max_tokens=500
                    )
                    
                    ai_reply = response.choices[0].message.content
                    st.session_state.buddy_messages.append({"role": "assistant", "content": ai_reply})
                    with st.chat_message("assistant"): st.markdown(ai_reply)
                except Exception as e:
                    st.error(f"Error: {e}")

    # --- AI CHAT (AI Agent) ---
    elif page == "🤖 AI Chat":
        st.title("🤖 AI Agent & Assistant")
        st.write("നിങ്ങൾക്ക് ടൈപ്പ് ചെയ്യാം, അല്ലെങ്കിൽ 'ബിരിയാണി 150' എന്ന് പറഞ്ഞാൽ അത് ഷീറ്റിൽ എൻട്രി ഇടും.")
        
        if "messages" not in st.session_state: st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]): st.markdown(message["content"])

        v_raw = speech_to_text(language='ml', key='ai_voice_input')
        prompt = st.chat_input("Ask anything or add expense...")

        final_prompt = v_raw if v_raw else prompt

        if final_prompt:
            st.session_state.messages.append({"role": "user", "content": final_prompt})
            with st.chat_message("user"): st.markdown(final_prompt)

            with st.spinner("AI ആലോചിക്കുന്നു..."):
                try:
                    client = Groq(api_key=GROQ_API_KEY)
                    utc_now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
                    
                    system_instruction = f"നീ ഒരു ഫിനാൻസ് AI അസിസ്റ്റന്റാണ്. സമയം: {utc_now}. ബാലൻസ്: {bal} Rs. ചെലവ് ചേർക്കാൻ add_new_entry ടൂൾ ഉപയോഗിക്കുക."
                    
                    messages_for_api = [{"role": "system", "content": system_instruction}] + [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-2:]]

                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile", 
                        messages=messages_for_api,
                        tools=tools,
                        tool_choice="auto",
                        max_tokens=500
                    )

                    response_message = response.choices[0].message
                    entry_saved = False
                    
                    if response_message.tool_calls:
                        for tool_call in response_message.tool_calls:
                            if tool_call.function.name == "add_new_entry":
                                args = json.loads(tool_call.function.arguments)
                                result = add_new_entry(
                                    item=args.get("item"), amount=args.get("amount"), 
                                    category=args.get("category", "Others"), type=args.get("type", "Debit")
                                )
                                if "Success" in result:
                                    ai_reply = f"✅ {args.get('item')}-ന് {args.get('amount')} Rs ഞാൻ എൻട്രി ഇട്ടു!"
                                    entry_saved = True
                                else: ai_reply = f"❌ {result}"
                    else:
                        ai_reply = response_message.content

                    st.session_state.messages.append({"role": "assistant", "content": ai_