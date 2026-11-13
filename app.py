def analyze_images_with_groq(images_bytes_list, is_video=False):
    if not GROQ_API_KEY: 
        return False, "Groq Key missing!"
    try:
        client = Groq(api_key=GROQ_API_KEY)
        
        # വീഡിയോ ആണെങ്കിൽ ആളുകളെ എണ്ണാൻ, ഫോട്ടോ ആണെങ്കിൽ സ്റ്റോക്ക് എണ്ണാൻ
        if is_video:
            prompt_text = "Analyze these CCTV video frames. Count the exact number of people visible and describe their actions. Provide the report in Malayalam."
        else:
            prompt_text = "Count the exact number of items/products visible in this image. Tell me the name of the item and the quantity. Provide the report in Malayalam."
        
        content_list = [{"type": "text", "text": prompt_text}]
        
        for img in images_bytes_list:
            content_list.append({
                "type": "image_url", 
                "image_url": {"url": f"data:image/jpeg;base64,{base64.b64encode(img).decode('utf-8')}"}
            })
            
        res = client.chat.completions.create(
            model=VISION_MODEL, 
            messages=[{"role": "user", "content": content_list}], 
            max_tokens=800
        ).choices[0].message.content
        
        # മലയാളത്തിലേക്ക് തർജ്ജമ ചെയ്യുന്നു
        prompt_ml = f"Translate this report into natural Malayalam. Do NOT translate brand names.\n\n{res}"
        
        final_res = client.chat.completions.create(
            model=AGENT_MODEL, 
            messages=[{"role": "user", "content": prompt_ml}], 
            max_tokens=800
        ).choices[0].message.content
        
        return True, final_res
    except Exception as e: 
        return False, f"Vision Error: {str(e)}"