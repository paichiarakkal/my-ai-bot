# --- 5. AI AGENT (VOICE + TEXT) ---
elif page == "🤖 AI Agent":
    st.title("🤖 PAICHI Business AI Agent")
    st.write("ചാറ്റ് വഴിയോ ശബ്ദം വഴിയോ (Voice) നിങ്ങളുടെ ബിസിനസ്സ് കാര്യങ്ങൾ ചെയ്യാം.")
    
    if not GROQ_API_KEY:
        st.error("Groq API Key ലഭ്യമല്ല!")

    # ചാറ്റ് ക്ലിയർ ചെയ്യാനുള്ള ബട്ടൺ
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

    # ചാറ്റ് ഹിസ്റ്ററി കാണിക്കുന്നു
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # വോയ്സ് ഇൻപുട്ട് (Record Audio)
    st.write("---")
    st.write("🎤 **അല്ലെങ്കിൽ ഇവിടെ ക്ലിക്ക് ചെയ്ത് സംസാരിക്കാം (ശബ്ദം കേൾക്കാൻ അടുത്ത് പിടിക്കുക):**")
    audio_value = st.audio_input("Record a voice message")

    prompt = None

    if audio_value:
        with st.spinner("ശബ്ദം കേൾക്കുന്നു..."):
            try:
                client = Groq(api_key=GROQ_API_KEY)
                # ശബ്ദം ടെക്സ്റ്റ് ആക്കി മാറ്റുന്നു (language="ml" കളഞ്ഞു, prompt കൊടുത്തു)
                transcription = client.audio.transcriptions.create(
                    file=(audio_value.name, audio_value.read()),
                    model=WHISPER_MODEL,
                    response_format="text",
                    prompt="This is a grocery shop business. Words used: Shop 1, Shop 2, Sales, Expense, Salary, Stock, Rupees, Aayi, Undayi."
                )
                prompt = transcription.strip()
                if prompt:
                    st.info(f"🗣️ നിങ്ങൾ പറഞ്ഞത്: **{prompt}**")
                else:
                    st.warning("ശബ്ദം കേട്ടില്ല, ദയവായി വീണ്ടും പറയുക.")
            except Exception as e:
                st.error(f"Audio Error: {str(e)}")

    # ടെക്സ്റ്റ് ഇൻപുട്ട്
    text_prompt = st.chat_input("ഇവിടെ ടൈപ്പ് ചെയ്യാം (അല്ലെങ്കിൽ മുകളിൽ വോയ്സ് റെക്കോർഡ് ചെയ്യാം)")

    if text_prompt:
        prompt = text_prompt

    if prompt:
        # യൂസർ മെസ്സേജ് ആഡ് ചെയ്യുന്നു
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.spinner("AI ആലോചിക്കുന്നു..."):
            try:
                ai_reply, tool_used = process_ai_agent(prompt)
                
                st.session_state.messages.append({"role": "assistant", "content": ai_reply})
                with st.chat_message("assistant"):
                    st.markdown(ai_reply)
                    
                if tool_used:
                    st.rerun()
            except Exception as e:
                st.error(f"AI Error: {str(e)}")