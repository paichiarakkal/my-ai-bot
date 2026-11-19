import streamlit as st
import imaplib
import email
from email.header import decode_header
import json
import hashlib
from groq import Groq
from twilio.rest import Client

# --- PAGE CONFIG ---
st.set_page_config(page_title="PAICHI FULL AGENT", layout="wide")

# --- SECRETS ---
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
GMAIL_USER = st.secrets.get("GMAIL_USER", "")
GMAIL_APP_PASSWORD = st.secrets.get("GMAIL_APP_PASSWORD", "")
TWILIO_SID = st.secrets.get("TWILIO_SID", st.secrets.get("TWILIO_ACCOUNT_SID", ""))
TWILIO_AUTH_TOKEN = st.secrets.get("TWILIO_AUTH_TOKEN", "")
TWILIO_FROM = st.secrets.get("TWILIO_FROM", "whatsapp:+14155238886")

AGENT_MODEL = "openai/gpt-oss-120b"
WHISPER_MODEL = "whisper-large-v3"

# --- FUNCTIONS (TOOLS) ---
def check_gmail_emails(count=3):
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        return "Gmail App Password Streamlit Secrets-ൽ നൽകിയിട്ടില്ല."
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        mail.select("inbox")
        status, messages = mail.search(None, "ALL")
        mail_ids = messages[0].split()
        if not mail_ids:
            return "ഇൻബോക്സിൽ മെയിലുകൾ ഒന്നും ഇല്ല."
        
        latest_ids = mail_ids[-int(count):]
        email_list = []
        for i in reversed(latest_ids):
            res, msg = mail.fetch(i, "(RFC822)")
            for response in msg:
                if isinstance(response, tuple):
                    msg = email.message_from_bytes(response[1])
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8")
                    from_ = msg.get("From")
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                try:
                                    body = part.get_payload(decode=True).decode()
                                except:
                                    pass
                                break
                    else:
                        try:
                            body = msg.get_payload(decode=True).decode()
                        except:
                            pass
                    email_list.append(f"From: {from_}\nSubject: {subject}\nContent: {body[:400]}...\n")
        mail.logout()
        return "\n---\n".join(email_list)
    except Exception as e:
        return f"Gmail Error: {str(e)}"

def send_whatsapp_msg(to_number, message):
    if not TWILIO_SID or not TWILIO_AUTH_TOKEN:
        return "Twilio credentials നൽകിയിട്ടില്ല."
    try:
        client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
        clean_num = to_number.strip()
        if not clean_num.startswith("whatsapp:"):
            clean_num = f"whatsapp:{clean_num}" if clean_num.startswith("+") else f"whatsapp:+{clean_num}"
        client.messages.create(body=message, from_=TWILIO_FROM, to=clean_num)
        return f"Success: {to_number}-ലേക്ക് വാട്ട്സാപ്പ് മെസ്സേജ് അയച്ചു!"
    except Exception as e:
        return f"WhatsApp Error: {str(e)}"

# --- AI TOOLS DEFINITION ---
tools = [
    {
        "type": "function",
        "function": {
            "name": "check_gmail_emails",
            "description": "Check and read the latest emails from the user's Gmail inbox.",
            "parameters": {
                "type": "object",
                "properties": {
                    "count": {"type": "integer", "description": "Number of recent emails to fetch (default 3)"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "send_whatsapp_msg",
            "description": "Send a WhatsApp message to a phone number.",
            "parameters": {
                "type": "object",
                "properties": {
                    "to_number": {"type": "string", "description": "Phone number with country code e.g. +971501234567"},
                    "message": {"type": "string", "description": "The text message to send"}
                },
                "required": ["to_number", "message"]
            }
        }
    }
]

# --- UI ---
st.title("🤖 PAICHI SMART AGENT")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_audio_hash" not in st.session_state:
    st.session_state.last_audio_hash = None

if st.sidebar.button("🗑️ Clear Chat"):
    st.session_state.messages = []
    st.session_state.last_audio_hash = None
    st.rerun()

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# Audio & Text Input
audio_val = st.audio_input("🎤 വോയ്‌സ് റെക്കോർഡ് ചെയ്യുക")
prompt = st.chat_input("ചോദ്യങ്ങൾ ചോദിക്കാം (ഉദാ: last gmail വായിക്കൂ)...")

if audio_val:
    current_hash = hashlib.md5(audio_val.getvalue()).hexdigest()
    if st.session_state.last_audio_hash != current_hash:
        st.session_state.last_audio_hash = current_hash
        try:
            client = Groq(api_key=GROQ_API_KEY)
            transcribed = client.audio.transcriptions.create(
                file=("audio.wav", audio_val.getvalue()),
                model=WHISPER_MODEL,
                response_format="text"
            ).strip()
            # "y" പോലുള്ള അനാവശ്യ ശബ്ദങ്ങൾ ഒഴിവാക്കാൻ
            if len(transcribed) > 1:
                prompt = transcribed
        except Exception as e:
            st.error(f"Audio Error: {e}")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("ആലോചിക്കുന്നു..."):
            try:
                client = Groq(api_key=GROQ_API_KEY)
                sys_msg = {
                    "role": "system",
                    "content": (
                        "You are Paichi AI Assistant. Always reply in natural Malayalam. "
                        "If the user asks to check Gmail or last email, use the `check_gmail_emails` tool immediately and summarize the emails in Malayalam. "
                        "If the user asks to send a WhatsApp message, use `send_whatsapp_msg`. "
                        "Note: You cannot read incoming WhatsApp messages due to WhatsApp privacy rules; inform the user politely if they ask what came on WhatsApp."
                    )
                }
                
                chat_history = [sys_msg] + [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-6:]]
                
                response = client.chat.completions.create(
                    model=AGENT_MODEL,
                    messages=chat_history,
                    tools=tools,
                    tool_choice="auto"
                )
                
                msg = response.choices[0].message
                
                if msg.tool_calls:
                    # ടൂൾ പ്രവർത്തിപ്പിക്കുന്നു
                    chat_history.append(msg)
                    for tc in msg.tool_calls:
                        args = json.loads(tc.function.arguments) if tc.function.arguments else {}
                        if tc.function.name == "check_gmail_emails":
                            tool_res = check_gmail_emails(args.get("count", 3))
                        elif tc.function.name == "send_whatsapp_msg":
                            tool_res = send_whatsapp_msg(args.get("to_number"), args.get("message"))
                        else:
                            tool_res = "Unknown tool"
                            
                        chat_history.append({
                            "role": "tool",
                            "tool_call_id": tc.id,
                            "name": tc.function.name,
                            "content": str(tool_res)
                        })
                    
                    # ടൂളിൽ നിന്ന് കിട്ടിയ വിവരങ്ങൾ വെച്ച് AI മറുപടി ഉണ്ടാക്കുന്നു
                    final_res = client.chat.completions.create(
                        model=AGENT_MODEL,
                        messages=chat_history
                    ).choices[0].message.content
                else:
                    final_res = msg.content

                st.markdown(final_res)
                st.session_state.messages.append({"role": "assistant", "content": final_res})
                
            except Exception as e:
                st.error(f"Error: {e}"