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
        
        # നിങ്ങളുടെ പഴയ കോൺഫിഗറേഷൻ (മറ്റ് സോഷ്യൽ മീഡിയകൾക്കായി)
        ydl_opts_old = {
            'format': 'best[ext=mp4]/best', 
            'nocheckcertificate': True,
            'quiet': True,
            'no_warnings': True,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
            }
        }
        
        # YouTube-ൽ നല്ല വ്യക്തതയുള്ള (HD) വീഡിയോകൾക്ക് വേണ്ടിയുള്ള പുതിയ കോൺഫിഗറേഷൻ
        ydl_opts_hd = {
            'format': 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best',
            'nocheckcertificate': True,
            'quiet': True,
            'no_warnings': True,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
            }
        }
        
        # ലിങ്ക് YouTube ആണെങ്കിൽ HD ഓപ്ഷൻ എടുക്കുന്നു, അല്ലെങ്കിൽ പഴയ ഓപ്ഷൻ എടുക്കുന്നു
        if "youtube.com" in url or "youtu.be" in url:
            ydl_opts = ydl_opts_hd
        else:
            ydl_opts = ydl_opts_old
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # ഫയൽ സെർവറിലേക്ക് ഡൗൺലോഡ് ചെയ്യാതെ അതിന്റെ വിവരങ്ങൾ മാത്രം എടുക്കുന്നു
                info = ydl.extract_info(url, download=False)
                video_url = info.get('url')
                title = info.get('title', 'video')
                
                # വീഡിയോയുടെ ടൈറ്റിൽ ക്ലീൻ ചെയ്ത് ഫയൽ നെയിം ഉണ്ടാക്കുന്നു
                clean_title = "".join([c for c in title if c.isalpha() or c.isdigit() or c==' ']).rstrip()
                filename = f"{clean_title}.mp4"
                
            if video_url:
                st.success("വീഡിയോ റെഡിയായിട്ടുണ്ട്!")
                # ഡൗൺലോഡ് ലിങ്ക് നേരിട്ട് Streamlit ബട്ടണിലേക്ക് നൽകുന്നു
                st.video(video_url) # ആപ്പിൽ തന്നെ വീഡിയോ പ്ലേ ചെയ്തു നോക്കാനും സാധിക്കും
                
                # ബോണസ്: ക്ലൗഡിൽ പ്രശ്നമില്ലാതെ വർക്ക് ആകാൻ ഒരു ഡൗൺലോഡ് ബട്ടൺ ലിങ്ക് കൂടി നൽകാം
                st.markdown(f'[ഫോണിലേക്ക് ഡൗൺലോഡ് ചെയ്യാൻ ഇവിടെ ഞെക്കുക ⬇️]({video_url})')
            else:
                st.error("വീഡിയോ യുആർഎൽ കണ്ടെത്താൻ കഴിഞ്ഞില്ല.")
                
        except Exception as e:
            st.error(f"ഡൗൺലോഡ് ചെയ്യാൻ സാധിച്ചില്ല. ലിങ്ക് കൃത്യമാണോ എന്ന് പരിശോധിക്കുക. എറർ: {e}")
    else:
        st.warning("ദയവായി ഒരു വീഡിയോ ലിങ്ക് നൽകുക!")
