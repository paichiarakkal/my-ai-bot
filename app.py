import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import requests
from datetime import datetime, timezone, timedelta
import random
import plotly.express as px
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
st.set_page_config(page_title="PAICHI EXPENSES v3.0 - FULL AGENT", layout="wide", initial_sidebar_state="expanded")

# --- SECRETS & CONFIG ---
CSV_URL = st.secrets.get("GOOGLE_SHEET_CSV", "")
DEBT_CSV_URL = st.secrets.get("GOOGLE_SHEET_DEBT_CSV", "")
WEB_APP_URL = st.secrets.get("APPS_SCRIPT_URL", "")
STOCK_CSV_URL = st.secrets.get("STOCK_SHEET_CSV_LINK", "")
STOCK_FORM_API = st.secrets.get("STOCK_FORM_API", "")
WA_PHONE = st.secrets.get("WA_PHONE", "971551347989")

USER_PINS = {
    "faisal": st.secrets.get("PIN_FAISAL", "1234"),
    "shabana": st.secrets.get("PIN_SHABANA", "2222"),
    "admin": st.secrets.get("PIN_ADMIN", "1111")
}

BG_IMAGE_URL = "https://raw.githubusercontent.com/paichiarakkal/paichiarakkal/main/profile.jpg"
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")

# Gmail Credentials
GMAIL_USER = st.secrets.get("GMAIL_USER", "")
GMAIL_APP_PASSWORD = st.secrets.get("GMAIL_APP_PASSWORD", "")

# Twilio WhatsApp Credentials
TWILIO_SID = st.secrets.get("TWILIO_SID", st.secrets.get("TWILIO_ACCOUNT_SID", ""))
TWILIO_AUTH_TOKEN = st.secrets.get("TWILIO_AUTH_TOKEN", "")
TWILIO_FROM = st.secrets.get("TWILIO_FROM", "whatsapp:+14155238886")

VISION_MODEL = "qwen/qwen3.8-27b"
AGENT_MODEL  = "openai/gpt-oss-120b"
WHISPER_MODEL = "whisper-large-v3"

GST = timezone(timedelta(hours=4))
st_autorefresh(interval=60000, key="auto_refresh")

# --- STYLING ---
st.markdown(f"""
    <style>
    html, body, [data-testid="stAppViewContainer"], .stApp {{ 
        background-color: #060913 !important;
        background-image: linear-gradient(rgba(10, 10, 25, 0.85), rgba(10, 10, 25, 0.95)), url("{BG_IMAGE_URL}"); 
        background-size: cover; background-attachment: fixed; background-position: center;
        color: #ffffff !important; 
    }}
    [data-testid="stHeader"] {{ background-color: rgba(6, 9, 19, 0.9) !important; }}
    [data-testid="stSidebar"] {{ background: rgba(20, 20, 35, 0.85) !important; backdrop-filter: blur(15px); }}
    .stButton>button {{ 
        background: linear-gradient(135deg, #FFD700, #FFA500); color: #000; border-radius: 12px; 
        font-weight: bold; width: 100%; border: none; padding: 10px;
    }}
    .glass-card {{ background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 20px; padding: 25px; margin-bottom: 25px; text-align: center; }}
    h1, h2, h3, p, label {{ color: #FFFFFF !important; }}
    </style>
""", unsafe_allow_html=True)

# --- SESSION STATES ---
if 'auth' not in st.session_state: st.session_state.auth, st.session_state.user = False, ""
if "messages" not in st.session_state: st.session_state.messages = []
if "audio_counter" not in st.session_state: st.session_state.audio_counter = 0

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
    except Exception: 
        return False

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
                    email_list.append(f"From: {from_}\nSubject: {subject}\nBody: {body[:500]}...\n")
        mail.logout()
        return "\n---\n".join(email_list)
    except Exception as e: return f"Gmail Error: {str(e)}"

# --- LOGIN SCREEN ---
if not st.session_state.auth:
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        st.subheader("🔐 LOGIN PAICHI AGENT")
        u = st.selectbox("👤 Select User", ["faisal", "shabana", "admin"]).lower()
        pin = st.text_input("🔑 Enter PIN", type="password", max_chars=4)
        if st.button("UNLOCK 🔓"):
            if USER_PINS.get(u) == pin:
                st.session_state.auth, st.session_state.user = True, u
                st.rerun()
            else: st.error("❌ Incorrect PIN!")
else:
    st.title("🤖 PAICHI FULL AGENT (Gmail, WhatsApp, Mobile Access)")
    
    menu = ["🤖 AI Agent Chat", "📧 Gmail Inbox", "📢 WhatsApp Marketing", "🎥 Mobile/CCTV Vision"]
    page = st.sidebar.radio("Navigation", menu)
    
    if st.sidebar.button("Logout"): 
        st.session_state.auth = False
        st.rerun()

    if page == "🤖 AI Agent Chat":
        st.subheader("AI Voice & Text Assistant")
        for m in st.session_state.messages:
            with st.chat_message(m["role"]): st.markdown(m["content"])
            
        audio_val = st.audio_input("🎤 വോയ്‌സ് റെക്കോർഡ് ചെയ്യുക", key=f"aud_{st.session_state.audio_counter}")
        prompt = st.chat_input("ചോദ്യങ്ങൾ ചോദിക്കാം...")
        
        if audio_val:
            client = Groq(api_key=GROQ_API_KEY)
            prompt = client.audio.transcriptions.create(file=(audio_val.name, audio_val.getvalue()), model=WHISPER_MODEL, response_format="text").strip()
            
        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.spinner("AI പ്രോസസ്സ് ചെയ്യുന്നു..."):
                client = Groq(api_key=GROQ_API_KEY)
                res = client.chat.completions.create(model=AGENT_MODEL, messages=[{"role": "system", "content": "You are an AI assistant in Malayalam."}] + st.session_state.messages).choices[0].message.content
                st.session_state.messages.append({"role": "assistant", "content": res})
                st.rerun()

    elif page == "📧 Gmail Inbox":
        st.subheader("📧 Gmail Integration")
        if st.button("🔄 Check Latest Emails"):
            emails_data = check_gmail_emails(5)
            st.text_area("Inbox Messages", emails_data, height=300)

    elif page == "📢 WhatsApp Marketing":
        st.subheader("📢 Twilio WhatsApp Integration")
        num = st.text_input("Mobile Number (with country code, e.g., 971501234567)")
        msg_text = st.text_area("Message")
        if st.button("🚀 Send WhatsApp"):
            if send_whatsapp_custom(f"whatsapp:+{num}", msg_text):
                st.success("✅ WhatsApp message sent successfully!")
            else:
                st.error("❌ Failed to send message. Check Twilio credentials.")

    elif page == "🎥 Mobile/CCTV Vision":
        st.subheader("📷 Mobile Camera / Image / Video Vision")
        uploaded = st.file_uploader("Upload Image or Video", type=["jpg", "png", "mp4"])
        if uploaded and st.button("🔍 Analyze with AI Vision"):
            client = Groq(api_key=GROQ_API_KEY)
            b64 = base64.b64encode(uploaded.getvalue()).decode('utf-8')
            res = client.chat.completions.create(model=VISION_MODEL, messages=[{"role": "user", "content": [{"type": "text", "text": "Describe this image in Malayalam."}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}]}])
            st.success(res.choices[0].message.content)