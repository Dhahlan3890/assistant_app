import streamlit as st
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, WebRtcMode
from gradio_client import Client, handle_file

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

class AudioProcessor(AudioProcessorBase):
    """Custom audio processor to handle real-time audio."""
    def __init__(self):
        self.transcribed_text = None

    def recv(self, frame):
        # Handle real-time audio processing and transcription
        # Example: Use a speech-to-text model here
        self.transcribed_text = "Mock Transcription"  # Replace with actual transcription logic
        return frame

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
        st.session_state.messages.append({"role": "user", "content": user_input})
        system_message = sample_to_message[selected_sample]

        try:
            response = client_chat.predict(
                message=user_input,
                system_message=system_message,
                max_tokens=param_4,
                temperature=0.7,
                top_p=0.95,
                api_name="/chat"
            )
            st.session_state.messages.append({"role": "bot", "content": response})
        except Exception as e:
            st.error(f"An error occurred: {e}")

elif interaction_mode == "Microphone Input":
    st.write("Using microphone input...")
    webrtc_ctx = webrtc_streamer(
        key="speech",
        mode=WebRtcMode.SENDONLY,
        audio_processor_factory=AudioProcessor,
        media_stream_constraints={"audio": True, "video": False},
    )

    if webrtc_ctx.audio_processor:
        transcription = webrtc_ctx.audio_processor.transcribed_text
        if transcription:
            st.write(f"Transcribed text: {transcription}")
            st.session_state.messages.append({"role": "user", "content": transcription})

            system_message = sample_to_message[selected_sample]

            try:
                response = client_chat.predict(
                    message=transcription,
                    system_message=system_message,
                    max_tokens=param_4,
                    temperature=0.7,
                    top_p=0.95,
                    api_name="/chat"
                )
                st.session_state.messages.append({"role": "bot", "content": response})
            except Exception as e:
                st.error(f"An error occurred: {e}")
