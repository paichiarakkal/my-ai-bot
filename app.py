# --- SHELF MONITOR LOGIC (UPDATED) ---
def analyze_shelf_changes(morning_bytes, evening_bytes):
    if not GROQ_API_KEY:
        return False, "Groq API Key missing!"
    try:
        client = Groq(api_key=GROQ_API_KEY)
        
        b64_morning = base64.b64encode(morning_bytes).decode('utf-8')
        b64_evening = base64.b64encode(evening_bytes).decode('utf-8')
        
        # AI-യോട് കർശനമായ നിർദ്ദേശം നൽകുന്നു
        prompt_text_en = (
            "You are an expert retail auditor. Compare these two images of the same shelf (Morning vs Evening). "
            "IMPORTANT: If the images are identical or there are NO noticeable changes in the stock, you MUST explicitly say: "
            "'No changes detected. The shelf looks exactly the same.' Do NOT invent or imagine differences. "
            "If there are actual changes, list which items are reduced or moved."
        )
        
        content_list = [
            {"type": "text", "text": prompt_text_en},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_morning}"}},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_evening}"}}
        ]
        
        completion_vision = client.chat.completions.create(
            model=VISION_MODEL,
            messages=[{"role": "user", "content": content_list}],
            max_tokens=800,
            temperature=0.1  # ഇത് കൊടുത്താൽ AI സ്വന്തം ഇഷ്ടത്തിന് കാര്യങ്ങൾ സങ്കൽപ്പിക്കില്ല
        )
        english_report = completion_vision.choices[0].message.content

        prompt_text_ml = (
            "You are an expert translator. Translate the following shelf comparison report into natural, easy-to-understand Malayalam. "
            "Do NOT translate English brand names or product names. Keep the format clean and professional.\n\n"
            f"English Report:\n{english_report}"
        )

        completion_translate = client.chat.completions.create(
            model=AGENT_MODEL,
            messages=[{"role": "user", "content": prompt_text_ml}],
            max_tokens=800
        )
        return True, completion_translate.choices[0].message.content
    except Exception as e:
        return False, f"Shelf Analysis Error: {str(e)}"