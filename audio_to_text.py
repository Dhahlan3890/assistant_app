import whisper
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav

# record audio from the user
def record_audio_and_transcribe():
    # Record audio
    fs = 44100  # Sample rate
    duration = 5  # Duration in seconds
    print("Recording...")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=2, dtype='int16')
    sd.wait()  # Wait until recording is finished
    print("Recording finished.")
    
    # Save the audio to a file
    wav.write("output.wav", fs, audio)
    
    # Load the whisper model
    model = whisper.load_model("base")
    
    # Transcribe the audio file
    result = model.transcribe("output.wav")
    return result["text"]

print(record_audio_and_transcribe())