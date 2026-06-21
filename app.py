import streamlit as st
import yt_dlp
import os

# ആപ്പിന്റെ പുതിയ തലക്കെട്ട്
st.title("All-in-One Video Downloader 🚀")
st.write("YouTube, Instagram, Facebook, TikTok തുടങ്ങി ഏത് വീഡിയോ ലിങ്കും താഴെ പേസ്റ്റ് ചെയ്ത് ഡൗൺലോഡ് ചെയ്യാം.")

# ലിങ്ക് വാങ്ങാനുള്ള ബോക്സ്
url = st.text_input("വീഡിയോ ലിങ്ക് ഇവിടെ പേസ്റ്റ് ചെയ്യുക:")

if st.button("Download Video"):
    if url:
        st.info("വീഡിയോ പ്രോസസ്സ് ചെയ്യുന്നു, ദയവായി കാത്തിരിക്കുക...")
        
        # എല്ലാ വെബ്‌സൈറ്റുകളെയും സപ്പോർട്ട് ചെയ്യാനും ബ്ലോക്കുകൾ ഒഴിവാക്കാനുമുള്ള അഡ്വാൻസ്ഡ് കോൺഫിഗറേഷൻ
        ydl_opts = {
            # സാധ്യമായ ഏറ്റവും മികച്ച സിംഗിൾ ഫയൽ MP4 ഫോർമാറ്റ് തിരഞ്ഞെടുക്കുന്നു
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best', 
            'outtmpl': '%(title)s.%(ext)s',
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
            'quiet': True,
            'no_warnings': True,
            'source_address': '0.0.0.0', # സെർവർ ഐപി പ്രശ്നങ്ങൾ കുറയ്ക്കാൻ
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
            }
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # ലിങ്കിൽ നിന്നുള്ള വീഡിയോ വിവരങ്ങൾ എടുത്ത് ഡൗൺലോഡ് ചെയ്യുന്നു
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                
            st.success("വീഡിയോ വിജയകരമായി ഡൗൺലോഡ് ചെയ്തു!")
            
            # ഫോണിലേക്ക് സേവ് ചെയ്യാനുള്ള ബട്ടൺ
            with open(filename, "rb") as file:
                st.download_button(
                    label="ഫോണിലേക്ക് സേവ് ചെയ്യുക ⬇️",
                    data=file,
                    file_name=filename,
                    mime="video/mp4"
                )
                
            # ഉപയോഗത്തിന് ശേഷം സെർവറിലെ താൽക്കാലിക ഫയൽ ഡിലീറ്റ് ചെയ്യുന്നു
            os.remove(filename)
                
        except Exception as e:
            st.error(f"ഡൗൺലോഡ് ചെയ്യാൻ സാധിച്ചില്ല. ലിങ്ക് കൃത്യമാണോ എന്ന് പരിശോധിക്കുക. എറർ: {e}")
    else:
        st.warning("ദയവായി ഒരു വീഡിയോ ലിങ്ക് നൽകുക!")
