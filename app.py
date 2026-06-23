import streamlit as st
import yt_dlp
import io

# ആപ്പിന്റെ പുതിയ തലക്കെട്ട്
st.title("All-in-One Video Downloader 🚀")
st.write("YouTube, Instagram, Facebook, TikTok തുടങ്ങി ഏത് വീഡിയോ ലിങ്കും താഴെ പേസ്റ്റ് ചെയ്ത് ഡൗൺലോഡ് ചെയ്യാം.")

# ലിങ്ക് വാങ്ങാനുള്ള ബോക്സ്
url = st.text_input("വീഡിയോ ലിങ്ക് ഇവിടെ പേസ്റ്റ് ചെയ്യുക:")

if st.button("Download Video"):
    if url:
        st.info("വീഡിയോ പ്രോസസ്സ് ചെയ്യുന്നു, ദയവായി കാത്തിരിക്കുക...")
        
        # ക്ലൗഡ് പ്ലാറ്റ്‌ഫോമുകളിൽ ഏറ്റവും നന്നായി വർക്ക് ചെയ്യുന്ന ലൈറ്റ് വെയ്റ്റ് കോൺഫിഗറേഷൻ
        ydl_opts = {
            'format': 'best', # ഏറ്റവും അനുയോജ്യമായ സിംഗിൾ ഫയൽ ഫോർമാറ്റ് എടുക്കുന്നു
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
                
                # ചിലപ്പോൾ 'url' നേരിട്ട് കിട്ടാത്ത അവസ്ഥ വന്നാൽ formats-ൽ നിന്ന് എടുക്കാൻ വേണ്ടിയുള്ള മാറ്റം
                video_url = info.get('url')
                if not video_url and 'formats' in info:
                    video_url = info['formats'][-1].get('url')
                    
                title = info.get('title', 'video')
                clean_title = "".join([c for c in title if c.isalpha() or c.isdigit() or c==' ']).rstrip()
                filename = f"{clean_title}.mp4"
                
            if video_url:
                st.success("വീഡിയോ റെഡിയായിട്ടുണ്ട്!")
                st.video(video_url) 
                st.markdown(f'[ഫോണിലേക്ക് ഡൗൺലോഡ് ചെയ്യാൻ ഇവിടെ ഞെക്കുക ⬇️]({video_url})')
            else:
                st.error("വീഡിയോ യുആർഎൽ കണ്ടെത്താൻ കഴിഞ്ഞില്ല. യൂട്യൂബ് സെർവർ തടസ്സപ്പെടുത്തിയതാകാം.")
                
        except Exception as e:
            st.error(f"ഡൗൺലോഡ് ചെയ്യാൻ സാധിച്ചില്ല. എറർ: {e}")
    else:
        st.warning("ദയവായി ഒരു വീഡിയോ ലിങ്ക് നൽകുക!")
