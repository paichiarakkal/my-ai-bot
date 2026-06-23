import streamlit as st
import yt_dlp

# ആപ്പിന്റെ പുതിയ തലക്കെട്ട്
st.title("All-in-One Video Downloader 🚀")
st.write("YouTube, Instagram, Facebook, TikTok തുടങ്ങി ഏത് വീഡിയോ ലിങ്കും താഴെ പേസ്റ്റ് ചെയ്ത് ഡൗൺലോഡ് ചെയ്യാം.")

# ലിങ്ക് വാങ്ങാനുള്ള ബോക്സ്
url = st.text_input("വീഡിയോ ലിങ്ക് ഇവിടെ പേസ്റ്റ് ചെയ്യുക:")

if st.button("Download Video"):
    if url:
        st.info("വീഡിയോ പ്രോസസ്സ് ചെയ്യുന്നു, ദയവായി കാത്തിരിക്കുക...")
        
        # ഇൻസ്റ്റാഗ്രാം, യൂട്യൂബ് എന്നിവയ്ക്ക് കൂടുതൽ അനുയോജ്യമായ കോൺഫിഗറേഷൻ
        ydl_opts = {
            # ഓഡിയോയും വീഡിയോയും ചേർന്ന ഏറ്റവും നല്ല ഫോർമാറ്റ് തിരഞ്ഞെടുക്കുന്നു
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'nocheckcertificate': True,
            'quiet': True,
            'no_warnings': True,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
            }
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                video_url = info.get('url')
                title = info.get('title', 'video')
                
                clean_title = "".join([c for c in title if c.isalpha() or c.isdigit() or c==' ']).rstrip()
                
            if video_url:
                st.success(f"🎬 വീഡിയോ കണ്ടെത്തി: {clean_title}")
                
                # ആപ്പിൽ തന്നെ വീഡിയോ പ്ലേ ചെയ്യാനുള്ള സൗകര്യം
                st.video(video_url)
                
                # ഡൗൺലോഡ് ചെയ്യാനുള്ള ഡയറക്റ്റ് ബട്ടൺ
                st.write("🔽 താഴെയുള്ള ലിങ്കിൽ റൈറ്റ് ക്ലിക്ക് ചെയ്ത് 'Save link as' കൊടുത്ത് ഡൗൺലോഡ് ചെയ്യാം:")
                st.markdown(f'<a href="{video_url}" target="_blank" style="display: inline-block; padding: 10px 20px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 4px;">വീഡിയോ സേവ് ചെയ്യാൻ ഇവിടെ ഞെക്കുക</a>', unsafe_allow_html=True)
            else:
                st.error("വീഡിയോ യുആർഎൽ കണ്ടെത്താൻ കഴിഞ്ഞില്ല.")
                
        except Exception as e:
            st.error(f"ഡൗൺലോഡ് ചെയ്യാൻ സാധിച്ചില്ല. ഇൻസ്റ്റാഗ്രാം പ്രൈവറ്റ് അക്കൗണ്ടുകളിലെ ലിങ്ക് ആണോ അല്ലെങ്കിൽ ലിങ്ക് മാറിയതാണോ എന്ന് പരിശോധിക്കുക.")
            # കൂടുതൽ വിവരങ്ങൾക്ക് വേണമെങ്കിൽ താഴെയുള്ള വരി അൺകമന്റ് ചെയ്യാം
            # st.error(f"Error details: {e}")
    else:
        st.warning("ദയവായി ഒരു വീഡിയോ ലിങ്ക് നൽകുക!")
