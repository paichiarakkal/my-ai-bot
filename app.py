import streamlit as st

# ആപ്പിന്റെ തലക്കെട്ട്
st.title("PAICHI GOLD – Live P&L Tracker 📈")
st.markdown("---")

# 1. നിലവിലെ പൊസിഷനുകളുടെ വിവരങ്ങൾ നൽകാനുള്ള ഇൻപുട്ടുകൾ (ഉദാഹരണത്തിന്)
st.subheader("📊 ട്രേഡ് വിവരങ്ങൾ നൽകുക")

col1, col2, col3 = st.columns(3)

with col1:
    buy_price = st.number_input("വാങ്ങിയ വില (Buy Price):", min_value=0.0, value=100.0, step=0.5)
with col2:
    current_price = st.number_input("ഇപ്പോഴത്തെ വില (LTP):", min_value=0.0, value=120.0, step=0.5)
with col3:
    quantity = st.number_input("ക്വാണ്ടിറ്റി (Quantity):", min_value=0, value=50, step=1)

# --- P&L കണക്കുകൂട്ടലുകൾ ---
# ടോട്ടൽ ഇൻവെസ്റ്റ്‌മെന്റ്
total_investment = buy_price * quantity
# നിലവിലെ ആകെ മൂല്യം
current_value = current_price * quantity

# യഥാർത്ഥ ലാഭം/നഷ്ടം (P&L)
pnl = current_value - total_investment

# ശതമാനം (Percentage Change)
if total_investment > 0:
    pnl_percentage = (pnl / total_investment) * 100
else:
    pnl_percentage = 0.0

st.markdown("---")

# 2. പ്രോഫിറ്റ് & ലോസ് ഡിസ്പ്ലേ സെക്ഷൻ
st.subheader("💰 Today's Realized P&L")

# ലാഭമാണോ നഷ്ടമാണോ എന്ന് നോക്കി ചിഹ്നം മാറ്റാൻ
if pnl > 0:
    pnl_label = f"🟢 Profit: +₹{pnl:,.2f}"
    delta_text = f"+{pnl_percentage:.2f}%"
elif pnl < 0:
    pnl_label = f"🔴 Loss: -₹{abs(pnl):,.2f}"
    delta_text = f"{pnl_percentage:.2f}%"
else:
    pnl_label = "⚪ No Profit / No Loss"
    delta_text = "0.00%"

# Streamlit മെട്രിക്സ് ഉപയോഗിച്ച് ബോക്സ് ഉണ്ടാക്കുന്നു
st.metric(
    label="ആകെ ലാഭം / നഷ്ടം (P&L)", 
    value=f"₹{pnl:,.2f}", 
    delta=delta_text
)

# അധിക ഭംഗിക്കായി ഒരു കളർ ബോക്സ് കൂടി താഴെ നൽകാം
if pnl > 0:
    st.success(f"സൂപ്പർ ഭായ്! നിങ്ങൾ ഇപ്പോൾ **₹{pnl:,.2f}** ലാഭത്തിലാണ്! ഇനി 'Kill Switch' ഓർത്തോളൂ! 😉")
elif pnl < 0:
    st.error(f"ശ്രദ്ധിക്കുക ഭായ്! നിങ്ങൾ ഇപ്പോൾ **₹{abs(pnl):,.2f}** നഷ്ടത്തിലാണ്. അച്ചടക്കം പാലിക്കുക!")
