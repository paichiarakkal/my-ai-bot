import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
import plotly.express as px
from fpdf import FPDF
import json
import base64
import os
import cv2
import tempfile
import hashlib
import imaplib
import email
import time
from email.header import decode_header
from groq import Groq
from twilio.rest import Client

# --- CONFIG (നിങ്ങളുടെ ലിങ്കുകൾ ഇവിടെ ചേർക്കുക) ---
CSV_URL = "YOUR_FINANCE_SHEET_CSV_LINK"
FORM_API = "YOUR_FINANCE_FORM_API"
STOCK_CSV_URL = "YOUR_STOCK_SHEET_CSV_LINK"
STOCK_FORM_API = "YOUR_STOCK_FORM_API"

USER_PINS = {"admin": "1234", "shop1": "1111"}

try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except Exception:
    GROQ_API_KEY = ""

GMAIL_USER = st.secrets.get("GMAIL_USER", "")
GMAIL_APP_PASSWORD = st.secrets.get("GMAIL_APP_PASSWORD", "")

# --- TWILIO CONFIG (Secrets-ൽ നിന്ന് എടുക്കുന്നു) ---
try:
    TWILIO_SID = st.secrets["TWILIO_SID"]
    TWILIO_AUTH_TOKEN = st.secrets["TWILIO_AUTH_TOKEN"]
    TWILIO_FROM = st.secrets.get("TWILIO_FROM", "whatsapp:+14155238886")
except Exception:
    TWILIO_SID = ""
    TWILIO_AUTH_TOKEN = ""
    TWILIO_FROM = "whatsapp:+14155238886"

VISION_MODEL = "qwen/qwen3.8-27b"
AGENT_MODEL  = "openai/gpt-oss-120b"
WHISPER_MODEL = "whisper-large-v3"

# --- SAFE FORM SUBMIT ---
def submit_form(api_url, payload):
    if not api_url or "YOUR_" in api_url:
        return True  
    try:
        r = requests.post(api_url, data=payload, timeout=10)
        return r.status_code == 200
    except Exception as e:
        st.error(f"❌ Submission failed: {e}")
        return False

# --- WHATSAPP SENDER ---
def send_whatsapp_custom(to_number, msg):
    if not TWILIO_SID or not TWILIO_AUTH_TOKEN: return False
    try:
        client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
        client.messages.create(body=msg, from_=TWILIO_FROM, to=to_number)
        return True
    except Exception as e:
        print(f"Twilio Error: {e}")
        return False

# --- STREAMLIT UI SETUP ---
st.set_page_config(page_title="PAICHI BUSINESS", layout="wide")

st.markdown("""
    <style>
    .stApp { background: #f4f6f9; color: #000000; }
    [data-testid="stSidebar"] { background: #e0e0e0 !important; }
    .stButton>button { background-color: #007BFF; color: #ffffff; border-radius: 10px; font-weight: bold; }
    .stDownloadButton>button { background-color: #28a745; color: #ffffff; border-radius: 10px; font-weight: bold; }
    .banner { background: #ffffff; padding: 25px; border-radius: 15px; border-left: 10px solid #007BFF; text-align: center; margin-bottom: 25px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
    h1, h2, h3, p, label, span { color: #000000 !important; font-weight: bold !important; }
    [data-testid="stChatMessage"] { background-color: #ffffff !important; border-radius: 10px; padding: 15px; border: 1px solid #ccc; color: #000; }
    .banner .b-label { color: #007BFF !important; font-size: 20px; }
    .banner .b-value { color: #000000 !important; font-size: 40px; }
    </style>
""", unsafe_allow_html=True)

if 'auth' not in st.session_state:
    st.session_state.auth, st.session_state.user = False, ""
if "messages" not in st.session_state:
    st.session_state.messages = []
if "audio_counter" not in st.session_state:
    st.session_state.audio_counter = 0
if "last_audio_hash" not in st.session_state:
    st.session_state.last_audio_hash = None
if "wa_message" not in st.session_state:
    st.session_state.wa_message = ""

def flash_success(msg):
    st.session_state["_flash"] = msg

def show_flash():
    msg = st.session_state.pop("_flash", None)
    if msg:
        st.success(msg)

# --- HELPER: Safe CSV load ---
def _append_cache_buster(url):
    if not url or "YOUR_" in url:
        raise ValueError("placeholder")
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}r={random.randint(1,999)}"

@st.cache_data(ttl=5)
def load_finance_data():
    try:
        df = pd.read_csv(_append_cache_buster(CSV_URL))
        df.columns = df.columns.str.strip()
        df['Debit'] = pd.to_numeric(df['Debit'], errors='coerce').fillna(0)
        df['Credit'] = pd.to_numeric(df['Credit'], errors='coerce').fillna(0)
        return df
    except Exception:
        return pd.DataFrame(columns=['Date', 'Shop Name', 'Item', 'Debit', 'Credit'])

@st.cache_data(ttl=5)
def load_stock_data():
    try:
        df = pd.read_csv(_append_cache_buster(STOCK_CSV_URL))
        df.columns = df.columns.str.strip()
        df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce').fillna(0)
        return df
    except Exception:
        return pd.DataFrame(columns=['Date', 'Item', 'Quantity', 'Type'])

# PDF Helper
def _find_unicode_font():
    candidates = ["/usr/share/fonts/truetype/noto/NotoSansMalayalam-Regular.ttf", "C:/Windows/Fonts/arial.ttf"]
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
        except: pass

    pdf.set_font("UFont" if has_unicode else "Helvetica", size=14)
    pdf.cell(190, 10, txt=title, ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("UFont" if has_unicode else "Helvetica", size=10)
    col_width = 190 / len(columns)
    for col in columns: pdf.cell(col_width, 10, txt=str(col), border=1, align='C')
    pdf.ln()
    pdf.set_font("UFont" if has_unicode else "Helvetica", size=9)
    
    def _safe(v):
        s = str(v)
        return s if has_unicode else s.encode('ascii', 'ignore').decode('ascii')
    for _, row in df.iterrows():
        for col in columns: pdf.cell(col_width, 10, txt=_safe(row[col]), border=1)
        pdf.ln()
    return bytes(pdf.output())


# ============================================
# 🤖 AI AGENT TOOLS & FUNCTIONS
# ============================================
tools = [
    {"type": "function", "function": {"name": "add_finance", "description": "Add finance", "parameters": {"type": "object", "properties": {"shop": {"type": "string", "enum": ["Shop 1", "Shop 2"]}, "item": {"type": "string"}, "amount": {"type": "number"}, "type": {"type": "string", "enum": ["Debit", "Credit"]}}, "required": ["shop", "item", "amount", "type"]}}},
    {"type": "function", "function": {"name": "add_stock", "description": "Add stock", "parameters": {"type": "object", "properties": {"item_name": {"type": "string"}, "qty": {"type": "number"}, "stock_type": {"type": "string", "enum": ["Stock In", "Stock Out"]}}, "required": ["item_name", "qty", "stock_type"]}}},
    {"type": "function", "function": {"name": "check_gmail", "description": "Read emails", "parameters": {"type": "object", "properties": {"count": {"type": "number"}}, "required": ["count"]}}}
]

def execute_add_finance(shop, item, amount, t_type):
    payload = {"entry.1044099436": datetime.now().strftime("%Y-%m-%d"), "entry.2013476337": f"[{shop}] {item}", "entry.1460982454": amount if t_type == "Debit" else 0, "entry.1221658767": 0 if t_type == "Debit" else amount}
    if submit_form(FORM_API, payload): load_finance_data.clear(); return "Success"
    return "Failed"

def execute_add_stock(item_name, qty, stock_type):
    payload = {"entry.1044099436": datetime.now().strftime("%Y-%m-%d"), "entry.2013476337": item_name, "entry.1460982454": qty, "entry.1221658767": stock_type}
    if submit_form(STOCK_FORM_API, payload): load_stock_data.clear(); return "Success"
    return "Failed"

def check_gmail_emails(count=3):
    if not GMAIL_USER or not GMAIL_APP_PASSWORD: return "Gmail App Password ഇല്ല."
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        mail.select("inbox")
        status, messages = mail.search(None, "ALL")
        mail_ids = messages[0].split()
        if not mail_ids: return "മെയിലുകൾ ഇല്ല."
        
        latest_ids = mail_ids[-int(count):]
        email_list = []
        for i in reversed(latest_ids):
            res, msg = mail.fetch(i, "(RFC822)")
            for response in msg:
                if isinstance(response, tuple):
                    msg = email.message_from_bytes(response[1])
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes): subject = subject.decode(encoding if encoding else "utf-8")
                    from_ = msg.get("From")
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                try: body = part.get_payload(decode=True).decode()
                                except: pass
                                break
                    else:
                        try: body = msg.get_payload(decode=True).decode()
                        except: pass
                    email_list.append(f"From: {from_}\nSubject: {subject}\nBody: {body[:800]}...\n")
        mail.logout()
        return "\n---\n".join(email_list)
    except Exception as e: return f"Gmail Error: {str(e)}"

def extract_frames_from_video(video_bytes, num_frames=3):
    try:
        tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        tfile.write(video_bytes); tfile.close()
        cap = cv2.VideoCapture(tfile.name)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frames = []
        if total_frames > 0:
            step = max(1, total_frames // num_frames)
            for i in range(0, total_frames, step):
                cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                ret, frame = cap.read()
                if ret:
                    _, buffer = cv2.imencode('.jpg', frame)
                    frames.append(buffer.tobytes())
                if len(frames) >= num_frames: break
        cap.release(); os.unlink(tfile.name)
        return frames
    except: return []

def analyze_images_with_groq(images_bytes_list):
    if not GROQ_API_KEY: return False, "Groq Key missing!"
    try:
        client = Groq(api_key=GROQ_API_KEY)
        content_list = [{"type": "text", "text": "Analyze these CCTV frames. Count people, stock. Provide report."}]
        for img in images_bytes_list:
            content_list.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64.b64encode(img).decode('utf-8')}"}})
        res = client.chat.completions.create(model=VISION_MODEL, messages=[{"role": "user", "content": content_list}], max_tokens=800).choices[0].message.content
        prompt_ml = f"Translate into Malayalam. Do NOT translate brand names.\n\n{res}"
        return True, client.chat.completions.create(model=AGENT_MODEL, messages=[{"role": "user", "content": prompt_ml}], max_tokens=800).choices[0].message.content
    except Exception as e: return False, f"Vision Error: {str(e)}"

def _parse_employee(item_str):
    try:
        if ':' not in item_str: return "Unknown"
        return item_str.split(':', 1)[1].split('(')[0].strip() or "Unknown"
    except: return "Unknown"

def process_ai_agent(prompt_text):
    client = Groq(api_key=GROQ_API_KEY)
    system_instruction = f"നീ ഒരു ബിസിനസ്സ് AI ആണ്. ബാലൻസ്: ₹{st.session_state.get('current_bal', 0):,.2f}. മലയാളത്തിൽ മറുപടി നൽകുക."
    messages = [{"role": "system", "content": system_instruction}] + [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-4:]] + [{"role": "user", "content": prompt_text}]
    
    response = client.chat.completions.create(model=AGENT_MODEL, messages=messages, tools=tools, tool_choice="auto")
    msg = response.choices[0].message
    tool_used = False
    
    if msg.tool_calls:
        tool_used = True
        replies = []
        for tc in msg.tool_calls:
            try: args = json.loads(tc.function.arguments)
            except: continue
            
            if tc.function.name == "add_finance":
                res = execute_add_finance(args["shop"], args["item"], args["amount"], args["type"])
                replies.append(f"✅ {args['shop']}-ൽ '{args['item']}' എൻട്രി ഇട്ടു!" if res == "Success" else "❌ എൻട്രി പറ്റിയില്ല.")
            elif tc.function.name == "add_stock":
                res = execute_add_stock(args["item_name"], args["qty"], args["stock_type"])
                replies.append(f"✅ {args['item_name']} സ്റ്റോക്ക് അപ്ഡേറ്റ് ചെയ്തു!" if res == "Success" else "❌ സ്റ്റോക്ക് പറ്റിയില്ല.")
            elif tc.function.name == "check_gmail":
                raw = check_gmail_emails(args.get("count", 3))
                summary = client.chat.completions.create(model=AGENT_MODEL, messages=[{"role": "user", "content": f"ചുരുക്കി മലയാളത്തിൽ എഴുതുക:\n{raw}"}], max_tokens=800).choices[0].message.content
                replies.append(f"📧 **ഇമെയിൽ സംഗ്രഹം:**\n\n{summary}")
        ai_reply = "\n\n".join(replies)
    else:
        ai_reply = msg.content or ""
    return ai_reply, tool_used


# --- 🔒 LOGIN ---
if not st.session_state.auth:
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        st.subheader("🔐 PAICHI BUSINESS LOGIN")
        u = st.selectbox("👤 Select Role", ["admin", "shop1"]).lower()
        pin = st.text_input("🔑 Enter PIN", type="password", max_chars=4)
        if st.button("LOGIN"):
            if USER_PINS.get(u) == pin:
                st.session_state.auth, st.session_state.user = True, u; st.rerun()
            else: st.error("❌ Incorrect PIN!")

else:
    st.sidebar.title(f"👋 Welcome, {st.session_state.user.capitalize()}")
    
    menu = ["📊 Dashboard", "💰 Add Finance", "📦 Stock Management", "🧾 Bill Scanner", "📧 Email Replier", "📢 WhatsApp Marketing", "👨‍💼 Staff Salary", "🤖 AI Agent", "🎥 CCTV AI Vision"]
    page = st.sidebar.radio("Menu", menu)

    if st.sidebar.button("Logout"):
        st.session_state.auth = False; st.session_state.messages = []; st.rerun()

    df_fin = load_finance_data()
    df_stk = load_stock_data()
    bal = (df_fin['Credit'].sum() - df_fin['Debit'].sum()) if not df_fin.empty else 0
    st.session_state['current_bal'] = bal

    # --- 1. DASHBOARD ---
    if page == "📊 Dashboard":
        st.markdown(f'<div class="banner"><span class="b-label">Total Business Balance</span><br><span class="b-value">₹{bal:,.2f}</span></div>', unsafe_allow_html=True)
        if not df_fin.empty:
            shop_data = df_fin.groupby('Shop Name')[['Credit', 'Debit']].sum().reset_index()
            st.plotly_chart(px.bar(shop_data, x='Shop Name', y=['Credit', 'Debit'], barmode='group', color_discrete_sequence=['#00FF00', '#FF3131']), use_container_width=True)
            st.dataframe(df_fin.tail(10).iloc[::-1], use_container_width=True)

    # --- 2. ADD FINANCE ---
    elif page == "💰 Add Finance":
        st.title("💰 Finance Entry")
        show_flash()
        with st.form("finance_form", clear_on_submit=True):
            shop = st.selectbox("Select Shop", ["Shop 1", "Shop 2"])
            it = st.text_input("Description"); am_str = st.text_input("Amount")
            ty = st.radio("Type", ["Debit (Expense)", "Credit (Sales)"], horizontal=True)
            if st.form_submit_button("SAVE ENTRY"):
                try:
                    am = float(am_str.strip().replace(',', ''))
                    if execute_add_finance(shop, it, am, "Debit" if "Debit" in ty else "Credit") == "Success":
                        flash_success("Saved! ✅"); st.rerun()
                except: st.error("❗ Invalid amount.")

    # --- 3. STOCK MANAGEMENT ---
    elif page == "📦 Stock Management":
        st.title("📦 Stock & Inventory")
        show_flash()
        tab1, tab2, tab3 = st.tabs(["📊 Current Stock", "➕ Add Entry", "📄 Item History"])
        with tab1:
            if not df_stk.empty:
                s = df_stk.copy()
                s['In']  = s.apply(lambda x: x['Quantity'] if x['Type'] == 'Stock In'  else 0, axis=1)
                s['Out'] = s.apply(lambda x: x['Quantity'] if x['Type'] == 'Stock Out' else 0, axis=1)
                final_stk = s.groupby('Item')[['In', 'Out']].sum().reset_index()
                final_stk['Available'] = final_stk['In'] - final_stk['Out']
                st.dataframe(final_stk[['Item', 'Available']], use_container_width=True)
        with tab2:
            with st.form("stock_form", clear_on_submit=True):
                item_name  = st.text_input("Item Name"); qty = st.number_input("Quantity", min_value=1.0)
                stock_type = st.radio("Type", ["Stock In", "Stock Out"], horizontal=True)
                if st.form_submit_button("SAVE STOCK"):
                    if execute_add_stock(item_name, qty, stock_type) == "Success":
                        flash_success("Stock Updated! ✅"); st.rerun()

    # --- 4. BILL SCANNER ---
    elif page == "🧾 Bill Scanner":
        st.title("🧾 Bill Scanner")
        bill_file = st.file_uploader("Upload Bill Photo", type=["jpg", "jpeg", "png"])
        if bill_file is not None:
            st.image(bill_file, caption="Uploaded Bill", use_container_width=True)
            if st.button("🔍 Extract & Add"):
                with st.spinner("AI ബിൽ വായിക്കുന്നു..."):
                    try:
                        client = Groq(api_key=GROQ_API_KEY)
                        b64_img = base64.b64encode(bill_file.getvalue()).decode('utf-8')
                        prompt = "Extract item name, quantity, and total price. Return ONLY JSON array: [{\"item\": \"Sugar\", \"qty\": 5, \"price\": 250}]"
                        response = client.chat.completions.create(model=VISION_MODEL, messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}}]}], max_tokens=1000)
                        res_text = response.choices[0].message.content.strip()
                        if res_text.startswith("```json"): res_text = res_text[7:-3]
                        items_data = json.loads(res_text)
                        for item in items_data:
                            execute_add_stock(item['item'], item['qty'], "Stock In")
                            execute_add_finance("Shop 1", f"Purchase: {item['item']}", item['price'], "Debit")
                        st.success("🎉 എൻട്രി ഇട്ടു!"); st.rerun()
                    except Exception as e: st.error(f"Error: {e}")

    # --- 5. EMAIL REPLIER ---
    elif page == "📧 Email Replier":
        st.title("📧 Smart Email Replier")
        if st.button("🔄 പുതിയ മെയിലുകൾ ചെക്ക് ചെയ്യുക"):
            with st.spinner("AI മെയിലുകൾ വായിക്കുന്നു..."):
                raw_emails = check_gmail_emails(1)
                if "Error" in raw_emails or "ഇല്ല" in raw_emails: st.warning(raw_emails)
                else:
                    st.info("📥 **ഏറ്റവും പുതിയ മെയിൽ:**"); st.text_area("Email", raw_emails, height=200, disabled=True)
                    client = Groq(api_key=GROQ_API_KEY)
                    prompt = f"ഈ മെയിൽ പ്രധാനപ്പെട്ടതാണോ എന്ന് പറയുക. പ്രധാനമാണെങ്കിൽ ഒരു പ്രൊഫഷണൽ റിപ്ലൈ തയ്യാറാക്കുക.\n\n{raw_emails}"
                    with st.spinner("AI റിപ്ലൈ തയ്യാറാക്കുന്നു..."):
                        reply_res = client.chat.completions.create(model=AGENT_MODEL, messages=[{"role": "user", "content": prompt}], max_tokens=800).choices[0].message.content
                        st.success("✅ AI വിശകലനവും റിപ്ലൈയും:"); st.markdown(reply_res)

    # --- 6. WHATSAPP MARKETING (പുതിയ ഫീച്ചർ) ---
    elif page == "📢 WhatsApp Marketing":
        st.title("📢 Customer WhatsApp Marketing")
        st.write("കസ്റ്റമർമാർക്ക് ഓഫറുകളും മറ്റു വിവരങ്ങളും വാട്ട്‌സ്ആപ്പിൽ അയക്കാം.")

        st.subheader("1. മെസ്സേജ് തയ്യാറാക്കുക")
        ai_prompt = st.text_input("AI-യോട് മെസ്സേജ് എഴുതാൻ പറയാം (ഉദാ: 'ഓണം ഓഫർ 10%')")
        if st.button("🤖 AI മെസ്സേജ് ഉണ്ടാക്കുക") and ai_prompt:
            with st.spinner("AI മെസ്സേജ് തയ്യാറാക്കുന്നു..."):
                try:
                    client = Groq(api_key=GROQ_API_KEY)
                    prompt = f"ഇതിനെ അടിസ്ഥാനമാക്കി ഒരു കിടിലൻ വാട്ട്സ്ആപ്പ് മാർക്കറ്റിംഗ് മെസ്സേജ് മലയാളത്തിൽ എഴുതുക. കൂടുതൽ ഇമോജികൾ ഉപയോഗിക്കുക: '{ai_prompt}'"
                    res = client.chat.completions.create(model=AGENT_MODEL, messages=[{"role": "user", "content": prompt}]).choices[0].message.content
                    st.session_state['wa_message'] = res
                except: st.error("AI എറർ!")
        
        msg_to_send = st.text_area("മെസ്സേജ്", value=st.session_state.get('wa_message', ''), height=150)

        st.subheader("2. കസ്റ്റമർ നമ്പറുകൾ")
        st.write("Twilio Sandbox-ൽ ജോയിൻ ചെയ്ത നമ്പറുകൾ മാത്രമേ ഇപ്പോൾ വർക്ക് ചെയ്യൂ.")
        numbers_input = st.text_area("ഫോൺ നമ്പറുകൾ (കോമ ഉപയോഗിച്ച് വേർതിരിക്കുക)", placeholder="+971501234567, +919876543210")
        numbers_list = [num.strip() for num in numbers_input.split(",") if num.strip()]

        if st.button("🚀 മെസ്സേജ് അയക്കുക"):
            if not msg_to_send: st.error("ദയവായി മെസ്സേജ് നൽകുക.")
            elif not numbers_list: st.error("ദയവായി ഒരു നമ്പറെങ്കിലും നൽകുക.")
            elif not TWILIO_SID: st.error("Twilio Config ലഭ്യമല്ല.")
            else:
                success_count = 0
                for num in numbers_list:
                    formatted_num = f"whatsapp:{num}" if not num.startswith("whatsapp:") else num
                    if send_whatsapp_custom(formatted_num, msg_to_send):
                        success_count += 1
                    time.sleep(1) 
                st.success(f"✅ {success_count} കസ്റ്റമർമാർക്ക് മെസ്സേജ് അയച്ചു!")

    # --- 7. STAFF SALARY ---
    elif page == "👨‍💼 Staff Salary":
        st.title("👨‍💼 Staff Salary Management")
        show_flash()
        with st.form("salary_form", clear_on_submit=True):
            shop = st.selectbox("Select Shop", ["Shop 1", "Shop 2"])
            emp_name = st.text_input("Employee Name"); sal_amt = st.number_input("Salary Amount", min_value=1.0)
            if st.form_submit_button("PAY SALARY"):
                if execute_add_finance(shop, f"Salary: {emp_name}", sal_amt, "Debit") == "Success":
                    flash_success(f"✅ {emp_name}-ന്റെ ശമ്പളം നൽകി!"); st.rerun()

    # --- 8. AI AGENT ---
    elif page == "🤖 AI Agent":
        st.title("🤖 PAICHI Business AI")
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("🗑️ Clear Chat"): st.session_state.messages = []; st.session_state['audio_counter'] += 1; st.rerun()

        for message in st.session_state.messages:
            with st.chat_message(message["role"]): st.markdown(message["content"])

        audio_value = st.audio_input("🎤 റെക്കോർഡ് ചെയ്യാൻ അമർത്തുക", key=f"audio_{st.session_state['audio_counter']}")
        text_prompt = st.chat_input("ഇവിടെ ടൈപ്പ് ചെയ്യാം...")
        prompt = None

        if audio_value:
            if st.session_state.get("last_audio_hash") != hashlib.md5(audio_value.getvalue()).hexdigest():
                st.session_state["last_audio_hash"] = hashlib.md5(audio_value.getvalue()).hexdigest()
                with st.spinner("ശബ്ദം കേൾക്കുന്നു..."):
                    try:
                        client = Groq(api_key=GROQ_API_KEY)
                        prompt = client.audio.transcriptions.create(file=(audio_value.name, audio_value.getvalue()), model=WHISPER_MODEL, response_format="text").strip()
                    except Exception as e: st.error(f"Audio Error: {str(e)}")

        if text_prompt: prompt = text_prompt

        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            with st.spinner("AI ടൈപ്പ് ചെയ്യുന്നു..."):
                try:
                    ai_reply, tool_used = process_ai_agent(prompt)
                    st.session_state.messages.append({"role": "assistant", "content": ai_reply})
                    with st.chat_message("assistant"): st.markdown(ai_reply)
                    st.session_state['audio_counter'] += 1; st.rerun()
                except Exception as e: st.error(f"AI Error: {str(e)}")

    # --- 9. CCTV AI VISION ---
    elif page == "🎥 CCTV AI Vision":
        st.title("🎥 CCTV AI Vision")
        uploaded_file = st.file_uploader("Upload Shop CCTV Photo or Video", type=["jpg", "jpeg", "png", "mp4"])
        if uploaded_file is not None:
            if "image" in uploaded_file.type:
                st.image(uploaded_file, use_container_width=True)
                images_to_analyze = [uploaded_file.getvalue()]
            else:
                st.video(uploaded_file)
                with st.spinner("ഫ്രെയിമുകൾ എടുക്കുന്നു..."):
                    images_to_analyze = extract_frames_from_video(uploaded_file.getvalue())
                    if not images_to_analyze: st.error("ഫ്രെയിമുകൾ എടുക്കാൻ സാധിച്ചില്ല."); st.stop()

            if st.button("🔍 Analyze with AI"):
                with st.spinner("AI വിശകലനം ചെയ്യുന്നു..."):
                    ok, analysis_result = analyze_images_with_groq(images_to_analyze)
                    if ok: st.success(analysis_result)
                    else: st.error(analysis_result)