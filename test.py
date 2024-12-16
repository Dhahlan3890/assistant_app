import streamlit as st
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, WebRtcMode
import numpy as np
from gradio_client import Client, handle_file
import speech_recognition as sr
import os

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize Gradio Clients
client_tts = Client("mrfakename/E2-F5-TTS")
client_chat = Client("suayptalha/Chat-with-FastLlama")

# Mapping of samples to system messages
samples = ["madara", "girl", "tony_stark", "tobi", "obito", "deadpool"]

sample_to_message = {
    "girl": """You are a girl who loves to flirt with everyone...""",  # Truncated for brevity
    "madara": """You are Madara Uchiha, a legendary and feared shinobi...""",
    "tony_stark": """You are Tony Stark, a billionaire with a proud mentality...""",
    "tobi": """You are Tobi, a mysterious and mischievous character...""",
    "obito": """You are Obito Uchiha, a man whose life has been shaped by profound loss...""",
    "deadpool": """You are Deadpool, the wisecracking, fourth-wall-breaking anti-hero..."""
}

# Audio Processor for WebRTC
class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def recv(self, frame):
        audio_array = frame.to_ndarray()
        audio_bytes = audio_array.tobytes()

        try:
            # Recognize speech using Google Speech Recognition
            with sr.AudioFile(audio_bytes) as source:
                audio_data = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio_data)
                return text
        except sr.UnknownValueError:
            return "Google Speech Recognition could not understand audio."
        except sr.RequestError as e:
            return f"Error with Google Speech Recognition: {e}"

# Text-to-Speech Conversion
def text_to_speech(text, sample):
    try:
        result = client_tts.predict(
            ref_audio_input=handle_file(f'input/{sample}.mp3'),
            ref_text_input="",
            gen_text_input=text,
            remove_silence=False,
            cross_fade_duration_slider=0.15,
            speed_slider=1,
            api_name="/basic_tts"
        )
        audio_file = open(result[0], "rb")
        audio_bytes = audio_file.read()
        st.audio(audio_bytes, format="audio/mp3", autoplay=True)
    except Exception as e:
        st.error(f"Text-to-Speech conversion failed: {e}")

# Streamlit Layout
st.title("Interactive Chat with Streamlit")

# Sidebar for Settings
with st.sidebar:
    st.header("Settings")
    selected_sample = st.selectbox("Select Voice Sample", samples)
    param_4 = st.slider("Max Tokens", min_value=1, max_value=1024, value=256)
    interaction_mode = st.radio("Interaction Mode", ["Text Input", "Microphone Input", "File Upload"])

# Display Chat History
st.write("### Chat History")
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.write(f"**You:** {msg['content']}")
    else:
        st.write(f"**Bot ({selected_sample}):** {msg['content']}")

# Interaction based on selected mode
if interaction_mode == "Text Input":
    with st.form(key="text_input_form"):
        user_input = st.text_input("Enter your message:")
        submit_button = st.form_submit_button("Send")
    
    if submit_button and user_input:
        # Display user message in chat
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Generate system message
        system_message = sample_to_message[selected_sample]
        
        try:
            # Get response from the model
            response = client_chat.predict(
                message=user_input,
                system_message=system_message,
                max_tokens=param_4,
                temperature=0.7,
                top_p=0.95,
                api_name="/chat"
            )
            
            # Display bot response in chat
            st.session_state.messages.append({"role": "bot", "content": response})
            
            # Convert response to speech
            text_to_speech(response, selected_sample)
        except Exception as e:
            st.error(f"An error occurred: {e}")

if interaction_mode == "Microphone Input":
    st.write("### Speak into the microphone")
    webrtc_ctx = webrtc_streamer(
        key="speech-recognition",
        mode=WebRtcMode.SENDONLY,
        audio_processor_factory=AudioProcessor,
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
    )

    if webrtc_ctx is None:
        st.error("WebRTC streamer could not be initialized. Check permissions or configuration.")
    elif webrtc_ctx.state.playing and webrtc_ctx.audio_processor:
        st.write("Listening...")
        try:
            transcribed_text = webrtc_ctx.audio_processor.recv()
            st.write(f"Transcribed Text: {transcribed_text}")

            if transcribed_text:
                # Add user message to chat history
                st.session_state.messages.append({"role": "user", "content": transcribed_text})

                # Generate system message based on the selected sample
                system_message = sample_to_message[selected_sample]

                # Get bot response
                response = client_chat.predict(
                    message=transcribed_text,
                    system_message=system_message,
                    max_tokens=param_4,
                    temperature=0.7,
                    top_p=0.95,
                    api_name="/chat"
                )
                # Add bot response to chat history
                st.session_state.messages.append({"role": "bot", "content": response})

                # Convert response to speech
                text_to_speech(response, selected_sample)
        except Exception as e:
            st.error(f"Error during audio processing: {e}")


elif interaction_mode == "File Upload":
    st.write("### Upload an audio file for transcription")
    uploaded_file = st.file_uploader("Upload an audio file", type=["wav", "mp3"])
    if uploaded_file is not None:
        recognizer = sr.Recognizer()
        try:
            with sr.AudioFile(uploaded_file) as source:
                audio_data = recognizer.record(source)
                transcribed_text = recognizer.recognize_google(audio_data)
                st.write(f"Transcribed Text: {transcribed_text}")

                # Add user message to chat history
                st.session_state.messages.append({"role": "user", "content": transcribed_text})

                # Generate system message based on the selected sample
                system_message = sample_to_message[selected_sample]

                # Get bot response
                response = client_chat.predict(
                    message=transcribed_text,
                    system_message=system_message,
                    max_tokens=param_4,
                    temperature=0.7,
                    top_p=0.95,
                    api_name="/chat"
                )
                # Add bot response to chat history
                st.session_state.messages.append({"role": "bot", "content": response})

                # Convert response to speech
                text_to_speech(response, selected_sample)
        except sr.UnknownValueError:
            st.error("Google Speech Recognition could not understand the audio.")
        except sr.RequestError as e:
            st.error(f"Error with Google Speech Recognition service: {e}")
