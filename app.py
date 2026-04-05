if mode == "MARKET":
    # Rocket Animation (ഇത് അവിടെ തന്നെ നിൽക്കട്ടെ)
    p_holder = st.empty()
    for i in range(1, 25):
        p_holder.markdown(f"### {'&nbsp;' * i} 🚀 *AI Analyzing {st.session_state.sel[1]}...*")
        time.sleep(0.08)
    p_holder.empty()

    sym, name, multi = st.session_state.sel
    data = get_live_data(sym)
    if data:
        st.subheader(f"📍 {name}")
        lp, ap = data['p'] * multi, data['ai'] * multi
        
        # ഗ്രാഫ് ഒഴിവാക്കി, വിലകൾ മാത്രം കാണിക്കുന്നു
        c1, c2 = st.columns(2)
        c1.metric("ലൈവ് വില", f"₹{lp:,.2f}")
        c2.metric("AI പ്രവചനം", f"₹{ap:,.2f}")
        
        # --- പഴയ st.line_chart ഇവിടെ നിന്ന് ഒഴിവാക്കി ---
