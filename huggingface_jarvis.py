import streamlit as st
import pyttsx3
import os
import requests
from gradio_client import Client, handle_file
import subprocess

if os.name == 'posix':
    try:
        # Command to install espeak-ng
        command = ["sudo", "apt", "install", "-y", "espeak-ng"]
        
        # Execute the command
        subprocess.run(command, check=True)
        print("eSpeak-ng installed successfully!")
    except subprocess.CalledProcessError as e:
        print("Error occurred while installing eSpeak-ng:", e)


client_tts = Client("mrfakename/E2-F5-TTS")

samples = ["girl", "madara", "tony_stark"]

# Mapping of samples to system messages
sample_to_message = {
    "girl": "you are a girl who loves to flirt with everyone",
    "madara": "you are a warrior who motivates anyone",
    "tony_stark": "you are a billionaire with a proud mentality"
}

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
    

engine = pyttsx3.init()

def talk(text):
    """Convert text to speech."""
    engine.say(text)
    engine.runAndWait()

voices = engine.getProperty('voices')

engine.setProperty('voice', voices[1].id)

engine.setProperty('rate', 140)

# Initialize Gradio Client
client = Client("suayptalha/Chat-with-FastLlama")

# Streamlit app
st.title("Gradio Client with Streamlit")

# User input
message = st.text_input("Enter your message:", "Hello!!")

# Additional parameters
param_4 = st.number_input("Param 4 (Max Tokens):", min_value=1, max_value=1024, value=512)

# Dropdown to select voice sample
selected_sample = st.selectbox("Select voice sample:", samples)

# Button to submit the request
if st.button("Submit"):
    try:
        # Get the system message based on the selected sample
        system_message = sample_to_message[selected_sample]
        
        # Call the Gradio client
        result = client.predict(
                message=message,
                system_message=system_message,
                max_tokens=param_4,
                temperature=0.7,
                top_p=0.95,
                api_name="/chat"
        )
        # Display the result
        st.success("Response from the model:")
        st.write(result)
        # Convert text to speech
        text_to_speech(result, selected_sample)
    except Exception as e:
        # Handle errors
        st.error(f"An error occurred: {e}")
