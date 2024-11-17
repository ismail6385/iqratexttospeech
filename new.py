import streamlit as st
import os
import asyncio
import edge_tts
import io
import base64

# Page config
st.set_page_config(
    page_title="Text to Speech Generator",
    page_icon="🎙️",
    layout="wide"
)

# Title
st.title("🎙️ Professional Text-to-Speech Generator")
st.markdown("Create high-quality audio content for your YouTube channel")

# Available voices
VOICES = {
    "Female (US)": "en-US-JennyNeural",
    "Male (US)": "en-US-GuyNeural",
    "Female (UK)": "en-GB-SoniaNeural",
    "Male (UK)": "en-GB-RyanNeural",
}

# Voice styles
STYLES = ["normal", "cheerful", "excited", "friendly", "hopeful", "sad"]

async def generate_speech(text, voice, rate="+0%"):
    output = io.BytesIO()
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            output.write(chunk["data"])
    
    output.seek(0)
    return output.read()

def get_binary_file_downloader_html(bin_data, file_label='File', filename="audio.mp3"):
    bin_str = base64.b64encode(bin_data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{filename}">Download {file_label}</a>'
    return href

# Create tabs
tab1, tab2 = st.tabs(["Single Story", "Batch Processing"])

# Single Story Tab
with tab1:
    st.header("Single Story Generator")
    
    # Create two columns
    col1, col2 = st.columns([2, 1])
    
    # First column - Text input
    with col1:
        story_title = st.text_input("Story Title", "My Story")
        story_text = st.text_area(
            "Enter your story text",
            height=300,
            placeholder="Once upon a time..."
        )

    # Second column - Voice settings
    with col2:
        st.subheader("Voice Settings")
        selected_voice = st.selectbox("Select Voice", list(VOICES.keys()))
        voice_style = st.selectbox("Voice Style", STYLES)
        speaking_rate = st.slider(
            "Speaking Rate",
            min_value=-50,
            max_value=50,
            value=0,
            step=10,
            help="0 is normal speed"
        )

    # Generate button
    if st.button("Generate Audio", type="primary"):
        if story_text:
            with st.spinner("Generating audio..."):
                try:
                    rate_string = f"{speaking_rate:+d}%"
                    audio_data = asyncio.run(generate_speech(
                        story_text,
                        VOICES[selected_voice],
                        rate=rate_string
                    ))
                    
                    st.audio(audio_data, format='audio/mp3')
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

# Batch Processing Tab
with tab2:
    st.header("Batch Story Processing")
    
    uploaded_files = st.file_uploader(
        "Upload text files (.txt)",
        type=['txt'],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        batch_voice = st.selectbox(
            "Select Voice for Batch Processing",
            list(VOICES.keys()),
            key="batch_voice"
        )
        
        batch_rate = st.slider(
            "Speaking Rate for Batch Processing",
            min_value=-50,
            max_value=50,
            value=0,
            step=10,
            key="batch_rate"
        )

        if st.button("Process All Stories", type="primary"):
            with st.spinner("Processing stories..."):
                try:
                    for uploaded_file in uploaded_files:
                        content = uploaded_file.read().decode()
                        rate_string = f"{batch_rate:+d}%"
                        
                        audio_data = asyncio.run(generate_speech(
                            content,
                            VOICES[batch_voice],
                            rate=rate_string
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
