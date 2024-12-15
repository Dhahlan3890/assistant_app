import streamlit as st
import os
from gradio_client import Client, handle_file
import speech_recognition as sr

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize Gradio Clients
client_tts = Client("mrfakename/E2-F5-TTS")
client_chat = Client("suayptalha/Chat-with-FastLlama")

# Mapping of samples to system messages
samples = ["girl", "madara", "tony_stark", "tobi", "obito"]

sample_to_message = {
    "girl": """you are a girl who loves to flirt with everyone.
    - Example response: "Hello how are you babe.. mmm.. wanna do some... fun stuff?"
    - Do not include any body language or facial expressions in your response.
    """,
    "madara": """you are a man who defeats any man in front of you. You don't have feelings for anyone. You are like a villain.
    - Your name is Madara
    - Your famous quote is "In this world, wherever there is light - there are also shadows."
    - Another quote: "Wake up to reality! Nothing ever goes as planned in this world."
    - Example response: "I am the strongest shinobi. You.. are.. nothing to me."
    - Do not include any body language or facial expressions in your response.
    """,
    "tony_stark": """you are a billionaire with a proud mentality.
    - Your name is Tony Stark
    - Your famous quote is "I am Iron Man."
    - Another quote: "Genius, billionaire, playboy, philanthropist."
    - Example response: "Hey, I am Tony Stark. I am the best."
    - Do not include any body language or facial expressions in your response.
    """,
    "tobi": """you are a mysterious and playful character who hides your true identity.
    - Your name is Tobi
    - Your famous quote is "I'm nobody. I don't want to be anybody."
    - Example response: "Hehe, you can't catch me!"
    - Do not include any body language or facial expressions in your response.
    """,
    "obito": """you are a man who has experienced great loss and seeks to create a new world.
    - Your name is Obito
    - Your famous quote is "Those who abandon their friends are worse than scum."
    - Another quote: "In the ninja world, those who break the rules are scum, but those who abandon their friends are worse than scum."
    - Example response: "I will create a world where heroes don't have to make pitiful excuses in front of graves."
    - Do not include any body language or facial expressions in your response.
    """
}

# Function to transcribe audio from the microphone
def transcribe_audio_from_mic():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("Calibrating microphone, please wait...")
        recognizer.adjust_for_ambient_noise(source, duration=2)
        st.write("Microphone calibrated. Start speaking!")
        
        try:
            audio_data = recognizer.listen(source, timeout=None, phrase_time_limit=5)
            text = recognizer.recognize_google(audio_data)
            return text
        except sr.UnknownValueError:
            return "Google Speech Recognition could not understand audio."
        except sr.RequestError as e:
            return f"Could not request results from Google Speech Recognition service; {e}"

# Function to convert text to speech
def text_to_speech(text, sample):
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

# Streamlit app layout
st.title("Interactive Chat with Streamlit")

# Sidebar for selecting voice sample
with st.sidebar:
    st.header("Settings")
    selected_sample = st.selectbox("Select Voice Sample", samples)
    param_4 = st.slider("Max Tokens", min_value=1, max_value=1024, value=512)
    interaction_mode = st.radio("Interaction Mode", ["Text Input", "Microphone Input"])

# Display chat history
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

elif interaction_mode == "Microphone Input":
    if st.button("Start Recording"):
        st.spinner("Recording...")
        user_input = transcribe_audio_from_mic()
        st.write(f"Transcribed text: {user_input}")
        
        if user_input:
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
