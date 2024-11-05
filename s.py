import streamlit as st
import google.generativeai as genai
import speech_recognition as sr
import pyttsx3
import threading

# Configure the API key directly
genai.configure(api_key="AIzaSyBN9ZlpzLLoHklPYo7d_7y7Uw9UW1wlE9E")

# Function to load the Gemini Pro model and get a response
model = genai.GenerativeModel("gemini-pro")
chat = model.start_chat(history=[])

def get_gemini_response(question):
    response = chat.send_message(question, stream=True)
    return response

# Initialize Text-to-Speech engine
tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', 150)  # Adjust the speaking rate if necessary

def speak_text(text):
    def run_tts():
        tts_engine.say(text)
        tts_engine.runAndWait()
    
    # Run TTS in a separate thread to prevent blocking the main thread
    tts_thread = threading.Thread(target=run_tts)
    tts_thread.start()

# Streamlit app configuration
st.set_page_config(page_title="eleAi")
st.markdown("<h1 style='text-align: center; color: cyan;'>Welcome to eleAi</h1>", unsafe_allow_html=True)

# CSS for Jarvis-like UI
st.markdown("""
    <style>
    .stTextInput, .stButton, .stMarkdown {
        font-size: 18px;
    }
    .jarvis-container {
        border: 2px solid cyan;
        border-radius: 10px;
        padding: 20px;
        background-color: #1e1e1e;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Options for input mode: Text or Voice
mode = st.radio("Select Input Mode:", options=["Speak", "Type"], index=1)

# Voice input handler
if mode == "Speak":
    if st.button("Record Your Question"):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            st.info("Listening...")
            try:
                audio = recognizer.listen(source, timeout=5)
                input_text = recognizer.recognize_google(audio)
                st.success(f"You said: {input_text}")

                response = get_gemini_response(input_text)
                st.subheader("Response:")
                full_response = ""

                for chunk in response:
                    if hasattr(chunk, 'text') and chunk.text:
                        st.write(chunk.text)
                        full_response += chunk.text
                    else:
                        st.warning("No valid response received. The model might have detected copyrighted content.")

                # Speak the response if mode is "Speak"
                if full_response:
                    speak_text(full_response)

            except sr.UnknownValueError:
                st.error("Sorry, I could not understand your voice.")
            except sr.RequestError:
                st.error("Could not request results; please check your internet connection.")

# Text input handler
elif mode == "Type":
    input_text = st.text_input("Type your question and press Enter:", key="input", on_change=lambda: st.session_state.update({'response_trigger': True}))

    if st.session_state.get('response_trigger', False) and input_text:
        st.session_state['response_trigger'] = False  # Reset the trigger
        response = get_gemini_response(input_text)
        st.subheader("Response:")
        full_response = ""
        for chunk in response:
            if hasattr(chunk, 'text') and chunk.text:
                st.write(chunk.text)
                full_response += chunk.text
            else:
                st.warning("No valid response received. The model might have detected copyrighted content.")

        # Respond only in text for "Type" mode
