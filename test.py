import streamlit as st
import speech_recognition as sr

def transcribe_from_mic():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    st.write("Adjusting for ambient noise, please wait...")
    with mic as source:
        recognizer.adjust_for_ambient_noise(source, duration=3)
        st.write("Listening now! Speak clearly into the microphone.")
        audio = recognizer.listen(source)

    st.write("Processing your input...")
    try:
        transcription = recognizer.recognize_google(audio)
        return transcription
    except sr.UnknownValueError:
        return "Sorry, I could not understand the audio."
    except sr.RequestError as e:
        return f"Could not request results from Google Speech Recognition service; {e}"

# Streamlit UI
st.title("Real-Time Microphone Transcription")
st.write("Press the button below to start transcribing your speech.")

if st.button("Start Listening"):
    st.write("Recording...")
    transcription = transcribe_from_mic()
    st.write("Transcription:")
    st.success(transcription)
