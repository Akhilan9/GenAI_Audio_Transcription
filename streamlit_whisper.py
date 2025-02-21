import streamlit as st
import whisper
import tempfile
from deep_translator import GoogleTranslator
from gtts import gTTS
import os

# ✅ Ensure this is the first Streamlit command
st.set_page_config(page_title="Audio Transcription & Translation", layout="wide")

# Custom CSS for a modern, visually appealing UI
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
        
        body {
            font-family: 'Poppins', sans-serif;
            background-color: #f7f8fc;
        }
        .stApp {
            background-color: white;
            padding: 40px 40px 30px;
            border-radius: 15px;
            box-shadow: 0px 4px 25px rgba(0, 0, 0, 0.1);
        }
        .sidebar .sidebar-content {
            background-color: #1e3a5f;
            color: white;
            padding: 20px;
            border-radius: 10px;
        }
        .stButton > button {
            border-radius: 12px;
            background: linear-gradient(135deg, #6e8efb, #a777e3);
            color: white;
            font-size: 18px;
            font-weight: bold;
            padding: 12px 24px;
            border: none;
            transition: 0.3s;
            box-shadow: 0px 4px 20px rgba(0, 0, 0, 0.1);
        }
        .stButton > button:hover {
            background: linear-gradient(135deg, #a777e3, #6e8efb);
            transform: scale(1.05);
        }
        .stTextArea, .stSelectbox, .stFileUploader {
            border-radius: 10px;
            padding: 10px;
            border: 1px solid #ccc;
            background-color: #fff;
        }
        .stTextArea {
            background-color: #f0f4ff;
        }
        .stAudio {
            margin-top: 15px;
            border-radius: 8px;
            box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.1);
        }
    </style>
""", unsafe_allow_html=True)

st.title("🎤 Audio Transcription & Translation App")
st.write("Upload an audio file, transcribe it, translate it, and even convert the translation into speech!")

# Upload audio file
audio_file = st.file_uploader("Upload Audio", type=["wav", "mp3", "m4a", "ogg", "flac"])

# Sidebar settings
st.sidebar.header("⚙️ Settings")


# Load Whisper model
@st.cache_resource
def load_model():
    return whisper.load_model("base")

model = load_model()
st.sidebar.success("✅ Whisper Model Loaded")

st.sidebar.subheader("🌍 Select Language for Translation")

# Define language mappings for gTTS
language_map = {
    "English": "en",
    "French": "fr",
    "Spanish": "es",
    "German": "de",
    "Hindi": "hi",
    "Chinese": "zh-CN",
    "Japanese": "ja",
    "Russian": "ru"
}

# Select target language for translation
lang_options = list(language_map.keys())
target_language = st.sidebar.selectbox("Select target language", lang_options, index=0)
target_lang_code = language_map[target_language]

# Create session state variables
if "transcribed_text" not in st.session_state:
    st.session_state.transcribed_text = ""

if "translated_text" not in st.session_state:
    st.session_state.translated_text = ""

# Store audio file content in memory
audio_bytes = None
if audio_file:
    audio_bytes = audio_file.read()  # Read the file once to store in memory

# Add Text Formatting Options
text_format = st.selectbox("Choose a text format", options=["None", "Bold", "Italic", "Underline", "Uppercase", "Lowercase"])
font_style = st.selectbox("Choose a font style", options=["Poppins", "Arial", "Times New Roman", "Courier New", "Verdana"])
font_size = st.selectbox("Choose a font size", options=["Small", "Medium", "Large"])

# Transcribe Button
if st.button("📝 Transcribe Audio"):
    if audio_file is not None:
        st.info("🔄 Processing audio file...")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            temp_audio.write(audio_bytes)
            temp_audio_path = temp_audio.name

        st.info("⏳ Transcribing...")
        transcription = model.transcribe(temp_audio_path)
        st.session_state.transcribed_text = transcription["text"]

        st.success("✅ Transcription Complete")

        # Apply selected text formatting
        formatted_text = st.session_state.transcribed_text

        if text_format == "Bold":
            formatted_text = f"<b>{formatted_text}</b>"  # Apply HTML bold formatting
        elif text_format == "Italic":
            formatted_text = f"<i>{formatted_text}</i>"  # Apply HTML italic formatting
        elif text_format == "Underline":
            formatted_text = f"<u>{formatted_text}</u>"  # Use HTML for underline
        elif text_format == "Uppercase":
            formatted_text = formatted_text.upper()
        elif text_format == "Lowercase":
            formatted_text = formatted_text.lower()

        # Font Style and Size Adjustment
        font_style_map = {
            "Poppins": "Poppins, sans-serif",
            "Arial": "Arial, sans-serif",
            "Times New Roman": "Times New Roman, serif",
            "Courier New": "Courier New, monospace",
            "Verdana": "Verdana, sans-serif"
        }

        # Define font size options
        font_size_map = {
            "Small": "12px",
            "Medium": "16px",
            "Large": "20px"
        }

        # Apply font style and size using inline CSS
        font_style_selected = font_style_map.get(font_style, "Poppins, sans-serif")
        font_size_selected = font_size_map.get(font_size, "16px")

        # Display the formatted text with font style and size applied
        st.markdown(
            f'<p style="font-family: {font_style_selected}; font-size: {font_size_selected};">{formatted_text}</p>',
            unsafe_allow_html=True
        )
    else:
        st.error("⚠️ Please upload an audio file.")

# Translate Button (Only enabled after transcription)
if st.button("🌍 Translate Text") and st.session_state.transcribed_text:
    st.info("🔄 Translating...")
    st.session_state.translated_text = GoogleTranslator(source="auto", target=target_lang_code).translate(st.session_state.transcribed_text)

    st.success(f"✅ Translation to {target_language} Complete")
    st.text_area(f"📝 Translated Text ({target_language})", st.session_state.translated_text, height=150)

    # Convert translated text to speech
    tts = gTTS(st.session_state.translated_text, lang=target_lang_code)
    tts_audio_path = "translated_audio.mp3"
    tts.save(tts_audio_path)

    st.audio(tts_audio_path, format='audio/mp3')
    st.success("🎧 Audio Translation Ready")

    # Download button for the translated audio
    with open(tts_audio_path, "rb") as audio_file:
        st.download_button(
            label="Download Translated Audio",
            data=audio_file,
            file_name="translated_audio.mp3",
            mime="audio/mp3"
        )

# Play the uploaded audio (using the stored memory content)
if audio_bytes:
    st.audio(audio_bytes, format='audio/mp3')
