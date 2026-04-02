elif choice == "Commodities":
    st.title("🛢️ Commodities & Gold")
    
    if st.button("🇮🇳 Crude Oil (MCX India Price)"):
        with st.spinner('Fetching MCX Data...'):
            d = get_data("CL=F") # Global Price
            if d:
                # MCX ഏകദേശ വില കണക്കാക്കുന്ന രീതി:
                # Global Price * USDINR * 10 (Multiplier)
                mcx_price = d['price'] * 83.5 * 1.25 
                
                st.metric("Crude Oil MCX (Approx)", f"₹{mcx_price:.2f}")
                st.write(f"Global RSI: {d['rsi']:.2f}")
                
                # നീ ഉപയോഗിക്കുന്ന സൂപ്പർ ട്രെൻഡ് പോലെ സിഗ്നൽ നൽകുന്നു
                if d['rsi'] < 35: 
                    st.success("SIGNAL: BUY 🟢 (Oversold)")
                elif d['rsi'] > 65: 
                    st.error("SIGNAL: SELL 🔴 (Overbought)")
                else: 
                    st.warning("SIGNAL: WAIT ⏳")
