import streamlit as st
import yt_dlp
import requests
import io

# --- 1. PAGE CONFIG & THEME ---
st.set_page_config(page_title="All-in-One Downloader", page_icon="🚀", layout="centered")

st.title("All-in-One Video Downloader 🚀")
st.write("YouTube, Instagram, Facebook തുടങ്ങി ഏത് വീഡിയോ ലിങ്കും താഴെ പേസ്റ്റ് ചെയ്ത് ഡൗൺലോഡ് ചെയ്യാം.")

# --- 2. USER INPUT ---
url = st.text_input("വീഡിയോ ലിങ്ക് ഇവിടെ പേസ്റ്റ് ചെയ്യുക:", placeholder="https://...")

# --- 3. DOWNLOAD LOGIC ---
if st.button("Download Video", use_container_width=True):
    if url:
        st.info("വീഡിയോ പ്രോസസ്സ് ചെയ്യുന്നു, ദയവായി காത്തിരിക്കുക...")
        
        # yt_dlp കോൺഫിഗറേഷൻ
        ydl_opts = {
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
                # ഫയൽ ഡൗൺലോഡ് ചെയ്യാതെ ലിങ്ക് മാത്രം എക്സ്ട്രാക്റ്റ് ചെയ്യുന്നു
                info = ydl.extract_info(url, download=False)
                video_url = info.get('url')
                title = info.get('title', 'video')
                
                # ഫയൽ നെയിമിലെ സ്പെഷ്യൽ ക്യാരക്ടറുകൾ ഒഴിവാക്കുന്നു
                clean_title = "".join([c for c in title if c.isalpha() or c.isdigit() or c==' ']).rstrip()
                filename = f"{clean_title}.mp4"
                
            if video_url:
                # വീഡിയോ ലിങ്കിൽ നിന്ന് ഡാറ്റ മെമ്മറിയിലേക്ക് ഡൗൺലോഡ് ചെയ്യുന്നു
                with st.spinner("ഡൗൺലോഡ് ബട്ടൺ തയ്യാറാക്കുന്നു..."):
                    response = requests.get(video_url, stream=True, timeout=30)
                    video_bytes = io.BytesIO(response.content)
                
                st.success("🎬 വീഡിയോ വിജയകരമായി പ്രോസസ്സ് ചെയ്തു!")
                
                # ആപ്പിൽ പ്ലേ ചെയ്യാനുള്ള പ്ലെയർ
                st.video(video_bytes)
                
                st.markdown("---")
                
                # ഫോണിലേക്ക് നേരിട്ട് സേവ് ചെയ്യാനുള്ള ഒഫീഷ്യൽ ബട്ടൺ
                st.download_button(
                    label="📥 ഫോണിലേക്ക് ഡൗൺലോഡ് ചെയ്യാം (Save Video)",
                    data=video_bytes,
                    file_name=filename,
                    mime="video/mp4",
                    use_container_width=True
                )
            else:
                st.error("വീഡിയോ യുആർഎൽ കണ്ടെത്താൻ കഴിഞ്ഞില്ല. ലിങ്ക് ഒരിക്കൽ കൂടി പരിശോധിക്കുക.")
                
        except Exception as e:
            st.error("ഡൗൺലോഡ് ചെയ്യാൻ സാധിച്ചില്ല! ഇൻസ്റ്റാഗ്രാം പ്രൈവറ്റ് ലിങ്ക് ആണോ അതോ ലിങ്ക് മാറിയതാണോ എന്ന് പരിശോധിക്കുക.")
            st.info("ശ്രദ്ധിക്കുക: Render-ൽ ഹോസ്റ്റ് ചെയ്യുമ്പോൾ ഇൻസ്റ്റാഗ്രാം ചിലപ്പോൾ ഐപി ബ്ലോക്ക് ചെയ്യാൻ സാധ്യതയുണ്ട്.")
    else:
        st.warning("ദയവായി ഒരു വീഡിയോ ലിങ്ക് നൽകുക!")
