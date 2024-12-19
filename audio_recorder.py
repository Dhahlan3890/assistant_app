import streamlit as st
from st_audiorec import st_audiorec
from gradio_client import Client
import io

# Constants
WHISPER_API_URL = "mrfakename/fast-whisper-turbo"

def transcribe_audio(client: Client, audio_data: bytes) -> str:
    """Transcribe audio data directly using the Whisper API."""
    try:
        # Create a file-like object from bytes
        audio_file = io.BytesIO(audio_data)
        audio_file.name = "audio.wav"  # Some APIs need a filename
        
        result = client.predict(
            audio=audio_file,
            task="transcribe",
            api_name="/transcribe"
        )
        return result
    except Exception as e:
        st.error(f"Transcription error: {str(e)}")
        return None

def main():
    st.title("Audio Recorder and Transcriber")
    
    # Initialize Whisper client
    client = Client(WHISPER_API_URL)
    
    # Record audio
    wav_audio_data = st_audiorec()
    
    if wav_audio_data is not None:
        # Display audio player
        st.audio(wav_audio_data, format='audio/wav')
        
        # Transcribe audio directly from memory
        transcription = transcribe_audio(client, wav_audio_data)
        
        if transcription:
            st.write("Transcription:", transcription)

if __name__ == "__main__":
    main()
