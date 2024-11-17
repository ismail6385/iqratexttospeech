import streamlit as st
import os
from gtts import gTTS
import tempfile
import base64
from pathlib import Path
import asyncio
import edge_tts
from pydub import AudioSegment
import io

# Page config
st.set_page_config(
    page_title="Professional Text to Speech Generator",
    page_icon="🎙️",
    layout="wide"
)

# Title and description
st.title("🎙️ Professional Text-to-Speech Generator")
st.markdown("Create high-quality audio content for your YouTube channel")

# Available voices
VOICES = {
    "Female (US)": "en-US-JennyNeural",
    "Male (US)": "en-US-GuyNeural",
    "Female (UK)": "en-GB-SoniaNeural",
    "Male (UK)": "en-GB-RyanNeural",
    "Female (Australian)": "en-AU-NatashaNeural",
    "Male (Australian)": "en-AU-WilliamNeural",
    "Female (Indian)": "en-IN-NeerjaNeural",
    "Male (Indian)": "en-IN-PrabhatNeural"
}

# Voice styles
STYLES = [
    "normal",
    "cheerful",
    "excited",
    "friendly",
    "hopeful",
    "sad",
    "shouting",
    "terrified",
    "unfriendly",
    "whispering"
]

async def generate_speech(text, voice, style, rate, volume):
    communicate = edge_tts.Communicate(text, voice, rate=f"{rate}%", volume=volume)
    audio_data = await communicate.get_audio()
    return audio_data

def mix_background_music(voice_audio, bg_music, bg_volume=-20):
    try:
        # Convert voice audio bytes to AudioSegment
        voice_segment = AudioSegment.from_mp3(io.BytesIO(voice_audio))
        
        # Convert background music bytes to AudioSegment
        bg_segment = AudioSegment.from_mp3(io.BytesIO(bg_music.read()))
        
        # Adjust background music duration to match voice
        if len(bg_segment) < len(voice_segment):
            bg_segment = bg_segment * (len(voice_segment) // len(bg_segment) + 1)
        bg_segment = bg_segment[:len(voice_segment)]
        
        # Adjust volume and mix
        bg_segment = bg_segment + bg_volume
        final_audio = voice_segment.overlay(bg_segment)
        
        # Export to bytes
        buffer = io.BytesIO()
        final_audio.export(buffer, format="mp3")
        return buffer.getvalue()
    except Exception as e:
        st.error(f"Error mixing audio: {str(e)}")
        return voice_audio

def get_binary_file_downloader_html(bin_data, file_label='File', filename="audio.mp3"):
    bin_str = base64.b64encode(bin_data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{filename}">Download {file_label}</a>'
    return href

# Main content area
tabs = st.tabs(["Single Story", "Batch Processing"])

with tabs[0]:
    st.header("Single Story Generator")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        story_title = st.text_input("Story Title", "My Story")
        story_text = st.text_area(
            "Enter your story text",
            height=300,
            placeholder="Once upon a time..."
        )

    with col2:
        st.subheader("Voice Settings")
        
        selected_voice = st.selectbox(
            "Select Voice",
            list(VOICES.keys())
        )
        
        voice_style = st.selectbox(
            "Voice Style",
            STYLES
        )
        
        speaking_rate = st.slider(
            "Speaking Rate",
            min_value=50,
            max_value=200,
            value=100,
            help="100 is normal speed"
        )
        
        volume = st.slider(
            "Voice Volume",
            min_value=0,
            max_value=100,
            value=100,
            help="Adjust voice volume"
        )
        
        st.subheader("Background Music")
        bg_music_file = st.file_uploader(
            "Upload Background Music (optional)",
            type=['mp3']
        )
        
        if bg_music_file:
            bg_volume = st.slider(
                "Background Music Volume",
                min_value=-40,
                max_value=0,
                value=-20,
                help="Adjust background music volume (negative values make it quieter)"
            )

    if st.button("Generate Audio", type="primary"):
        if story_text:
            with st.spinner("Generating audio..."):
                try:
                    # Generate speech
                    audio_data = asyncio.run(generate_speech(
                        story_text,
                        VOICES[selected_voice],
                        voice_style,
                        speaking_rate,
                        volume
                    ))
                    
                    # Mix with background music if provided
                    if bg_music_file:
                        audio_data = mix_background_music(
                            audio_data,
                            bg_music_file,
                            bg_volume
                        )
                    
                    # Display audio player
                    st.audio(audio_data, format='audio/mp3')
                    
                    # Download button
                    st.markdown(
                        get_binary_file_downloader_html(
                            audio_data,
                            'Download Audio',
                            f"{story_title}.mp3"
                        ),
                        unsafe_allow_html=True
                    )
                    
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
        else:
            st.warning("Please enter some text to generate audio.")

with tabs[1]:
    st.header("Batch Story Processing")
    
    uploaded_files = st.file_uploader(
        "Upload text files (.txt)",
        type=['txt'],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        # Use the same voice settings for batch processing
        col1, col2 = st.columns(2)
        
        with col1:
            batch_voice = st.selectbox(
                "Select Voice for Batch Processing",
                list(VOICES.keys()),
                key="batch_voice"
            )
            
            batch_style = st.selectbox(
                "Voice Style for Batch Processing",
                STYLES,
                key="batch_style"
            )
        
        with col2:
            batch_rate = st.slider(
                "Speaking Rate for Batch Processing",
                min_value=50,
                max_value=200,
                value=100,
                key="batch_rate"
            )
            
            batch_volume = st.slider(
                "Voice Volume for Batch Processing",
                min_value=0,
                max_value=100,
                value=100,
                key="batch_volume"
            )

        if st.button("Process All Stories", type="primary"):
            with st.spinner("Processing stories..."):
                try:
                    for uploaded_file in uploaded_files:
                        # Read content
                        content = uploaded_file.read().decode()
                        
                        # Generate audio
                        audio_data = asyncio.run(generate_speech(
                            content,
                            VOICES[batch_voice],
                            batch_style,
                            batch_rate,
                            batch_volume
                        ))
                        
                        # Display results
                        st.subheader(uploaded_file.name)
                        st.audio(audio_data, format='audio/mp3')
                        st.markdown(
                            get_binary_file_downloader_html(
                                audio_data,
                                f'Download {uploaded_file.name}',
                                f"{os.path.splitext(uploaded_file.name)[0]}.mp3"
                            ),
                            unsafe_allow_html=True
                        )
                            
                except Exception as e:
                    st.error(f"An error occurred during batch processing: {str(e)}")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center'>
    <p>Created for professional YouTube content creation</p>
    </div>
    """,
    unsafe_allow_html=True
)
