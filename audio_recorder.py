import streamlit as st
from st_audiorec import st_audiorec
from gradio_client import Client, handle_file
from pathlib import Path

# Constants
AUDIO_FILENAME = "audio_sample.wav"
WHISPER_API_URL = "mrfakename/fast-whisper-turbo"

def save_audio(audio_data: bytes, filename: str) -> Path:
    """Save audio data to a file and return the file path."""
    file_path = Path(filename)
    with open(file_path, "wb") as f:
        f.write(audio_data)
    return file_path

def transcribe_audio(client: Client, audio_path: Path) -> str:
    """Transcribe audio using the Whisper API."""
    try:
        result = client.predict(
            audio=handle_file(str(audio_path)),
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
        
        # Save and transcribe audio
        audio_path = save_audio(wav_audio_data, AUDIO_FILENAME)
        transcription = transcribe_audio(client, audio_path)
        
        if transcription:
            st.write("Transcription:", transcription)

if __name__ == "__main__":
    main()