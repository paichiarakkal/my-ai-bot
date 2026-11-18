import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import requests
from datetime import datetime, timezone, timedelta
import random
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF
import re
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
from streamlit_calendar import calendar
from twilio.rest import Client
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh

# --- STREAMLIT UI SETUP ---
st.set_page_config(page_title="PAICHI EXPENSES v3.0 - FULL COMMAND CENTER", layout="wide", initial_sidebar_state="expanded")

# --- CONFIG & SETTINGS ---
CSV_URL = st.secrets.get("GOOGLE_SHEET_CSV", "YOUR_FINANCE_SHEET_CSV_LINK")
DEBT_CSV_URL = st.secrets.get("GOOGLE_SHEET_DEBT_CSV", "")
WEB_APP_URL = st.secrets.get("APPS_SCRIPT_URL", "YOUR_FINANCE_FORM_API")
STOCK_CSV_URL = st.secrets.get("STOCK_SHEET_CSV_LINK", "YOUR_STOCK_SHEET_CSV_LINK")
STOCK_FORM_API = st.secrets.get("STOCK_FORM_API", "YOUR_STOCK_FORM_API")
WA_PHONE = "971551347989"

USER_PINS = {
    "faisal": st.secrets.get("PIN_FAISAL", "1234"),
    "shabana": st.secrets.get("PIN_SHABANA", "2222"),
    "admin": st.secrets.get("PIN_ADMIN", "1111")
}

BG_IMAGE_URL = "https://raw.githubusercontent.com/paichiarakkal/paichiarakkal/main/profile.jpg"
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")

GMAIL_USER = st.secrets.get("GMAIL_USER", "")
GMAIL_APP_PASSWORD = st.secrets.get("GMAIL_APP_PASSWORD", "")

# --- TWILIO CONFIG ---
try:
    TWILIO_SID = st.secrets.get("TWILIO_SID", st.secrets.get("TWILIO_ACCOUNT_SID", ""))
    TWILIO_AUTH_TOKEN = st.secrets.get("TWILIO_AUTH_TOKEN", "")
    TWILIO_FROM = st.secrets.get("TWILIO_FROM", "whatsapp:+14155238886")
except Exception:
    TWILIO_SID = ""
    TWILIO_AUTH_TOKEN = ""
    TWILIO_FROM = "whatsapp:+14155238886"

VISION_MODEL = "qwen/qwen3.8-27b"
AGENT_MODEL  = "openai/gpt-oss-120b"
WHISPER_MODEL = "whisper-large-v3"

# --- TIMEZONE SETUP (GST - Dubai Time) ---
GST = timezone(timedelta(hours=4))
st_autorefresh(interval=60000, key="auto_refresh")

# ============================================
# 🌑 FORCED FULL DARK MODE & 3D CSS
# ============================================
st.markdown(f"""
    <style>
    html, body, [data-testid="stAppViewContainer"], .stApp {{ 
        background-color: #060913 !important;
        background-image: linear-gradient(rgba(10, 10, 25, 0.85), rgba(10, 10, 25, 0.95)), url("{BG_IMAGE_URL}"); 
        background-size: cover; background-attachment: fixed; background-position: center;
        color: #ffffff !important; 
    }}
    [data-testid="stHeader"] {{ background-color: rgba(6, 9, 19, 0.9) !important; }}
    [data-testid="stSidebar"], [data-testid="stSidebar"] > div {{ 
        background: rgba(20, 20, 35, 0.85) !important; backdrop-filter: blur(15px);
        border-right: 1px solid rgba(255, 255, 255, 0.1); box-shadow: 5px 0 15px rgba(0,0,0,0.5);
    }}
    .stButton>button, .stFormSubmitButton>button {{ 
        background: linear-gradient(135deg, #FFD700, #FFA500); color: #000; border-radius: 12px; 
        font-weight: bold; width: 100%; border: none; padding: 10px;
        box-shadow: 0 4px 15px rgba(255, 215, 0, 0.4), inset 0 -3px 0 rgba(0,0,0,0.2);
        transition: all 0.2s ease;
    }}
    .stButton>button:hover {{ transform: translateY(-2px); box-shadow: 0 6px 20px rgba(255, 215, 0, 0.6); }}
    .glass-card {{ background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 20px; padding: 25px; box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37); margin-bottom: 25px; text-align: center; }}
    .balance-banner {{ background: linear-gradient(135deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.02)); backdrop-filter: blur(10px); padding: 30px; border-radius: 20px; border-left: 8px solid #FFD700; text-align: center; margin-bottom: 25px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }}
    .category-box {{ background: rgba(0, 0, 0, 0.5); padding: 20px; border-radius: 15px; text-align: center; border-bottom: 4px solid #FFD700; margin-bottom: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }}
    .alert-banner {{ background: linear-gradient(90deg, #ff4d4d, #cc0000); color: white; padding: 15px; border-radius: 10px; text-align: center; font-weight: bold; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(255, 77, 77, 0.4); }}
    .login-card {{ background: rgba(20, 20, 35, 0.8); backdrop-filter: blur(20px); padding: 40px; border-radius: 20px; max-width: 450px; margin: auto; margin-top: 80px; border: 1px solid rgba(255, 255, 255, 0.1); box-shadow: 0 15px 35px rgba(0,0,0,0.6); }}
    .card-3d {{
        background: linear-gradient(145deg, #0f172a, #1e293b) !important;
        border-radius: 20px !important; border: 1px solid #334155 !important;
        padding: 25px !important; text-align: center !important;
        box-shadow: 0 20px 35px rgba(0, 0, 0, 0.8); margin-bottom: 20px !important;
    }}
    .card-3d .b-label {{ color: #38bdf8 !important; font-size: 16px !important; text-transform: uppercase !important; }}
    .card-3d .b-value {{ color: #ffffff !important; font-size: 42px !important; font-weight: 900 !important; }}
    h1, h2, h3, p, label, span, th, td {{ color: #FFFFFF !important; font-weight: bold !important; text-shadow: 0 2px 4px rgba(0,0,0,0.5); }}
    [data-testid="stChatMessage"] {{ background: rgba(32, 44, 51, 0.9) !important; border-radius: 15px !important; padding: 15px !important; margin-bottom: 10px !important; border: 1px solid rgba(255,255,255,0.05) !important; box-shadow: 0 4px 10px rgba(0,0,0,0.3); }}
    [data-testid="stChatInput"] {{ background-color: rgba(42, 57, 66, 0.8) !important; border-radius: 25px !important; border: 1px solid rgba(255,255,255,0.1) !important; padding: 5px !important; }}
    input, textarea, select {{ color: #FFFFFF !important; -webkit-text-fill-color: #FFFFFF !important; background-color: rgba(0, 0, 0, 0.5) !important; border: 1px solid rgba(255, 255, 255, 0.2) !important; border-radius: 8px !important; }}
    ::placeholder {{ color: #AAAAAA !important; }}
    </style>
""", unsafe_allow_html=True)

# --- 🌐 THREE.JS 3D HEADER ---
def render_3d_header():
    three_js_html = """
    <div id="canvas-container" style="width: 100%; height: 130px; border-radius: 18px; overflow: hidden; position: relative; background: #090d16; border: 1px solid #1e293b; box-shadow: 0 10px 30px rgba(0,0,0,0.8);">
        <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center; z-index: 10; pointer-events: none; font-family: sans-serif;">
            <h1 style="margin: 0; font-size: 28px; color: #ffffff; text-shadow: 0 0 15px #38bdf8; letter-spacing: 3px;">PAICHI EXPENSES v3.0</h1>
            <p style="margin: 4px 0 0; font-size: 12px; color: #38bdf8; letter-spacing: 1.5px;">AI BUSINESS & FINANCE COMMAND CENTER</p>
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
if 'auth' not in st.session_state: st.session_state.auth, st.session_state.user = False, ""
if 'custom_alert_text' not in st.session_state: st.session_state.custom_alert_text = "Shop kuri book"
if 'low_limit' not in st.session_state: st.session_state.low_limit = 6000
if "last_processed_prompt" not in st.session_state: st.session_state.last_processed_prompt = None
if "pending_entry" not in st.session_state: st.session_state.pending_entry = None
if "entry_saved_flag" not in st.session_state: st.session_state.entry_saved_flag = False
if "messages" not in st.session_state: st.session_state.messages = []
if "audio_counter" not in st.session_state: st.session_state.audio_counter = 0
if "last_audio_hash" not in st.session_state: st.session_state.last_audio_hash = None
if "wa_message" not in st.session_state: st.session_state.wa_message = ""

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

def parse_mixed_dates(date_series):
    parsed = []
    for val in date_series:
        dt = pd.to_datetime(str(val).strip(), errors='coerce')
        if not pd.isna(dt) and dt.year == 2026 and dt.month < 4: 
            dt = dt.replace(year=2026)
        if pd.isna(dt): 
            dt = pd.to_datetime(str(val).strip(), dayfirst=True, errors='coerce')
        parsed.append(dt)
    return pd.Series(parsed)

@st.cache_data(ttl=10)
def load_data():
    try:
        if not CSV_URL or "YOUR_" in CSV_URL: return pd.DataFrame(columns=['Date', 'Item', 'Debit', 'Credit'])
        df = pd.read_csv(_append_cache_buster(CSV_URL))
        df.columns = df.columns.str.strip()
        df['Date'] = parse_mixed_dates(df['Date'])
        df['Debit'] = pd.to_numeric(df['Debit'], errors='coerce').fillna(0)
        df['Credit'] = pd.to_numeric(df['Credit'], errors='coerce').fillna(0)
        return df
    except Exception: 
        return pd.DataFrame(columns=['Date', 'Item', 'Debit', 'Credit'])

@st.cache_data(ttl=10)
def load_debts_data():
    try:
        if not DEBT_CSV_URL: return pd.DataFrame(columns=['ID', 'Name', 'Type', 'Amount', 'Date', 'Status', 'Sender'])
        df = pd.read_csv(_append_cache_buster(DEBT_CSV_URL))
        df.columns = df.columns.str.strip()
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
        return df
    except Exception: 
        return pd.DataFrame(columns=['ID', 'Name', 'Type', 'Amount', 'Date', 'Status', 'Sender'])

@st.cache_data(ttl=10)
def load_stock_data():
    try:
        if not STOCK_CSV_URL or "YOUR_" in STOCK_CSV_URL: return pd.DataFrame(columns=['Date', 'Item', 'Quantity', 'Type'])
        df = pd.read_csv(_append_cache_buster(STOCK_CSV_URL))
        df.columns = df.columns.str.strip()
        df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce').fillna(0)
        return df
    except Exception: 
        return pd.DataFrame(columns=['Date', 'Item', 'Quantity', 'Type'])

def submit_form(api_url, payload):
    if not api_url or "YOUR_" in api_url: return True  
    try:
        r = requests.post(api_url, data=payload, timeout=10)
        return r.status_code == 200
    except Exception as e:
        return False

def send_whatsapp_auto(msg):
    try:
        if TWILIO_SID and TWILIO_AUTH_TOKEN:
            client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
            client.messages.create(from_=TWILIO_FROM, body=msg, to=f'whatsapp:+{WA_PHONE}')
    except Exception: 
        pass 

def send_whatsapp_custom(to_number, msg):
    if not TWILIO_SID or not TWILIO_AUTH_TOKEN: return False
    try:
        client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
        client.messages.create(body=msg, from_=TWILIO_FROM, to=to_number)
        return True
    except Exception as e:
        return False

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
    except Exception: 
        return None

def add_new_entry(item, amount, category="Others", type="Debit", entry_date=None):
    try:
        if not entry_date: 
            entry_date = datetime.now(GST).strftime("%Y-%m-%d %H:%M:%S")
        payload = {"item": item, "amount": amount, "category": category, "type": type, "date": entry_date, "sender": st.session_state.user.capitalize()}
        if WEB_APP_URL and "YOUR_" not in WEB_APP_URL:
            requests.post(WEB_APP_URL, json=payload, timeout=10)
        send_whatsapp_auto(f"✅ *AI Entry Added*\n📝 Item: {item}\n💰 Amt: ₹{amount}")
        return f"Success: {item} - ₹{amount} ({type})"
    except Exception as e: 
        return f"Error: {str(e)}"

def add_debt_via_ai(name, type, amount, date=None):
    try:
        if not date: 
            date = datetime.now(GST).strftime("%Y-%m-%d")
        payload = {"action": "add_debt", "name": name, "type": type, "amount": amount, "date": date, "sender": st.session_state.user.capitalize()}
        if WEB_APP_URL and "YOUR_" not in WEB_APP_URL:
            requests.post(WEB_APP_URL, json=payload, timeout=10)
        send_whatsapp_auto(f"🤝 *AI Debt Added*\n👤 Person: {name}\n📌 Type: {type}\n💰 Amt: ₹{amount}")
        return f"Success: {type} - {name} - ₹{amount}"
    except Exception as e: 
        return f"Error: {str(e)}"

def execute_add_stock(item_name, qty, stock_type):
    payload = {"entry.1044099436": datetime.now().strftime("%Y-%m-%d"), "entry.2013476337": item_name, "entry.1460982454": qty, "entry.1221658767": stock_type}
    if submit_form(STOCK_FORM_API, payload): 
        load_stock_data.clear()
        return "Success"
    return "Failed"

def check_gmail_emails(count=3):
    if not GMAIL_USER or not GMAIL_APP_PASSWORD: return "Gmail App Password ക്രമീകരിച്ചിട്ടില്ല."
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        mail.select("inbox")
        status, messages = mail.search(None, "ALL")
        mail_ids = messages[0].split()
        if not mail_ids: return "മെയിലുകൾ ഒന്നും ലഭ്യമല്ല."
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

# --- TOOLS FOR AI AGENT ---
tools = [
    {
        "type": "function", 
        "function": {
            "name": "add_new_entry", 
            "description": "Add a single expense or income", 
            "parameters": {
                "type": "object", 
                "properties": {
                    "item": {"type": "string"}, 
                    "amount": {"type": "number"}, 
                    "category": {"type": "string", "description": "Food, Shop, Fish, Travel, Rent, Others"}, 
                    "type": {"type": "string", "enum": ["Debit", "Credit"]}, 
                    "date": {"type": "string", "description": "YYYY-MM-DD HH:MM:SS"}
                }, 
                "required": ["item", "amount"]
            }
        }
    },
    {
        "type": "function", 
        "function": {
            "name": "add_debt_entry", 
            "description": "Add money lent or borrowed to Debt Tracker", 
            "parameters": {
                "type": "object", 
                "properties": {
                    "name": {"type": "string", "description": "Person name"}, 
                    "type": {"type": "string", "enum": ["Lent (കൊടുത്തത്)", "Borrowed (വാങ്ങിയത്)"]}, 
                    "amount": {"type": "number"}, 
                    "date": {"type": "string"}
                }, 
                "required": ["name", "type", "amount"]
            }
        }
    },
    {
        "type": "function", 
        "function": {
            "name": "add_stock", 
            "description": "Add stock items", 
            "parameters": {
                "type": "object", 
                "properties": {
                    "item_name": {"type": "string"}, 
                    "qty": {"type": "number"}, 
                    "stock_type": {"type": "string", "enum": ["Stock In", "Stock Out"]}
                }, 
                "required": ["item_name", "qty", "stock_type"]
            }
        }
    },
    {
        "type": "function", 
        "function": {
            "name": "check_gmail", 
            "description": "Read emails", 
            "parameters": {
                "type": "object", 
                "properties": {
                    "count": {"type": "number"}
                }, 
                "required": ["count"]
            }
        }
    }
]

# --- 🔒 LOGIN SCREEN ---
if not st.session_state.auth:
    render_3d_header()
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.subheader("🔐 PAICHI EXPENSES v3.0 LOGIN")
        u = st.selectbox("👤 Select User", ["faisal", "shabana", "admin"]).lower()
        pin = st.text_input("🔑 Enter 4-Digit PIN", type="password", max_chars=4)
        if st.button("UNLOCK APP 🔓"):
            if USER_PINS.get(u) == pin:
                st.session_state.auth, st.session_state.user = True, u
                st.rerun()
            else: 
                st.error("❌ Incorrect PIN!")
        st.markdown('</div>', unsafe_allow_html=True)

else:
    render_3d_header()
    df = load_data()
    df_stk = load_stock_data()
    t_in, t_out = (df['Credit'].sum(), df['Debit'].sum()) if not df.empty else (0.0, 0.0)
    bal = t_in - t_out
    st.session_state['current_bal'] = bal
    
    if st.session_state.user != "shabana":
        with st.sidebar.expander("⚙️ Settings"):
            st.session_state.custom_alert_text = st.text_area("Alert Message", value=st.session_state.custom_alert_text)
            st.session_state.low_limit = st.number_input("Low Balance Limit (₹)", value=st.session_state.low_limit)
    
    if bal < st.session_state.low_limit:
        st.markdown(f'<div class="alert-banner">⚠️ ബാലൻസ് കുറവാണ്: {st.session_state.custom_alert_text} (₹{bal:,.2f})!</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="balance-banner"><span style="font-size:22px; color:#E0B0FF; letter-spacing: 2px;">AVAILABLE BALANCE</span><br><span style="font-size:50px; color:#FFD700; font-family: monospace;">₹{bal:,.2f}</span></div>', unsafe_allow_html=True)
    
    menu = ["📊 Dashboard", "💰 Add Entry", "📅 Calendar", "📊 Report", "🔍 History", "🤝 Debt Tracker", "📦 Stock", "🧾 Bill Scanner", "📧 Email Replier", "📢 WhatsApp Marketing", "📰 Market News", "🎥 CCTV Vision", "🤖 AI Chat", "🧠 My AI Buddy"]
    page = st.sidebar.radio("Menu", menu)
    
    if st.sidebar.button("Logout", use_container_width=True): 
        st.session_state.auth = False
        st.rerun()

    # --- DASHBOARD ---
    if page == "📊 Dashboard" and not df.empty:
        st.title("Financial Overview (3D Mesh)")
        st.markdown(f'<div class="glass-card"><h2 style="color:#00FF00;">Credit: ₹{t_in:,.2f}</h2><h2 style="color:#FF3131;">Debit: ₹{t_out:,.2f}</h2></div>', unsafe_allow_html=True)
        
        df_plot = df.copy()
        if 'Index' not in df_plot.columns: df_plot['Index'] = range(1, len(df_plot) + 1)
        fig_3d = px.scatter_3d(
            df_plot, x='Index', y='Credit', z='Debit',
            color='Item', size_max=18, opacity=0.9,
            color_discrete_sequence=['#38bdf8', '#f43f5e', '#FFD700']
        )
        fig_3d.update_layout(
            paper_bgcolor='#060913', font=dict(color='#ffffff'),
            scene=dict(
                xaxis=dict(backgroundcolor="#0f172a", gridcolor="#334155"),
                yaxis=dict(backgroundcolor="#0f172a", gridcolor="#334155"),
                zaxis=dict(backgroundcolor="#0f172a", gridcolor="#334155"),
            ),
            margin=dict(l=0, r=0, b=0, t=0), height=400
        )
        st.plotly_chart(fig_3d, use_container_width=True)

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
                    if not st.session_state.entry_saved_flag:
                        add_new_entry(it, am, cat, ty)
                        st.session_state.entry_saved_flag = True
                        st.success("Saved! ✅")
                        time.sleep(1)
                        st.session_state.entry_saved_flag = False
                        st.rerun()
                except Exception as e: 
                    st.error(f"Error! Valid amount required. {e}")

    # --- CALENDAR ---
    elif page == "📅 Calendar" and not df.empty:
        st.title("P&L Calendar View 📅")
        df_cal = df.dropna(subset=['Date'])
        summary = df_cal.groupby(df_cal['Date'].dt.strftime('%Y-%m-%d')).agg({'Debit': 'sum', 'Credit': 'sum'}).reset_index()
        events = []
        for _, row in summary.iterrows():
            if row['Credit'] > 0: events.append({"title": f" +₹{row['Credit']:,.0f}", "start": row['Date'], "backgroundColor": "#198754"})
            if row['Debit'] > 0: events.append({"title": f" -₹{row['Debit']:,.0f}", "start": row['Date'], "backgroundColor": "#dc3545"})
        
        calendar(events=events, options={"headerToolbar": {"left": "prev,next today", "center": "title", "right": "dayGridMonth"}, "initialView": "dayGridMonth"}, key="pnl_calendar")

    # --- REPORT & HISTORY ---
    elif (page == "📊 Report" or page == "🔍 History") and not df.empty:
        df_rep = df.copy()
        df_rep['Month'] = df_rep['Date'].dt.strftime('%B %Y')
        months = df_rep.dropna(subset=['Month']).sort_values(by='Date', ascending=False)['Month'].unique()
        
        if len(months) == 0: 
            st.warning("No data found!")
        else:
            sel_m = st.selectbox("Select Month", months)
            m_df = df_rep[df_rep['Month'] == sel_m].copy()
            m_deb, m_crd = m_df['Debit'].sum(), m_df['Credit'].sum()
            
            if page == "📊 Report":
                st.title("Monthly Expense Analysis")
                c1, c2, c3 = st.columns(3)
                c1.markdown(f'<div class="glass-card"><h3 style="color:#00FF00;">Credit</h3><h1 style="color:#00FF00;">₹{m_crd:,.2f}</h1></div>', unsafe_allow_html=True)
                c2.markdown(f'<div class="glass-card"><h3 style="color:#FF3131;">Expense</h3><h1 style="color:#FF3131;">₹{m_deb:,.2f}</h1></div>', unsafe_allow_html=True)
                c3.markdown(f'<div class="glass-card"><h3 style="color:#FFD700;">Savings</h3><h1 style="color:#FFD700;">₹{m_crd - m_deb:,.2f}</h1></div>', unsafe_allow_html=True)
                
                st.plotly_chart(px.pie(m_df[m_df['Debit'] > 0], values='Debit', names='Item', hole=0.4), use_container_width=True)

            clean_df = m_df.drop(columns=['Month'], errors='ignore')
            clean_df['Date'] = clean_df['Date'].dt.strftime('%d/%m/%Y')
            st.dataframe(clean_df.iloc[::-1], use_container_width=True)

            if page == "📊 Report":
                pdf_bytes = create_pdf(clean_df)
                if pdf_bytes:
                    st.download_button("📄 Download PDF Report", data=pdf_bytes, file_name=f"Paichi_Report_{sel_m}.pdf", mime="application/pdf")

    # --- DEBT TRACKER ---
    elif page == "🤝 Debt Tracker":
        st.title("🤝 Debt Tracker (കടം കണക്കുകൾ)")
        df_debts = load_debts_data()
        tab1, tab2 = st.tabs(["📋 View All Debts", "➕ Add New Debt"])

        with tab1:
            if df_debts.empty:
                st.info("നിലവിൽ കടങ്ങൾ ഒന്നുമില്ല.")
            else:
                st.dataframe(df_debts, use_container_width=True)

        with tab2:
            with st.form("cloud_debt_form", clear_on_submit=True):
                d_name = st.text_input("👤 Person Name")
                d_type = st.selectbox("📌 Type", ["Lent (കൊടുത്തത്)", "Borrowed (വാങ്ങിയത്)"])
                d_amount = st.number_input("💰 Amount (₹)", min_value=1.0)
                d_date = st.date_input("📅 Date", value=datetime.now(GST).date())
                if st.form_submit_button("SAVE DEBT"):
                    add_debt_via_ai(d_name, d_type, d_amount, str(d_date))
                    st.success("Debt Saved! ✅"); time.sleep(1); st.rerun()

    # --- STOCK ---
    elif page == "📦 Stock":
        st.title("📦 Stock Management")
        show_flash()
        tab1, tab2 = st.tabs(["📊 Current Stock", "➕ Add Stock"])
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
                item_name  = st.text_input("Item Name")
                qty = st.number_input("Quantity", min_value=1.0)
                stock_type = st.radio("Type", ["Stock In", "Stock Out"], horizontal=True)
                if st.form_submit_button("SAVE STOCK"):
                    if execute_add_stock(item_name, qty, stock_type) == "Success":
                        flash_success("Stock Updated! ✅"); st.rerun()

    # --- BILL SCANNER ---
    elif page == "🧾 Bill Scanner":
        st.title("🧾 Bill Scanner")
        bill_file = st.file_uploader("Upload Bill Photo", type=["jpg", "jpeg", "png"])
        if bill_file:
            st.image(bill_file, use_container_width=True)
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
                            add_new_entry(f"Purchase: {item['item']}", item['price'], "Shop", "Debit")
                        st.success("🎉 എൻട്രി വിജയകരമായി ചേർത്തു!"); st.rerun()
                    except Exception as e: st.error(f"Error: {e}")

    # --- EMAIL REPLIER ---
    elif page == "📧 Email Replier":
        st.title("📧 Smart Email Replier")
        if st.button("🔄 പുതിയ മെയിലുകൾ പരിശോധിക്കുക"):
            raw_emails = check_gmail_emails(3)
            st.text_area("Emails", raw_emails, height=200, disabled=True)

    # --- WHATSAPP MARKETING ---
    elif page == "📢 WhatsApp Marketing":
        st.title("📢 Customer WhatsApp Marketing")
        ai_prompt = st.text_input("AI-യോട് മെസ്സേജ് എഴുതാൻ ആവശ്യപ്പെടുക (ഉദാ: 'ഓണം ഓഫർ')")
        if st.button("🤖 AI മെസ്സേജ് തയ്യാറാക്കുക") and ai_prompt:
            client = Groq(api_key=GROQ_API_KEY)
            st.session_state['wa_message'] = client.chat.completions.create(model=AGENT_MODEL, messages=[{"role": "user", "content": f"ഈ വിഷയത്തിൽ മലയാളത്തിൽ ഒരു വാട്ട്സാപ്പ് മാർക്കറ്റിംഗ് മെസ്സേജ് എഴുതുക: '{ai_prompt}'"}]).choices[0].message.content
        msg_to_send = st.text_area("Message", value=st.session_state.get('wa_message', ''), height=150)
        numbers_input = st.text_area("Phone Numbers (Comma separated)", placeholder="+971501234567, +919876543210")
        if st.button("🚀 Send WhatsApp Messages"):
            numbers_list = [num.strip() for num in numbers_input.split(",") if num.strip()]
            for num in numbers_list:
                send_whatsapp_custom(f"whatsapp:{num}" if not num.startswith("whatsapp:") else num, msg_to_send)
                time.sleep(1)
            st.success("✅ മെസ്സേജുകൾ അയച്ചിട്ടുണ്ട്!")

    # --- MARKET NEWS ---
    elif page == "📰 Market News":
        st.title("📰 Daily Business & Market News")
        if st.button("🔄 വാർത്തകൾ ലോഡ് ചെയ്യുക"):
            raw_news = fetch_rss_news()
            client = Groq(api_key=GROQ_API_KEY)
            summary = client.chat.completions.create(model=AGENT_MODEL, messages=[{"role": "user", "content": f"ഇത് മലയാളത്തിൽ ചുരുക്കി എഴുതുക:\n{raw_news}"}], max_tokens=800).choices[0].message.content
            st.markdown(summary)

    # --- CCTV VISION ---
    elif page == "🎥 CCTV Vision":
        st.title("🎥 CCTV AI Vision & Footfall Monitor")
        uploaded_file = st.file_uploader("Upload CCTV Photo or Video", type=["jpg", "jpeg", "png", "mp4"])
        if uploaded_file:
            is_vid = "image" not in uploaded_file.type
            images_to_analyze = extract_frames_from_video(uploaded_file.getvalue()) if is_vid else [uploaded_file.getvalue()]
            if st.button("🔍 AI വിശകലനം ചെയ്യുക"):
                ok, analysis_result = analyze_images_with_groq(images_to_analyze, is_video=is_vid)
                st.success(analysis_result) if ok else st.error(analysis_result)

    # --- AI CHAT & AGENT ---
    elif page == "🤖 AI Chat":
        st.title("🤖 PAICHI AI Assistant & Agent")
        
        if st.button("🗑️ Clear Chat"): 
            st.session_state.messages = []
            st.session_state['audio_counter'] += 1
            st.rerun()
        
        for message in st.session_state.messages:
            with st.chat_message(message["role"]): st.markdown(message["content"])

        if st.session_state.messages and st.session_state.messages[-1]["role"] == "assistant":
            col_y, col_n = st.columns(2)
            with col_y:
                if st.button("✅ YES (സ്ഥിരീകരിക്കുക)", use_container_width=True):
                    st.session_state.messages.append({"role": "user", "content": "Yes"})
                    with st.spinner("ഷീറ്റിലേക്ക് ചേർക്കുന്നു..."):
                        client = Groq(api_key=GROQ_API_KEY)
                        messages = [{"role": "system", "content": "നിങ്ങൾ ഒരു അസിസ്റ്റന്റാണ്. ഉപയോക്താവ് Yes എന്ന് പറഞ്ഞാൽ അപ്പോൾ തന്നിരിക്കുന്ന പ്രകാരം ടൂൾ ഉപയോഗിക്കുക."}] + [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-4:]]
                        response = client.chat.completions.create(model=AGENT_MODEL, messages=messages, tools=tools, tool_choice="auto")
                        msg = response.choices[0].message
                        if msg.tool_calls:
                            for tc in msg.tool_calls:
                                args = json.loads(tc.function.arguments)
                                if tc.function.name == 'add_new_entry':
                                    add_new_entry(args.get("item"), args.get("amount"), args.get("category", "Others"), args.get("type", "Debit"))
                                elif tc.function.name == 'add_stock':
                                    execute_add_stock(args.get("item_name"), args.get("qty"), args.get("stock_type", "Stock In"))
                        st.session_state.messages.append({"role": "assistant", "content": "✅ വിജയകരമായി ഷീറ്റിൽ അപ്ഡേറ്റ് ചെയ്തിട്ടുണ്ട്!"})
                    st.rerun()
            with col_n:
                if st.button("❌ NO (വേണ്ട)", use_container_width=True):
                    st.session_state.messages.append({"role": "user", "content": "No"})
                    st.session_state.messages.append({"role": "assistant", "content": "❌ ശരി, ഈ എൻട്രി ഒഴിവാക്കിയിരിക്കുന്നു."})
                    st.rerun()
            
        audio_value = st.audio_input("🎤 വോയ്‌സ് റെക്കോർഡ് ചെയ്യുക", key=f"audio_{st.session_state['audio_counter']}")
        prompt = st.chat_input("ഇവിടെ ടൈപ്പ് ചെയ്യുക...")
        
        if audio_value and st.session_state.get("last_audio_hash") != hashlib.md5(audio_value.getvalue()).hexdigest():
            st.session_state["last_audio_hash"] = hashlib.md5(audio_value.getvalue()).hexdigest()
            client = Groq(api_key=GROQ_API_KEY)
            prompt = client.audio.transcriptions.create(file=(audio_value.name, audio_value.getvalue()), model=WHISPER_MODEL, response_format="text").strip()
            
        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.spinner("AI ആലോചിക്കുന്നു..."):
                try:
                    client = Groq(api_key=GROQ_API_KEY)
                    system_instruction = f"നീ ഒരു ഫിനാൻസ്, സ്റ്റോക്ക് & CCTV വിഷൻ AI അസിസ്റ്റന്റാണ്. ബാലൻസ്: {bal}. ഉപയോക്താവ് ക്യാമറ പരിശോധിക്കാനോ ഫൂട്ടേജുകളെക്കുറിച്ച് ചോദിക്കാനോ ആവശ്യപ്പെട്ടാൽ, '🎥 CCTV Vision' പേജ് ഉപയോഗിക്കാൻ നിർദ്ദേശിക്കുക."
                    messages = [{"role": "system", "content": system_instruction}] + [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-4:]]
                    response = client.chat.completions.create(model=AGENT_MODEL, messages=messages, tools=tools, tool_choice="auto")
                    msg = response.choices[0].message
                    ai_reply = msg.content or "ഇത് സേവ് ചെയ്യട്ടെയോ?"
                    st.session_state.messages.append({"role": "assistant", "content": ai_reply})
                    st.rerun()
                except Exception as e:
                    st.error(f"AI Error: {e}")

    # --- MY AI BUDDY ---
    elif page == "🧠 My AI Buddy":
        st.title("🧠 Your Personal AI Buddy")
        if "buddy_messages" not in st.session_state: st.session_state.buddy_messages = []
        for msg in st.session_state.buddy_messages:
            with st.chat_message(msg["role"]): st.markdown(msg["content"])
        user_input = st.chat_input("ചോദ്യങ്ങൾ ചോദിക്കാം...", key="buddy_chat_box")
        if user_input:
            st.session_state.buddy_messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"): st.markdown(user_input)
            with st.spinner("ആലോചിക്കുന്നു..."):
                try:
                    client = Groq(api_key=GROQ_API_KEY)
                    system_prompt = "You are a helpful personal AI assistant for a Malayali. Answer their questions in Malayalam in a friendly way."
                    messages = [{"role": "system", "content": system_prompt}] + [{"role": m["role"], "content": m["content"]} for m in st.session_state.buddy_messages[-4:]]
                    response = client.chat.completions.create(model=AGENT_MODEL, messages=messages, max_tokens=1024)
                    ai_reply = response.choices[0].message.content
                    st.session_state.buddy_messages.append({"role": "assistant", "content": ai_reply})
                    with st.chat_message("assistant"): st.markdown(ai_reply)
                except Exception as e: 
                    st.error(f"Error: {e}")
import streamlit as st
from groq import Groq

# Page Config
st.set_page_config(page_title="My AI Assistant", layout="centered")

st.title("🤖 എന്റെ സ്വന്തം AI അസിസ്റ്റന്റ്")
st.write("ചേട്ടന് ആവശ്യമായ എന്ത് സംശയങ്ങളും ചോദിക്കാം, ഞാൻ കൃത്യമായി ഉത്തരം തരാം!")

# Groq API Key (Streamlit Secrets-ൽ നിന്ന് എടുക്കുന്നു)
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")

if not GROQ_API_KEY:
    st.error("⚠️ Groq API Key ക്രമീകരിച്ചിട്ടില്ല! ദയവായി secrets.toml-ൽ കീ നൽകുക.")
else:
    client = Groq(api_key=GROQ_API_KEY)

    # Chat history initialize ചെയ്യുക
    if "my_ai_messages" not in st.session_state:
        st.session_state.my_ai_messages = []

    # പഴയ ചാറ്റുകൾ കാണിക്കുക
    for message in st.session_state.my_ai_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # യൂസർ ഇൻപുട്ട്
    user_input = st.chat_input("ഇവിടെ ചോദിക്കാം...")

    if user_input:
        # യൂസർ മെസ്സേജ് സേവ് ചെയ്യുകയും കാണിക്കുകയും ചെയ്യുക
        st.session_state.my_ai_messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # AI മറുപടി ജനേറ്റ് ചെയ്യുക
        with st.spinner("ആലോചിക്കുന്നു..."):
            try:
                system_prompt = "You are a helpful, friendly personal AI assistant for a Malayali. Answer all questions in natural Malayalam in a warm and engaging way."
                messages = [{"role": "system", "content": system_prompt}] + [
                    {"role": m["role"], "content": m["content"]} for m in st.session_state.my_ai_messages
                ]
                
                response = client.chat.completions.create(
                    model="openai/gpt-oss-120b",  # ശക്തമായ AI മോഡൽ
                    messages=messages,
                    max_tokens=1024
                )
                
                ai_reply = response.choices[0].message.content
                
                # AI മറുപടി സേവ് ചെയ്യുകയും കാണിക്കുകയും ചെയ്യുക
                st.session_state.my_ai_messages.append({"role": "assistant", "content": ai_reply})
                with st.chat_message("assistant"):
                    st.markdown(ai_reply)
                    
            except Exception as e:
                st.error(f"എറർ വന്നു: {e}")