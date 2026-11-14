import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import requests
from datetime import datetime
import random
import plotly.express as px
import plotly.graph_objects as go
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
import urllib.request
import xml.etree.ElementTree as ET
from email.header import decode_header
from groq import Groq
from twilio.rest import Client

# --- CONFIG ---
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

# --- TWILIO CONFIG ---
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
        return False

# --- 🌑 FORCED FULL DARK MODE & 3D UI SETUP ---
st.set_page_config(page_title="PAICHI 3D DARK", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"], .stApp { 
        background-color: #060913 !important;
        background-image: radial-gradient(circle at 15% 15%, #111d3a 0%, #060913 60%) !important;
        color: #ffffff !important; 
    }
    [data-testid="stHeader"] { background-color: rgba(6, 9, 19, 0.9) !important; }
    [data-testid="stSidebar"], [data-testid="stSidebar"] > div { 
        background-color: #0b1120 !important; 
        border-right: 1px solid #1e293b !important;
    }
    h1, h2, h3, h4, h5, h6, p, label, span, li, td, th, .stMarkdown { color: #f1f5f9 !important; }
    .stButton>button, .stFormSubmitButton>button { 
        background: linear-gradient(135deg, #0284c7 0%, #2563eb 100%) !important;
        color: #ffffff !important; border-radius: 12px !important; font-weight: 800 !important; 
        border: 1px solid #38bdf8 !important;
        box-shadow: 0 6px 15px rgba(2, 132, 199, 0.4), 0 3px 0 #1e3a8a !important;
    }
    .card-3d {
        background: linear-gradient(145deg, #0f172a, #1e293b) !important;
        border-radius: 20px !important; border: 1px solid #334155 !important;
        padding: 25px !important; text-align: center !important;
        box-shadow: 0 20px 35px rgba(0, 0, 0, 0.8); margin-bottom: 20px !important;
    }
    .card-3d .b-label { color: #38bdf8 !important; font-size: 16px !important; text-transform: uppercase !important; }
    .card-3d .b-value { color: #ffffff !important; font-size: 42px !important; font-weight: 900 !important; }
    input, textarea, select, [data-baseweb="input"] > div, [data-baseweb="select"] > div {
        background-color: #1e293b !important; color: #ffffff !important; border: 1px solid #475569 !important; border-radius: 10px !important;
    }
    [data-testid="stChatMessage"] { 
        background-color: #111827 !important; border-radius: 16px !important; padding: 15px !important; border: 1px solid #374151 !important; 
    }
    [data-testid="stChatInput"] { background-color: #0b1120 !important; }
    [data-testid="stChatInput"] > div { background-color: #1e293b !important; border: 1px solid #38bdf8 !important; }
    </style>
""", unsafe_allow_html=True)

# --- 🌐 THREE.JS DARK 3D HEADER ---
def render_3d_header():
    three_js_html = """
    <div id="canvas-container" style="width: 100%; height: 130px; border-radius: 18px; overflow: hidden; position: relative; background: #090d16; border: 1px solid #1e293b; box-shadow: 0 10px 30px rgba(0,0,0,0.8);">
        <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center; z-index: 10; pointer-events: none; font-family: sans-serif;">
            <h1 style="margin: 0; font-size: 28px; color: #ffffff; text-shadow: 0 0 15px #38bdf8; letter-spacing: 3px;">PAICHI 3D DARK</h1>
            <p style="margin: 4px 0 0; font-size: 12px; color: #38bdf8; letter-spacing: 1.5px;">AI BUSINESS COMMAND CENTER</p>
        </div>
    </div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
        const container = document.getElementById('canvas-container');
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(60, container.clientWidth / container.clientHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
        renderer.setSize(container.clientWidth, container.clientHeight);
        container.appendChild(renderer.domElement);
        const geometry = new THREE.TorusKnotGeometry(1.4, 0.4, 100, 16);
        const material = new THREE.MeshBasicMaterial({ color: 0x38bdf8, wireframe: true, transparent: true, opacity: 0.3 });
        const torusKnot = new THREE.Mesh(geometry, material);
        scene.add(torusKnot);
        camera.position.z = 4.5;
        function animate() {
            requestAnimationFrame(animate);
            torusKnot.rotation.x += 0.008;
            torusKnot.rotation.y += 0.012;
            renderer.render(scene, camera);
        }
        animate();
    </script>
    """
    components.html(three_js_html, height=140)

# --- SESSION STATES ---
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

def _append_cache_buster(url):
    if not url or "YOUR_" in url: raise ValueError("placeholder")
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

# ============================================
# 🤖 AI AGENT TOOLS & FUNCTIONS
# ============================================
tools = [
    {"type": "function", "function": {"name": "add_finance", "description": "Add finance entry only AFTER user confirms with Yes.", "parameters": {"type": "object", "properties": {"shop": {"type": "string", "enum": ["Shop 1", "Shop 2"]}, "item": {"type": "string"}, "amount": {"type": "number"}, "type": {"type": "string", "enum": ["Debit", "Credit"]}}, "required": ["shop", "item", "amount", "type"]}}},
    {"type": "function", "function": {"name": "add_stock", "description": "Add stock items only AFTER user confirms with Yes.", "parameters": {"type": "object", "properties": {"item_name": {"type": "string"}, "qty": {"type": "number"}, "stock_type": {"type": "string", "enum": ["Stock In", "Stock Out"]}}, "required": ["item_name", "qty", "stock_type"]}}},
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

def fetch_rss_news():
    try:
        url = "https://news.google.com/rss/search?q=gold+rate+petrol+price+kerala+uae+business&hl=en-US&gl=US&ceid=US:en"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req)
        xml_data = response.read()
        root = ET.fromstring(xml_data)
        items = root.findall('.//item')
        return "\n".join([f"- {item.find('title').text}" for item in items[:5]])
    except Exception as e:
        return f"Error fetching news: {e}"

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

def analyze_images_with_groq(images_bytes_list, is_video=False):
    if not GROQ_API_KEY: return False, "Groq Key missing!"
    try:
        client = Groq(api_key=GROQ_API_KEY)
        prompt_text = "Analyze these CCTV video frames carefully. Count the exact number of people visible and describe what they are doing. Provide the report in Malayalam." if is_video else "Count the exact number of items visible and tell me the name and quantity in Malayalam."
        content_list = [{"type": "text", "text": prompt_text}]
        for img in images_bytes_list:
            content_list.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64.b64encode(img).decode('utf-8')}"}})
        res = client.chat.completions.create(model=VISION_MODEL, messages=[{"role": "user", "content": content_list}], max_tokens=1000, temperature=0.1).choices[0].message.content
        final_res = client.chat.completions.create(model=AGENT_MODEL, messages=[{"role": "user", "content": f"Translate into natural Malayalam:\n\n{res}"}], max_tokens=800).choices[0].message.content
        return True, final_res
    except Exception as e: return False, f"Vision Error: {str(e)}"

def process_ai_agent(prompt_text):
    client = Groq(api_key=GROQ_API_KEY)
    
    system_instruction = (
        f"നീ ഒരു ബിസിനസ്സ് AI ആണ്. ബാലൻസ്: ₹{st.session_state.get('current_bal', 0):,.2f}. "
        "ഉപയോക്താവ് വല്ല സാധനവും അളവും പറഞ്ഞാൽ (ഉദാഹരണത്തിന്: 'Sugar 5 kg') അല്ലെങ്കിൽ വരവ്/ചെലവ് കണക്ക് പറഞ്ഞാൽ, "
        "ഒരിക്കലും ഉടൻ തന്നെ ടൂൾ കോൾ ചെയ്യരുത്. "
        "പകരം, 'ഈ വിവരങ്ങൾ ഷീറ്റിലേക്ക് ചേർക്കട്ടെയോ? താഴെ കാണുന്ന YES അല്ലെങ്കിൽ NO ബട്ടൺ അമർത്തുക.' എന്ന് ചോദിച്ചു അനുവാദം ചോദിക്കുക. "
        "ഉപയോക്താവ് 'Yes' എന്ന് മറുപടി നൽകിയാൽ മാത്രം (മുമ്പത്തെ ചാറ്റിൽ പറഞ്ഞ വിവരങ്ങൾ എടുത്ത്) `add_stock` അല്ലെങ്കിൽ `add_finance` ടൂൾ ഉപയോഗിച്ച് ഷീറ്റിലേക്ക് ചേർക്കുക. "
        "മലയാളത്തിൽ മറുപടി നൽകുക."
    )
    
    messages = [{"role": "system", "content": system_instruction}] + [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-6:]] + [{"role": "user", "content": prompt_text}]
    
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
                replies.append(f"✅ {args['shop']}-ൽ '{args['item']}' (₹{args['amount']}) എൻട്രി ഇട്ടു!" if res == "Success" else "❌ എൻട്രി പറ്റിയില്ല.")
            elif tc.function.name == "add_stock":
                res = execute_add_stock(args["item_name"], args["qty"], args.get("stock_type", "Stock In"))
                replies.append(f"✅ {args['item_name']} ({args['qty']} qty) സ്റ്റോക്കിലേക്ക് വിജയകരമായി ചേർത്തു!" if res == "Success" else "❌ സ്റ്റോക്ക് അപ്ഡേറ്റ് പരാജയപ്പെട്ടു.")
            elif tc.function.name == "check_gmail":
                raw = check_gmail_emails(args.get("count", 3))
                summary = client.chat.completions.create(model=AGENT_MODEL, messages=[{"role": "user", "content": f"ചുരുക്കി മലയാളത്തിൽ എഴുതുക:\n{raw}"}], max_tokens=800).choices[0].message.content
                replies.append(f"📧 **ഇമെയിൽ സംഗ്രഹം:**\n\n{summary}")
        ai_reply = "\n\n".join(replies)
    else:
        ai_reply = msg.content or ""
    return ai_reply, tool_used

# --- 🔒 3D DARK LOGIN SCREEN ---
if not st.session_state.auth:
    render_3d_header()
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        st.markdown('<div class="card-3d"><h2 style="margin:0;">🔐 DARK MODE LOGIN</h2><p style="color:#38bdf8 !important;">Enter PIN to Access Dashboard</p></div>', unsafe_allow_html=True)
        u = st.selectbox("👤 Select Role", ["admin", "shop1"]).lower()
        pin = st.text_input("🔑 Enter PIN", type="password", max_chars=4)
        if st.button("LOGIN", use_container_width=True):
            if USER_PINS.get(u) == pin:
                st.session_state.auth, st.session_state.user = True, u; st.rerun()
            else: st.error("❌ Incorrect PIN!")

else:
    render_3d_header()
    st.sidebar.markdown(f"### 💠 Operator: `{st.session_state.user.upper()}`")
    
    menu = ["📊 3D Dashboard", "💰 Add Finance", "📦 Stock Management", "🧾 Bill Scanner", "📧 Email Replier", "📢 WhatsApp Marketing", "📰 Daily Market News", "👨‍💼 Staff Salary", "🤖 AI Agent", "🎥 CCTV AI Vision"]
    page = st.sidebar.radio("NAVIGATION", menu)

    if st.sidebar.button("LOGOUT", use_container_width=True):
        st.session_state.auth = False; st.session_state.messages = []; st.rerun()

    df_fin = load_finance_data()
    df_stk = load_stock_data()
    bal = (df_fin['Credit'].sum() - df_fin['Debit'].sum()) if not df_fin.empty else 0
    st.session_state['current_bal'] = bal

    # --- 1. REAL 3D DARK DASHBOARD ---
    if page == "📊 3D Dashboard":
        c1, c2, c3 = st.columns(3)
        tot_cred = df_fin['Credit'].sum() if not df_fin.empty else 0
        tot_deb = df_fin['Debit'].sum() if not df_fin.empty else 0
        
        with c1:
            st.markdown(f'<div class="card-3d"><span class="b-label">Total Balance</span><br><span class="b-value">₹{bal:,.0f}</span></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="card-3d"><span class="b-label" style="color:#4ade80 !important;">Total Credit</span><br><span class="b-value" style="color:#4ade80 !important;">₹{tot_cred:,.0f}</span></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="card-3d"><span class="b-label" style="color:#f87171 !important;">Total Debit</span><br><span class="b-value" style="color:#f87171 !important;">₹{tot_deb:,.0f}</span></div>', unsafe_allow_html=True)

        if not df_fin.empty:
            st.subheader("🌐 Interactive 3D Financial Mesh")
            df_plot = df_fin.copy()
            df_plot['Index'] = range(1, len(df_plot) + 1)
            fig_3d = px.scatter_3d(
                df_plot, x='Index', y='Credit', z='Debit',
                color='Shop Name', size_max=18, opacity=0.9,
                hover_data=['Item', 'Date'],
                color_discrete_sequence=['#38bdf8', '#f43f5e']
            )
            fig_3d.update_layout(
                paper_bgcolor='#060913', font=dict(color='#ffffff'),
                scene=dict(
                    xaxis=dict(backgroundcolor="#0f172a", gridcolor="#334155"),
                    yaxis=dict(backgroundcolor="#0f172a", gridcolor="#334155"),
                    zaxis=dict(backgroundcolor="#0f172a", gridcolor="#334155"),
                ),
                margin=dict(l=0, r=0, b=0, t=0), height=450
            )
            st.plotly_chart(fig_3d, use_container_width=True)
            st.dataframe(df_fin.tail(10).iloc[::-1], use_container_width=True)

    # --- 2. ADD FINANCE ---
    elif page == "💰 Add Finance":
        st.title("💰 Finance Entry")
        show_flash()
        with st.form("finance_form", clear_on_submit=True):
            shop = st.selectbox("Select Shop", ["Shop 1", "Shop 2"])
            it = st.text_input("Description"); am_str = st.text_input("Amount")
            ty = st.radio("Type", ["Debit (Expense)", "Credit (Sales)"], horizontal=True)
            if st.form_submit_button("SAVE ENTRY", use_container_width=True):
                try:
                    am = float(am_str.strip().replace(',', ''))
                    if execute_add_finance(shop, it, am, "Debit" if "Debit" in ty else "Credit") == "Success":
                        flash_success("Saved! ✅"); st.rerun()
                except: st.error("❗ Invalid amount.")

    # --- 3. STOCK MANAGEMENT ---
    elif page == "📦 Stock Management":
        st.title("📦 Stock & Inventory")
        show_flash()
        tab1, tab2 = st.tabs(["📊 Current Stock", "➕ Add Entry"])
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
                if st.form_submit_button("SAVE STOCK", use_container_width=True):
                    if execute_add_stock(item_name, qty, stock_type) == "Success":
                        flash_success("Stock Updated! ✅"); st.rerun()

    # --- 4. BILL SCANNER ---
    elif page == "🧾 Bill Scanner":
        st.title("🧾 Bill Scanner")
        bill_file = st.file_uploader("Upload Bill Photo", type=["jpg", "jpeg", "png"])
        if bill_file is not None:
            st.image(bill_file, caption="Uploaded Bill", use_container_width=True)
            if st.button("🔍 Extract & Add", use_container_width=True):
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
        if st.button("🔄 പുതിയ മെയിലുകൾ ചെക്ക് ചെയ്യുക", use_container_width=True):
            with st.spinner("AI മെയിലുകൾ വായിക്കുന്നു..."):
                raw_emails = check_gmail_emails(1)
                if "Error" in raw_emails or "ഇല്ല" in raw_emails: st.warning(raw_emails)
                else:
                    st.text_area("Email", raw_emails, height=200, disabled=True)
                    client = Groq(api_key=GROQ_API_KEY)
                    prompt = f"ഈ മെയിൽ പ്രധാനപ്പെട്ടതാണോ എന്ന് പറയുക. പ്രധാനമാണെങ്കിൽ ഒരു പ്രൊഫഷണൽ റിപ്ലൈ തയ്യാറാക്കുക.\n\n{raw_emails}"
                    reply_res = client.chat.completions.create(model=AGENT_MODEL, messages=[{"role": "user", "content": prompt}], max_tokens=800).choices[0].message.content
                    st.markdown(reply_res)

    # --- 6. WHATSAPP MARKETING ---
    elif page == "📢 WhatsApp Marketing":
        st.title("📢 Customer WhatsApp Marketing")
        ai_prompt = st.text_input("AI-യോട് മെസ്സേജ് എഴുതാൻ പറയാം (ഉദാ: 'ഓണം ഓഫർ 10%')")
        if st.button("🤖 AI മെസ്സേജ് ഉണ്ടാക്കുക", use_container_width=True) and ai_prompt:
            client = Groq(api_key=GROQ_API_KEY)
            prompt = f"ഇതിനെ അടിസ്ഥാനമാക്കി ഒരു കിടിലൻ വാട്ട്സ്ആപ്പ് മാർക്കറ്റിംഗ് മെസ്സേജ് മലയാളത്തിൽ എഴുതുക: '{ai_prompt}'"
            st.session_state['wa_message'] = client.chat.completions.create(model=AGENT_MODEL, messages=[{"role": "user", "content": prompt}]).choices[0].message.content
        msg_to_send = st.text_area("മെസ്സേജ്", value=st.session_state.get('wa_message', ''), height=150)
        numbers_input = st.text_area("ഫോൺ നമ്പറുകൾ", placeholder="+971501234567, +919876543210")
        numbers_list = [num.strip() for num in numbers_input.split(",") if num.strip()]
        if st.button("🚀 മെസ്സേജ് അയക്കുക", use_container_width=True):
            if msg_to_send and numbers_list and TWILIO_SID:
                for num in numbers_list:
                    send_whatsapp_custom(f"whatsapp:{num}" if not num.startswith("whatsapp:") else num, msg_to_send)
                    time.sleep(1)
                st.success("✅ മെസ്സേജ് അയച്ചു!")

    # --- 7. DAILY MARKET NEWS ---
    elif page == "📰 Daily Market News":
        st.title("📰 Daily Market & Business News")
        if st.button("🔄 വാർത്തകൾ കാണുക", use_container_width=True):
            raw_news = fetch_rss_news()
            client = Groq(api_key=GROQ_API_KEY)
            summary = client.chat.completions.create(model=AGENT_MODEL, messages=[{"role": "user", "content": f"മലയാളത്തിൽ ചുരുക്കി എഴുതുക:\n{raw_news}"}], max_tokens=800).choices[0].message.content
            st.markdown(summary)

    # --- 8. STAFF SALARY ---
    elif page == "👨‍💼 Staff Salary":
        st.title("👨‍💼 Staff Salary Management")
        show_flash()
        with st.form("salary_form", clear_on_submit=True):
            shop = st.selectbox("Select Shop", ["Shop 1", "Shop 2"])
            emp_name = st.text_input("Employee Name"); sal_amt = st.number_input("Salary Amount", min_value=1.0)
            if st.form_submit_button("PAY SALARY", use_container_width=True):
                if execute_add_finance(shop, f"Salary: {emp_name}", sal_amt, "Debit") == "Success":
                    flash_success(f"✅ {emp_name}-ന്റെ ശമ്പളം നൽകി!"); st.rerun()

    # --- 9. AI AGENT (WITH YES / NO BUTTONS) ---
    elif page == "🤖 AI Agent":
        st.title("🤖 PAICHI Business AI")
        st.info("💡 ടിപ്പ്: 'Sugar 5 kg' എന്ന് പറഞ്ഞാൽ AI ചോദിക്കും. തുടർന്ന് താഴെ കാണുന്ന YES / NO ബട്ടൺ അമർത്തിയാൽ മതി!")
        
        if st.button("🗑️ Clear Chat"): 
            st.session_state.messages = []
            st.session_state['audio_counter'] += 1
            st.rerun()
        
        for message in st.session_state.messages:
            with st.chat_message(message["role"]): 
                st.markdown(message["content"])

        # --- YES / NO QUICK ACTION BUTTONS ---
        if st.session_state.messages and st.session_state.messages[-1]["role"] == "assistant":
            col_y, col_n = st.columns(2)
            with col_y:
                if st.button("✅ YES (ചേർക്കുക)", use_container_width=True):
                    st.session_state.messages.append({"role": "user", "content": "Yes"})
                    with st.spinner("ഷീറ്റിലേക്ക് ചേർക്കുന്നു..."):
                        ai_reply, _ = process_ai_agent("Yes")
                        st.session_state.messages.append({"role": "assistant", "content": ai_reply})
                    st.rerun()
            with col_n:
                if st.button("❌ NO (വേണ്ട)", use_container_width=True):
                    st.session_state.messages.append({"role": "user", "content": "No"})
                    st.session_state.messages.append({"role": "assistant", "content": "❌ ശരി, ഇത് ഒഴിവാക്കിയിരിക്കുന്നു. മറ്റെന്തെങ്കിലും സഹായം ആവശ്യമുണ്ടോ?"})
                    st.rerun()
            
        audio_value = st.audio_input("🎤 റെക്കോർഡ് ചെയ്യാൻ അമർത്തുക", key=f"audio_{st.session_state['audio_counter']}")
        text_prompt = st.chat_input("ഇവിടെ ടൈപ്പ് ചെയ്യാം (ഉദാ: Sugar 5 kg)...")
        prompt = text_prompt
        
        if audio_value and st.session_state.get("last_audio_hash") != hashlib.md5(audio_value.getvalue()).hexdigest():
            st.session_state["last_audio_hash"] = hashlib.md5(audio_value.getvalue()).hexdigest()
            client = Groq(api_key=GROQ_API_KEY)
            prompt = client.audio.transcriptions.create(file=(audio_value.name, audio_value.getvalue()), model=WHISPER_MODEL, response_format="text").strip()
            
        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.spinner("AI ആലോചിക്കുന്നു..."):
                ai_reply, _ = process_ai_agent(prompt)
                st.session_state.messages.append({"role": "assistant", "content": ai_reply})
            st.session_state['audio_counter'] += 1
            st.rerun()

    # --- 10. CCTV AI VISION ---
    elif page == "🎥 CCTV AI Vision":
        st.title("🎥 CCTV AI Vision")
        uploaded_file = st.file_uploader("Upload Shop CCTV Photo or Video", type=["jpg", "jpeg", "png", "mp4"])
        if uploaded_file is not None:
            is_vid = "image" not in uploaded_file.type
            images_to_analyze = extract_frames_from_video(uploaded_file.getvalue()) if is_vid else [uploaded_file.getvalue()]
            if st.button("🔍 Analyze with AI", use_container_width=True):
                ok, analysis_result = analyze_images_with_groq(images_to_analyze, is_video=is_vid)
                st.success(analysis_result) if ok else st.error(analysis_result)