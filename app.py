import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
import plotly.express as px
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh
from fpdf import FPDF
import re
import urllib.parse
import threading
from streamlit_calendar import calendar
import json
import base64
import os
import cv2
import tempfile
import hashlib
from groq import Groq
from PIL import Image
import io

# --- CONFIG & SETTINGS (നിങ്ങളുടെ ലിങ്കുകൾ) ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"
STOCK_CSV_URL = "YOUR_STOCK_SHEET_CSV_LINK" # നിങ്ങൾക്ക് സ്റ്റോക്ക് ഷീറ്റ് ഉണ്ടെങ്കിൽ കൊടുക്കാം, ഇല്ലെങ്കിൽ Demo കാണിക്കും
STOCK_FORM_API = "YOUR_STOCK_FORM_API"

WA_PHONE, WA_API_KEY = "971551347989", "7463030"
USERS = {"faisal": "faisal147", "shabana": "shabana123", "admin": "paichi786"}

try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except Exception:
    GROQ_API_KEY = ""

VISION_MODEL = "qwen/qwen3.8-27b"
AGENT_MODEL  = "openai/gpt-oss-120b"
WHISPER_MODEL = "whisper-large-v3"

# --- STREAMLIT UI & THEME (Dark Mode) ---
st.set_page_config(page_title="PAICHI MEGA APP v3.0", layout="wide")
st_autorefresh(interval=60000, key="auto_refresh")

st.markdown("""<style>
    .stApp { background: linear-gradient(135deg, #1A0521, #310062, #0D0214); color: #fff; }
    [data-testid="stSidebar"] { background: rgba(0,0,0,0.9) !important; }
    .stButton>button { background-color: #FFD700; color: #000; border-radius: 10px; font-weight: bold; width: 100%; transition: 0.3s; }
    .stButton>button:hover { background-color: #FFF; color: #000; box-shadow: 0px 0px 10px #FFD700; }
    .stDownloadButton>button { background-color: #28a745; color: #ffffff; border-radius: 10px; font-weight: bold; width: 100%;}
    .balance-banner { background: rgba(255, 255, 255, 0.07); padding: 25px; border-radius: 15px; border-left: 10px solid #FFD700; margin-bottom: 25px; text-align: center; box-shadow: 0px 4px 15px rgba(0,0,0,0.3); }
    .purple-box { background: rgba(255, 255, 255, 0.05); padding: 20px; border-radius: 25px; border: 2px solid rgba(255, 215, 0, 0.3); text-align: center; margin-bottom: 20px; }
    .category-box { background: rgba(255, 255, 255, 0.08); padding: 15px; border-radius: 15px; text-align: center; border-bottom: 4px solid #FFD700; margin-bottom: 15px; }
    .alert-banner { background-color: #ff4d4d; color: white; padding: 10px; border-radius: 10px; text-align: center; font-weight: bold; margin-bottom: 20px; }
    h1, h2, h3, p, label { color: white !important; font-weight: bold !important; }
    [data-testid="stChatMessage"] { background-color: #ffffff !important; border-radius: 10px; padding: 15px; border: 1px solid #ccc; color: #000; }
    [data-testid="stChatMessage"] p { color: #000 !important; }
</style>""", unsafe_allow_html=True)

# --- SESSION STATE ---
if 'auth' not in st.session_state: st.session_state.auth, st.session_state.user = False, ""
if 'custom_alert_text' not in st.session_state: st.session_state.custom_alert_text = "Shop kuri book"
if 'low_limit' not in st.session_state: st.session_state.low_limit = 6000
if "messages" not in st.session_state: st.session_state.messages = []
if "audio_counter" not in st.session_state: st.session_state.audio_counter = 0
if "last_audio_hash" not in st.session_state: st.session_state.last_audio_hash = None
if "order_counter" not in st.session_state: st.session_state.order_counter = 0

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
def load_finance_data():
    try:
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
        df.columns = df.columns.str.strip()
        df['Date'] = parse_mixed_dates(df['Date'])
        df['Debit'] = pd.to_numeric(df['Debit'], errors='coerce').fillna(0)
        df['Credit'] = pd.to_numeric(df['Credit'], errors='coerce').fillna(0)
        return df
    except Exception:
        # Demo Data
        return pd.DataFrame({
            'Date': pd.to_datetime(['2026-11-01', '2026-11-02', '2026-11-03']),
            'Item': ['[Faisal] Food: Tea', '[Shabana] Shop: Sugar', '[Admin] Fish: Meen'],
            'Debit': [50, 250, 500],
            'Credit': [0, 0, 0]
        })

@st.cache_data(ttl=10)
def load_stock_data():
    try:
        if not STOCK_CSV_URL or "YOUR_" in STOCK_CSV_URL: raise ValueError("Demo")
        df = pd.read_csv(f"{STOCK_CSV_URL}&r={random.randint(1,999)}")
        df.columns = df.columns.str.strip()
        df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce').fillna(0)
        return df
    except Exception:
        return pd.DataFrame({'Date': ['2026-11-01', '2026-11-02'], 'Item': ['Sugar', 'Milk'], 'Quantity': [50, 20], 'Type': ['Stock In', 'Stock Out']})

def _find_unicode_font():
    candidates = ["/usr/share/fonts/truetype/noto/NotoSansMalayalam-Regular.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "C:/Windows/Fonts/arial.ttf"]
    for p in candidates:
        if os.path.exists(p): return p
    return None

def generate_pdf(df, title, columns):
    pdf = FPDF()
    pdf.add_page()
    font_path = _find_unicode_font()
    has_unicode = False
    if font_path:
        try:
            pdf.add_font("UFont", "", font_path)
            has_unicode = True
        except Exception: has_unicode = False

    pdf.set_font("UFont" if has_unicode else "Helvetica", size=14)
    pdf.cell(190, 10, txt=title, ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("UFont" if has_unicode else "Helvetica", size=10)
    
    col_width = 190 / len(columns)
    for col in columns:
        pdf.cell(col_width, 10, txt=str(col), border=1, align='C')
    pdf.ln()
    pdf.set_font("UFont" if has_unicode else "Helvetica", size=9)

    def _safe(v):
        s = str(v)
        return s if has_unicode else s.encode('ascii', 'ignore').decode('ascii')

    for _, row in df.iterrows():
        for col in columns:
            pdf.cell(col_width, 10, txt=_safe(row[col]), border=1)
        pdf.ln()
    return bytes(pdf.output())

# --- GROQ AI HELPERS ---
def compress_image(image_bytes, max_size=(600, 600)):
    try:
        img = Image.open(io.BytesIO(image_bytes))
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        output = io.BytesIO()
        img.convert('RGB').save(output, format='JPEG', quality=60)
        return output.getvalue()
    except Exception: return image_bytes

def execute_add_finance(item, amount, t_type):
    payload = {
        "entry.1044099436": datetime.now().strftime("%Y-%m-%d"),
        "entry.2013476337": item,
        "entry.1460982454": amount if t_type == "Debit" else 0,
        "entry.1221658767": 0 if t_type == "Debit" else amount
    }
    try: requests.post(FORM_API, data=payload, timeout=10)
    except: pass
    load_finance_data.clear()
    return "Success"

# --- LOGIN ---
if not st.session_state.auth:
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        st.title("🔐 PAICHI MEGA APP LOGIN")
        u, p = st.text_input("Username").lower(), st.text_input("Password", type="password")
        if st.button("LOGIN"):
            if USERS.get(u) == p:
                st.session_state.auth, st.session_state.user = True, u
                st.rerun()
            else: st.error("❌ Access Denied!")

else:
    df = load_finance_data()
    df_stk = load_stock_data()
    t_in, t_out = (df['Credit'].sum(), df['Debit'].sum()) if not df.empty else (0.0, 0.0)
    bal = t_in - t_out

    # --- SIDEBAR SETTINGS ---
    if st.session_state.user != "shabana":
        with st.sidebar.expander("⚙️ Alert & Expense Settings"):
            st.session_state.custom_alert_text = st.text_area("Custom Alert Message", value=st.session_state.custom_alert_text)
            st.session_state.low_limit = st.number_input("Low Balance Limit (₹)", value=st.session_state.low_limit)
    
    # --- ALERT BANNER ---
    if bal < st.session_state.low_limit:
        st.markdown(f'<div class="alert-banner">⚠️ ശ്രദ്ധിക്കുക: അക്കൗണ്ട് ബാലൻസ് കുറവാണ്. {st.session_state.custom_alert_text} (₹{bal:,.2f})!</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="balance-banner"><span style="font-size:20px; color:#E0B0FF;">Available Balance</span><br><span style="font-size:40px; color:#FFD700; font-weight:bold;">₹{bal:,.2f}</span></div>', unsafe_allow_html=True)
    
    # --- MENU ---
    menu = [
        "💰 Smart Add Entry", "📅 Calendar View", "📊 Monthly Report", 
        "🔍 History", "🤝 Debt Tracker", "🧾 Bill Scanner", 
        "🗣️ Voice Order Kiosk", "🛒 Shelf Monitor", "🤖 AI Agent Chat", "🎥 CCTV Vision"
    ]
    if st.session_state.user != "shabana": menu.insert(0, "🏠 Dashboard")
    
    page = st.sidebar.radio("Navigate", menu)
    if st.sidebar.button("Logout"): st.session_state.auth = False; st.rerun()

    # --- 1. DASHBOARD ---
    if page == "🏠 Dashboard" and not df.empty:
        st.title("Financial Overview")
        st.markdown(f'<div class="purple-box"><h2 style="color:#00FF00;">Total Credit: ₹{t_in:,.2f}</h2><h2 style="color:#FF3131;">Total Debit: ₹{t_out:,.2f}</h2></div>', unsafe_allow_html=True)
        
        st.subheader("🗂️ Categorywise Expense Breakdown")
        def extract_cat(x):
            item_text = str(x).lower()
            if any(w in item_text for w in ["food", "ഭക്ഷണം", "ചായ", "ഹോട്ടൽ", "ബിരിയാണി"]): return "Food"
            elif any(w in item_text for w in ["shop", "കട", "സാധനങ്ങൾ"]): return "Shop"
            elif any(w in item_text for w in ["fish", "മീൻ", "ഇറച്ചി"]): return "Fish"
            elif any(w in item_text for w in ["travel", "യാത്ര", "പെട്രോൾ"]): return "Travel"
            return "Others"
        df['Cat'] = df['Item'].apply(extract_cat)
        cats = df[~df['Item'].str.contains('total', case=False, na=False)].groupby('Cat')['Debit'].sum().to_dict()
        
        cols = st.columns(3)
        for idx, (c_name, c_amt) in enumerate(cats.items()):
            if c_amt > 0:
                with cols[idx % 3]: st.markdown(f'<div class="category-box"><span style="font-size:16px; color:#aaa;">Total {c_name}</span><br><span style="font-size:24px; color:#FFF; font-weight:bold;">₹{c_amt:,.2f}</span></div>', unsafe_allow_html=True)

    # --- 2. SMART ADD ENTRY (Voice + Form) ---
    elif page == "💰 Smart Add Entry":
        st.title("Smart Voice Entry 🎙️")
        v_raw = speech_to_text(language='ml', key='voice_v9')
        v_cat, v_amt, v_desc, v_type = "Others", "", "", "Debit"
        
        if v_raw:
            raw = v_raw.lower().replace('.', '').replace(',', '')
            nums = re.findall(r'\d+', raw)
            v_amt = nums[0] if nums else ""
            v_desc = re.sub(r'\d+', '', raw).strip()
            if any(x in raw for x in ["food", "ഭക്ഷണം", "ചായ", "ഹോട്ടൽ"]): v_cat = "Food"
            elif any(x in raw for x in ["shop", "കട", "സാധനങ്ങൾ"]): v_cat = "Shop"
            elif any(x in raw for x in ["fish", "മീൻ", "ഇറച്ചി"]): v_cat = "Fish"
            elif any(x in raw for x in ["travel", "യാത്ര", "പെട്രോൾ"]): v_cat = "Travel"
            elif any(x in raw for x in ["rent", "വാടക"]): v_cat = "Rent"
            if any(x in raw for x in ["കിട്ടി", "വന്നു", "തന്നു", "credit"]): v_type = "Credit"

        with st.form("entry_form", clear_on_submit=True):
            it = st.text_input("Description", value=v_desc)
            am_str = st.text_input("Amount", value=str(v_amt))
            cat = st.selectbox("Category", ["Food", "Shop", "Fish", "Travel", "Rent", "Others"], index=["Food", "Shop", "Fish", "Travel", "Rent", "Others"].index(v_cat))
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True, index=0 if v_type == "Debit" else 1)
            if st.form_submit_button("SAVE & NOTIFY"):
                try:
                    am = float(am_str.strip().replace(',', ''))
                    execute_add_finance(f"[{st.session_state.user.capitalize()}] {cat}: {it}", am, ty)
                    send_whatsapp_auto(f"✅ *Paichi Entry*\n📝 Item: {it}\n💰 Amt: ₹{am}\n👤 User: {st.session_state.user}")
                    st.success("Saved & WhatsApp Sent! ✅"); st.rerun()
                except: st.error("Error! Valid amount required.")

    # --- 3. CALENDAR VIEW ---
    elif page == "📅 Calendar View" and not df.empty:
        st.title("P&L Calendar View 📅")
        df_cal = df.dropna(subset=['Date'])
        summary = df_cal.groupby(df_cal['Date'].dt.strftime('%Y-%m-%d')).agg({'Debit': 'sum', 'Credit': 'sum'}).reset_index()
        events = []
        for _, row in summary.iterrows():
            if row['Credit'] > 0: events.append({"title": f" +₹{row['Credit']:,.0f}", "start": row['Date'], "backgroundColor": "#198754", "borderColor": "#198754", "textColor": "white"})
            if row['Debit'] > 0: events.append({"title": f" -₹{row['Debit']:,.0f}", "start": row['Date'], "backgroundColor": "#dc3545", "borderColor": "#dc3545", "textColor": "white"})
        
        cal_data = calendar(events=events, options={"headerToolbar": {"left": "prev,next today", "center": "title", "right": "dayGridMonth"}, "initialView": "dayGridMonth", "selectable": True}, key="pnl_calendar")
        if cal_data.get("eventClick"):
            dt_click = cal_data["eventClick"]["event"]["start"].split("T")[0]
            st.markdown("---"); st.subheader(f"📋 Details for {pd.to_datetime(dt_click).strftime('%d %B %Y')}")
            day_df = df_cal[df_cal['Date'].dt.strftime('%Y-%m-%d') == dt_click].copy()
            if not day_df.empty:
                day_df['Date'] = day_df['Date'].dt.strftime('%d/%m/%Y')
                st.download_button("📥 Download This Day's Data", day_df[['Date', 'Item', 'Debit', 'Credit']].to_csv(index=False).encode('utf-8'), f"Transactions_{dt_click}.csv", "text/csv")
                st.dataframe(day_df[['Date', 'Item', 'Debit', 'Credit']], use_container_width=True)

    # --- 4. MONTHLY REPORT & 5. HISTORY ---
    elif (page == "📊 Monthly Report" or page == "🔍 History") and not df.empty:
        df_rep = df[(df['Date'].dt.year == 2026) & (df['Date'].dt.month >= 4)].copy()
        df_rep['Month'] = df_rep['Date'].dt.strftime('%B %Y')
        months = df_rep.dropna(subset=['Month']).sort_values(by='Date', ascending=False)['Month'].unique()
        
        if len(months) == 0: st.warning("No data found from April 2026 onwards!")
        else:
            sel_m = st.selectbox("Select Month", months)
            m_df = df_rep[df_rep['Month'] == sel_m].copy()
            
            search_query = st.text_input("🔍 Search items...", "").strip().lower()
            filter_type = st.selectbox("Filter Type", ["All", "Debit Only", "Credit Only"])
            if search_query: m_df = m_df[m_df['Item'].str.lower().str.contains(search_query, na=False)]
            if filter_type == "Debit Only": m_df = m_df[m_df['Debit'] > 0]
            elif filter_type == "Credit Only": m_df = m_df[m_df['Credit'] > 0]

            m_deb, m_crd = m_df['Debit'].sum(), m_df['Credit'].sum()
            
            if page == "📊 Monthly Report":
                st.title("Monthly Expense Analysis")
                c1, c2, c3 = st.columns(3)
                c1.markdown(f'<div class="purple-box"><h3 style="color:#00FF00;">Total Credit</h3><h1 style="color:#00FF00;">₹{m_crd:,.2f}</h1></div>', unsafe_allow_html=True)
                c2.markdown(f'<div class="purple-box"><h3 style="color:#FF3131;">Total Expense</h3><h1 style="color:#FF3131;">₹{m_deb:,.2f}</h1></div>', unsafe_allow_html=True)
                c3.markdown(f'<div class="purple-box"><h3 style="color:#FFD700;">Net Savings</h3><h1 style="color:#FFD700;">₹{m_crd - m_deb:,.2f}</h1></div>', unsafe_allow_html=True)
                
                if m_deb > 0:
                    m_df['Cat'] = m_df['Item'].apply(lambda x: x.split(':')[0] if ':' in str(x) else 'Others')
                    st.plotly_chart(px.pie(m_df[m_df['Debit'] > 0], values='Debit', names='Cat', hole=0.4, title=f"{sel_m} Expense Split").update_traces(textposition='inside', textinfo='percent+label'), use_container_width=True)

            clean_df = m_df.drop(columns=['Month'], errors='ignore')
            pdf_df = clean_df.copy()
            pdf_df['Date'] = pdf_df['Date'].dt.strftime('%d/%m/%Y')
            csv_bytes = clean_df.to_csv(index=False).encode('utf-8')
            
            if page == "📊 Monthly Report":
                st.download_button("📥 Download Excel/CSV Report", csv_bytes, f"Report_{sel_m.replace(' ', '_')}.csv", "text/csv")
            else:
                st.title("Transaction History")
                col_p, col_c = st.columns(2)
                pdf_b = generate_pdf(pdf_df, f"History: {sel_m}", ['Date', 'Item', 'Debit', 'Credit'])
                if pdf_b: col_p.download_button(f"📄 Download PDF", pdf_b, f"History_{sel_m.replace(' ', '_')}.pdf", "application/pdf")
                col_c.download_button("📥 Download CSV (Excel)", csv_bytes, f"History_{sel_m.replace(' ', '_')}.csv", "text/csv")
            
            clean_df['Date'] = clean_df['Date'].dt.strftime('%d/%m/%Y')
            st.dataframe(clean_df.iloc[::-1], use_container_width=True)

    # --- 6. DEBT TRACKER ---
    elif page == "🤝 Debt Tracker":
        st.title("🤝 Debt Tracker & Summary")
        st.info("ഇവിടെ നിങ്ങളുടെ കടം വാങ്ങിയതും നൽകിയതുമായ വിവരങ്ങൾ കാണാം. (Coming Soon)")

    # --- 7. BILL SCANNER (AI) ---
    elif page == "🧾 Bill Scanner":
        st.title("🧾 Bill / Stock Photo Scanner")
        bill_file = st.file_uploader("Upload Bill Photo", type=["jpg", "jpeg", "png"])
        if bill_file and GROQ_API_KEY:
            st.image(bill_file, caption="Uploaded Bill", use_container_width=True)
            if st.button("🔍 വായിച്ച് എൻട്രി ഇടുക"):
                with st.spinner("AI ബിൽ വായിക്കുന്നു..."):
                    try:
                        client = Groq(api_key=GROQ_API_KEY)
                        b64_img = base64.b64encode(compress_image(bill_file.getvalue())).decode('utf-8')
                        prompt = "Extract item name, quantity, and total price. Return ONLY JSON array: [{\"item\": \"Sugar\", \"qty\": 5, \"price\": 250}]"
                        response = client.chat.completions.create(model=VISION_MODEL, messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}}]}])
                        res_text = response.choices[0].message.content.strip()
                        if res_text.startswith("```json"): res_text = res_text[7:-3]
                        items = json.loads(res_text)
                        for item in items:
                            execute_add_finance(f"[Purchase] {item['item']}", item['price'], "Debit")
                        st.success("🎉 എല്ലാം എൻട്രി ഇട്ടു!"); st.rerun()
                    except Exception as e: st.error(f"Error: {e}")

    # --- 8. VOICE ORDER KIOSK ---
    elif page == "🗣️ Voice Order Kiosk":
        st.title("🗣️ AI Voice Order Kiosk")
        audio_order = st.audio_input("🎤 ഓർഡർ റെക്കോർഡ് ചെയ്യാൻ ഇവിടെ അമർത്തുക", key=f"order_{st.session_state.order_counter}")
        if audio_order and GROQ_API_KEY:
            with st.spinner("AI കേൾക്കുന്നു..."):
                try:
                    client = Groq(api_key=GROQ_API_KEY)
                    trans = client.audio.transcriptions.create(file=(audio_order.name, audio_order.getvalue()), model=WHISPER_MODEL, response_format="text")
                    st.info(f"🗣️ പറഞ്ഞത്: **{trans}**")
                    prompt = f"Extract items from: '{trans}'. Return ONLY JSON array: [{\"item\": \"Sugar\", \"qty\": 2}]"
                    res = client.chat.completions.create(model=AGENT_MODEL, messages=[{"role": "user", "content": prompt}]).choices[0].message.content
                    if res.startswith("```json"): res = res[7:-3]
                    order_data = json.loads(res)
                    st.dataframe(pd.DataFrame(order_data), use_container_width=True)
                    if st.button("✅ അടുത്തത്"): st.session_state.order_counter += 1; st.rerun()
                except Exception as e: st.error(f"Error: {e}")

    # --- 9. SHELF MONITOR ---
    elif page == "🛒 Shelf Monitor":
        st.title("🛒 Smart Shelf Monitor")
        c1, c2 = st.columns(2)
        m_file = c1.file_uploader("Morning Photo", type=["jpg", "png"])
        e_file = c2.file_uploader("Evening Photo", type=["jpg", "png"])
        if m_file and e_file and GROQ_API_KEY:
            if st.button("🔍 താരതമ്യം ചെയ്യുക"):
                with st.spinner("AI പരിശോധിക്കുന്നു..."):
                    try:
                        client = Groq(api_key=GROQ_API_KEY)
                        b64_m = base64.b64encode(compress_image(m_file.getvalue())).decode('utf-8')
                        b64_e = base64.b64encode(compress_image(e_file.getvalue())).decode('utf-8')
                        prompt = "Compare these shelf images (Morning vs Evening). If identical, say 'No changes'. If different, list what reduced."
                        res = client.chat.completions.create(model=VISION_MODEL, messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_m}"}}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_e}"}}]}]).choices[0].message.content
                        st.success(res)
                    except Exception as e: st.error(f"Error: {e}")

    # --- 10. AI AGENT CHAT ---
    elif page == "🤖 AI Agent Chat":
        st.title("🤖 PAICHI AI Chat")
        if st.button("🗑️ Clear Chat"): st.session_state.messages = []; st.session_state['audio_counter'] += 1; st.rerun()
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]): st.markdown(msg["content"])
        
        audio_val = st.audio_input("🎤 റെക്കോർഡ് ചെയ്യാൻ അമർത്തുക", key=f"ai_audio_{st.session_state['audio_counter']}")
        text_prompt = st.chat_input("ഇവിടെ ടൈപ്പ് ചെയ്യാം...")
        prompt = text_prompt
        
        if audio_val and GROQ_API_KEY:
            if st.session_state.get("last_audio_hash") != hashlib.md5(audio_val.getvalue()).hexdigest():
                st.session_state["last_audio_hash"] = hashlib.md5(audio_val.getvalue()).hexdigest()
                try:
                    client = Groq(api_key=GROQ_API_KEY)
                    prompt = client.audio.transcriptions.create(file=(audio_val.name, audio_val.getvalue()), model=WHISPER_MODEL).text
                    st.info(f"🗣️ {prompt}")
                except: pass

        if prompt and GROQ_API_KEY:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            with st.spinner("AI ടൈപ്പ് ചെയ്യുന്നു..."):
                try:
                    client = Groq(api_key=GROQ_API_KEY)
                    res = client.chat.completions.create(model=AGENT_MODEL, messages=[{"role": "system", "content": f"നീ ഒരു ബിസിനസ്സ് AI ആണ്. മലയാളത്തിൽ മറുപടി നൽകുക."}] + [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-4:]]).choices[0].message.content
                    st.session_state.messages.append({"role": "assistant", "content": res})
                    with st.chat_message("assistant"): st.markdown(res)
                    st.session_state['audio_counter'] += 1; st.rerun()
                except Exception as e: st.error(f"Error: {e}")

    # --- 11. CCTV VISION ---
    elif page == "🎥 CCTV Vision":
        st.title("🎥 CCTV AI Vision")
        file = st.file_uploader("Upload Photo/Video", type=["jpg", "png", "mp4"])
        if file and GROQ_API_KEY:
            if st.button("🔍 Analyze with AI"):
                with st.spinner("AI നോക്കുന്നു..."):
                    try:
                        client = Groq(api_key=GROQ_API_KEY)
                        if "image" in file.type:
                            imgs = [base64.b64encode(compress_image(file.getvalue())).decode('utf-8')]
                        else:
                            # Note: Simplified video processing for space
                            imgs = [] 
                            st.warning("Video processing requires OpenCV frames extraction.")
                        
                        if imgs:
                            res = client.chat.completions.create(model=VISION_MODEL, messages=[{"role": "user", "content": [{"type": "text", "text": "Analyze this shop CCTV. Count people and stock."}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{imgs[0]}"}}]}]).choices[0].message.content
                            st.success(res)
                    except Exception as e: st.error(f"Error: {e}")