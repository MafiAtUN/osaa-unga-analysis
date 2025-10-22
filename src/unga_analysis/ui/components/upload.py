"""
Upload components for file and text input
"""

import streamlit as st
from typing import Tuple, Optional


def upload_section() -> Tuple[Optional[object], Optional[str]]:
    """Render the upload section."""
    # Text input first
    st.markdown("#### 📝 Paste Text")
    pasted_text = st.text_area(
        "Paste transcript here",
        height=100,
        help="Paste the speech text directly (will be automatically translated to English if needed)"
    )
    
    # File uploader (second option)
    st.markdown("#### 📁 Or Upload File")
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['pdf', 'docx', 'mp3'],
        help="Upload a PDF, Word document, or MP3 audio file"
    )
    
    return uploaded_file, pasted_text


