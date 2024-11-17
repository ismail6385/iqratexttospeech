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

# Page config and other imports remain same...

# Modified rate calculation
def calculate_rate(percentage):
    # Convert percentage to appropriate rate format
    # 100% = +0%, 200% = +100%, 50% = -50%
    adjusted_rate = percentage - 100
    return f"{adjusted_rate:+d}%"

async def generate_speech(text, voice, style, rate_percentage, volume):
    rate = calculate_rate(rate_percentage)
    communicate = edge_tts.Communicate(text, voice, rate=rate, volume=volume)
    audio_data = await communicate.get_audio()
    return audio_data

# Rest of your imports and initial setup remain the same...

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
        
        # Modified rate slider
        speaking_rate = st.slider(
            "Speaking Rate",
            min_value=50,
            max_value=200,
            value=100,
            step=10,
            help="100% is normal speed, 50% is slower, 200% is faster"
        )
        
        # Modified volume slider
        volume = st.slider(
            "Voice Volume",
            min_value=0,
            max_value=100,
            value=100,
            help="Adjust voice volume"
        )

        # Background music settings
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
                    # Generate speech with corrected rate format
                    audio_data = asyncio.run(generate_speech(
                        story_text,
                        VOICES[selected_voice],
                        voice_style,
                        speaking_rate,  # This will now be properly formatted
                        f"{volume}%"
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
                    st.error("Please try a different rate or voice setting")
        else:
            st.warning("Please enter some text to generate audio.")

# Update the batch processing section similarly
with tabs[1]:
    st.header("Batch Story Processing")
    
    uploaded_files = st.file_uploader(
        "Upload text files (.txt)",
        type=['txt'],
        accept_multiple_files=True
    )
    
    if uploaded_files:
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
            # Modified batch rate slider
            batch_rate = st.slider(
                "Speaking Rate for Batch Processing",
                min_value=50,
                max_value=200,
                value=100,
                step=10,
                key="batch_rate"
            )
            
            # Modified batch volume slider
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
                        content = uploaded_file.read().decode()
                        
                        # Generate audio with corrected rate format
                        audio_data = asyncio.run(generate_speech(
                            content,
                            VOICES[batch_voice],
                            batch_style,
                            batch_rate,
                            f"{batch_volume}%"
                        ))
                        
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

# Footer remains the same...
