import speech_recognition as sr

# transcribe audio from microphone
def transcribe_audio_from_mic():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Please wait. Calibrating microphone...")
        recognizer.adjust_for_ambient_noise(source, duration=5)
        print("Microphone calibrated. Start speaking.")
        
        audio_data = recognizer.listen(source, timeout=None, phrase_time_limit=3)
        
        try:
            text = recognizer.recognize_google(audio_data)
            return text
        except sr.UnknownValueError:
            return "Google Speech Recognition could not understand audio"
        except sr.RequestError as e:
            return f"Could not request results from Google Speech Recognition service; {e}"

print(transcribe_audio_from_mic())