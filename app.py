import streamlit as st
import yfinance as yf
from PIL import Image
import os

# 1. പേജ് സെറ്റപ്പ്
st.set_page_config(page_title="Faisal Pro Smart Bot", layout="wide")
st.markdown('<link rel="manifest" href="./manifest.json">', unsafe_allow_html=True)

# 2. ഹെഡർ - ഫോട്ടോയും പേരും
cols = st.columns([1, 4, 1])
with cols[1]:
    if os.path.exists("image_12.png"):
        st.image(Image.open("image_12.png"), width=150)
    else:
        st.write("FAISAL ARAKKAL")
    st.markdown("<h1 style='text-align: center; color: #1E88E5;'>🤖 ഫൈസൽസ് സ്മാർട്ട് ബോട്ട്</h1>", unsafe_allow_html=True)

# 3. ലൈവ് കറൻസി കൺവെർട്ടർ (Side-bar)
st.sidebar.header("💰 വിനിമയ നിരക്ക് (AED to INR)")
try:
    # ലൈവ് റേറ്റ് ഇന്റർനെറ്റിൽ നിന്ന് എടുക്കുന്നു
    currency_data = yf.Ticker("AEDINR=X").history(period="1d")
    live_rate = currency_data['Close'].iloc[-1]
    st.sidebar.info(f"ഇന്നത്തെ നിരക്ക്: 1 AED = ₹{live_rate:.2f}")
except:
    live_rate = 22.85  # ഇന്റർനെറ്റ് ലഭ്യമല്ലെങ്കിൽ
    st.sidebar.warning("ഏകദേശ നിരക്ക് ഉപയോഗിക്കുന്നു")

aed_input = st.sidebar.number_input("ദിർഹം ടൈപ്പ് ചെയ്യുക (AED)", min_value=0.0, value=1000.0)
inr_result = aed_input * live_rate
st.sidebar.success(f"നാട്ടിലെ തുക: ₹{inr_result:,.2f}")

# 4. സിഗ്നൽ നൽകുന്ന ഫങ്ക്ഷൻ
def get_signal(df):
    if len(df) < 2: return "കാത്തിരിക്കുക", "grey"
    curr = df['Close'].iloc[-1]
    prev = df['Close'].iloc[-2]
    return ("BUY (വാങ്ങാം) 📈", "green") if curr > prev else ("SELL (വിൽക്കാം) 📉", "red")

# 5. ലൈവ് മാർക്കറ്റ് (Nifty, Crude Oil, Gold)
symbols = {"Nifty 50": "^NSEI", "Crude Oil (INR)": "CL=F", "Gold (INR)": "GC=F"}
main_cols = st.columns(3)

for i, (name, sym) in enumerate(symbols.items()):
    with main_cols[i]:
        df = yf.Ticker(sym).history(period="1d", interval="5m")
        if not df.empty:
            price = df['Close'].iloc[-1]
            # ഇന്ത്യൻ രൂപയിലേക്ക് മാറ്റുന്നു (ഏകദേശം)
            multi = 83.30 if "INR" in name else 1
            final_price = price * multi
            
            sig, color = get_signal(df)
            st.metric(label=name, value=f"₹{final_price:,.2f}")
            st.markdown(f"<h3 style='color: {color}; text-align: center;'>{sig}</h3>", unsafe_allow_html=True)
            st.line_chart(df['Close'])

# 6. സ്മാർട്ട് ചാറ്റ് ബോക്സ്
st.divider()
st.subheader("💬 ബോട്ടിനോട് ചോദിക്കാം")
user_input = st.text_input("മാർക്കറ്റിനെക്കുറിച്ചോ കറൻസിയെക്കുറിച്ചോ ചോദിക്കൂ...")
if user_input:
    if "rate" in user_input.lower() or "നിരക്ക്" in user_input:
        st.write(f"🤖: ഫൈസൽ, ഇന്നത്തെ ലൈവ് നിരക്ക് 1 AED = ₹{live_rate:.2f} ആണ്.")
    elif "crude" in user_input.lower() or "oil" in user_input.lower():
        st.write("🤖: ക്രൂഡ് ഓയിൽ ട്രെൻഡ് ചെക്ക് ചെയ്യുകയാണ്. ചാർട്ട് നോക്കുക.")
    else:
        st.write("🤖: മനസ്സിലായി, ഞാൻ നോക്കിയിട്ട് പറയാം!")
