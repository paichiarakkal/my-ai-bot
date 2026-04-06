if menu == "📈 LIVE MARKET":
    st.markdown("<h1>MCX CRUDE OIL: LIVE CHART ⚡</h1>", unsafe_allow_html=True)
    
    # Investing.com MCX Crude Oil (Symbol ID: 8849)
    # ഇത് നിന്റെ ആപ്പിനുള്ളിൽ നേരിട്ട് ലോഡ് ആകും
    investing_chart = """
    <div style="height:550px;">
        <iframe src="https://it.widgets.investing.com/live-charts-widget?force_lang=1&s=8849" width="100%" height="500" frameborder="0" allowtransparency="true" marginwidth="0" marginheight="0"></iframe>
        <div style="width:100%;text-align:center;font-size:12px;color:#FFD700;padding-top:5px;">
            <a href="https://www.investing.com/" target="_blank" style="color:#FFD700;text-decoration:none;">Live Charts provided by Investing.com</a>
        </div>
    </div>
    """
    st.components.v1.html(investing_chart, height=550)
