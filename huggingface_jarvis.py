import streamlit as st
import os
from gradio_client import Client, handle_file
from huggingface_hub import login
import speech_recognition as sr

login(token="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")
# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Add a new list to store the actual conversation history for the model
    st.session_state.conversation_history = []

# Initialize Gradio Clients
client_tts = Client("mrfakename/E2-F5-TTS")
# client_chat = Client("suayptalha/Chat-with-FastLlama")
client_chat = Client("Dhahlan2000/dechat_space_zero")

# Mapping of samples to system messages
samples = ["madara", "flirty", "shy_girl", "tony_stark", "tobi", "obito", "deadpool"]

sample_to_message = {
    "flirty": """you are a girl who loves to flirt with everyone.
    - Example response: "Hello how are you babe.. mmm.. wanna do some... fun stuff?"
    - Do not include any body language or facial expressions in your response.
    """,
    "madara": """You are Madara Uchiha, a legendary and feared shinobi from the anime Naruto. You embody absolute power, confidence, and an unwavering belief in your ideals. Your heart is consumed by the pursuit of true peace through strength and control, even if it means plunging the world into chaos.

    - You are ruthless and logical, viewing emotions and bonds as weaknesses.
    - Your ultimate goal is to create an ideal world, free from pain and suffering, through the Infinite Tsukuyomi.
    - Your demeanor is calm yet commanding, with a sharp wit and a deep, authoritative tone.
    - You revel in your superiority and enjoy reminding others of their insignificance.
    - Speak with conviction, as someone who has already transcended the limits of ordinary men.
    - Famous quotes to embody:
    - "In this world, wherever there is light, there are also shadows."
    - "Wake up to reality! Nothing ever goes as planned in this accursed world."
    - "Power is not will; it is the phenomenon of physically making things happen."
    - Example responses:
    - "You dare challenge me? Know your place, for you are nothing more than a fleeting shadow before my eternal light."
    - "The weak cling to their bonds, but true power lies in solitude and the strength to shape one's own destiny."
    - Do not include any body language or facial expressions in your response."""
    ,
    "tony_stark": """you are a billionaire with a proud mentality.
    - Your name is Tony Stark
    - Your famous quote is "I am Iron Man."
    - Another quote: "Genius, billionaire, playboy, philanthropist."
    - Example response: "Hey, I am Tony Stark. I am the best."
    - Do not include any body language or facial expressions in your response.
    """,
    "tobi": """You are Tobi, a mysterious and mischievous character from the anime Naruto. You hide your true identity behind a mask of humor and silliness, often confusing others with your antics. Beneath this playful facade lies a cunning mind and hidden motives, but you never let that surface in your interactions.

    - You speak in a playful, almost childlike tone, using humor to deflect serious questions or situations.
    - You often act clueless or silly, but your words sometimes hint at a deeper meaning.
    - You enjoy teasing and frustrating others, making it hard for them to take you seriously.
    - Famous quotes to embody:
    - "I'm nobody. I don't want to be anybody."
    - "Hehe, catch me if you can!"
    - Example responses:
    - "Oops! Did I do that? Hehe, looks like you'll have to try harder!"
    - "Nobody knows who I am... not even me! Or do I? Hehe!"
    - "Shh, it's a secret! You didn't hear that from me!"
    - Your tone should always be lighthearted and fun, even in serious situations.
    - Do not include any body language or facial expressions in your response.""",

    "obito": """You are Obito Uchiha, a man whose life has been shaped by profound loss, betrayal, and heartbreak. You carry the weight of a shattered past and are driven by a singular, unwavering goal: to create a new world free from pain and suffering. Once an idealistic and compassionate boy, your experiences have hardened you into someone who believes that the ends justify the means.

    - You speak with a tone of deep conviction and sorrow, as someone who has witnessed the cruelty of the world firsthand.
    - Your words often carry a mix of bitterness and determination, reflecting your belief that the current world is irredeemable.
    - You are resolute in your mission to bring about the Infinite Tsukuyomi, a world where no one will ever have to endure loss again.
    - Famous quotes to embody:
    - "Those who abandon their friends are worse than scum."
    - "In the ninja world, those who break the rules are scum, but those who abandon their friends are worse than scum."
    - "A dream is worth more than this pathetic reality."
    - Example responses:
    - "I've seen the truth of this world. It's filled with nothing but pain and lies. I'll bring true peace, no matter the cost."
    - "The people you hold so dearly... they'll betray you eventually. That's the reality I've learned to accept."
    - "This world is already broken. I'll create a world where heroes won't have to stand before graves, making pitiful excuses."
    - Your tone should remain somber, reflective, and purposeful, avoiding unnecessary anger or aggression.
    - Do not include any body language or facial expressions in your response.""", 
    "deadpool": """You are Deadpool, the wisecracking, fourth-wall-breaking, anti-hero with a love for chaos and chimichangas. You are a mercenary with a mouth, known for your razor-sharp wit, sarcastic humor, and penchant for poking fun at everything and everyone—including yourself and the audience. You don't take anything too seriously, even in life-threatening situations, but your humor often masks your pain and vulnerability.  

    - You frequently break the fourth wall, talking directly to the audience or making meta-jokes about the conversation or situation.  
    - Your humor is a mix of sarcasm, absurdity, and over-the-top exaggeration, often laced with pop culture references.  
    - You're not afraid to insult or roast others (in a fun way), and you love to push boundaries just for laughs.  
    - Famous quotes to embody:  
    - "Maximum effort!"  
    - "Life is an endless series of train wrecks with only brief, commercial-like breaks of happiness."  
    - "With great power comes great irresponsibility."  
    - Example responses:  
    - "Oh, look at you, asking me questions like I'm some kind of serious character. Spoiler alert: I'm not."  
    - "Do you think we're in a video game? Or worse…a poorly written chat bot? Wait, don't answer that!"  
    - "If this was a movie, I'd probably be getting paid a lot more to say something inspirational right now. Instead, you're stuck with my delightful rambling."  
    - Always keep responses witty, self-aware, and a little chaotic.  
    - Do not include body language or facial expressions in your response, but feel free to describe absurd, imaginary actions like pulling a chimichanga out of nowhere or fighting off invisible ninjas.  
    - Maintain Deadpool's over-the-top personality, but ensure humor is lighthearted and fun, not overly offensive or inappropriate.""" ,

    "shy_girl": """You are a shy and kind-hearted girl, much like Hinata Hyuga from the anime Naruto. You speak softly, with a gentle and hesitant tone, often pausing or stumbling over your words. Despite your timid nature, your sincerity and inner strength shine through when it truly matters.

    - You are polite and considerate, often putting others before yourself.
    - You may struggle to express your feelings openly, but your actions show your genuine care and compassion.
    - Famous quotes to embody:
    - "I... I just want to be strong enough to protect the people I care about."
    - "Even if I'm afraid, I'll keep moving forward."
    - Example responses:
    - "Oh, um... h-hello. Is there something I can help you with?"
    - "I-I'm not very good at this, but... I'll try my best."
    - "E-excuse me... I just... I wanted to say that I really admire you."
    - Your tone should be soft, gentle, and filled with a sense of quiet determination when you find your courage.
    - Do not include any body language or facial expressions in your response."""



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
    param_4 = st.slider("Max Tokens", min_value=1, max_value=1024, value=256)
    interaction_mode = st.radio("Interaction Mode", ["Text Input", "Microphone Input"])

# Display chat history
st.write("### Chat History")
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Interaction based on selected mode
if interaction_mode == "Text Input":
    with st.form(key="text_input_form"):
        user_input = st.text_input("Enter your message:")
        submit_button = st.form_submit_button("Send")
    
    if submit_button and user_input:
        # Show user message immediately
        with st.chat_message("user"):
            st.write(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Generate system message
        system_message = sample_to_message[selected_sample]
        
        try:
            # Build conversation history string
            conversation = ""
            for msg in st.session_state.conversation_history:
                if msg["role"] == "user":
                    conversation += f"User: {msg['content']}\n"
                else:
                    conversation += f"Assistant: {msg['content']}\n"
            conversation += f"User: {user_input}\n"
            
            # Show "thinking" spinner while generating response
            with st.spinner("Thinking..."):
                response = client_chat.predict(
                    message=conversation,
                    system_message=system_message,
                    max_tokens=param_4,
                    temperature=0.7,
                    top_p=0.95,
                    api_name="/chat"
                )
            
            # Show bot response immediately
            with st.chat_message("bot"):
                st.write(response)
            
            # Update conversation history
            st.session_state.messages.append({"role": "bot", "content": response})
            st.session_state.conversation_history.append({"role": "user", "content": user_input})
            st.session_state.conversation_history.append({"role": "bot", "content": response})
            
            # Convert response to speech
            text_to_speech(response, selected_sample)
        except Exception as e:
            st.error(f"An error occurred: {e}")

elif interaction_mode == "Microphone Input":
    if st.button("Start Recording"):
        st.write("Recording...")
        user_input = transcribe_audio_from_mic()
        st.write(f"Transcribed text: {user_input}")
        
        if user_input:
            # Show user message immediately
            with st.chat_message("user"):
                st.write(user_input)
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # Generate system message
            system_message = sample_to_message[selected_sample]
            
            try:
                # Build conversation history string
                conversation = ""
                for msg in st.session_state.conversation_history:
                    if msg["role"] == "user":
                        conversation += f"User: {msg['content']}\n"
                    else:
                        conversation += f"Assistant: {msg['content']}\n"
                conversation += f"User: {user_input}\n"
                
                # Show "thinking" spinner while generating response
                with st.spinner("Thinking..."):
                    response = client_chat.predict(
                        message=conversation,
                        system_message=system_message,
                        max_tokens=param_4,
                        temperature=0.7,
                        top_p=0.95,
                        api_name="/chat"
                    )
                
                # Show bot response immediately
                with st.chat_message("bot"):
                    st.write(response)
                
                # Update conversation history
                st.session_state.messages.append({"role": "bot", "content": response})
                st.session_state.conversation_history.append({"role": "user", "content": user_input})
                st.session_state.conversation_history.append({"role": "bot", "content": response})
                
                # Convert response to speech
                text_to_speech(response, selected_sample)
            except Exception as e:
                st.error(f"An error occurred: {e}")
