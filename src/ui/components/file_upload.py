"""
File upload component for handling document and audio uploads
"""

import streamlit as st
from typing import Tuple, Optional
from ...core.security.input_validation import validate_file_upload
from ...config.settings import settings

class FileUploadComponent:
    """Component for handling file uploads with security validation."""
    
    def __init__(self):
        self.max_file_size = settings.MAX_FILE_SIZE
        self.allowed_types = settings.ALLOWED_FILE_TYPES
    
    def render_upload_section(self) -> Tuple[Optional[st.runtime.uploaded_file_manager.UploadedFile], Optional[str]]:
        """
        Render the file upload section.
        
        Returns:
            Tuple of (uploaded_file, pasted_text)
        """
        st.markdown("### 📝 Text Input or File Upload")
        
        # Text input first
        st.markdown("#### ✍️ Paste Text (Recommended)")
        pasted_text = st.text_area(
            "Paste your speech text here:",
            height=150,
            placeholder="Paste the speech text directly here...",
            help="This is the fastest and most reliable method"
        )
        
        # File uploader (second option)
        st.markdown("#### 📁 Or Upload File")
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=['pdf', 'docx', 'mp3'],
            help=f"Upload a PDF, Word document, or MP3 audio file (max {self.max_file_size // (1024*1024)}MB)"
        )
        
        return uploaded_file, pasted_text
    
    def validate_upload(self, uploaded_file, pasted_text) -> Tuple[bool, str]:
        """
        Validate upload inputs.
        
        Args:
            uploaded_file: Uploaded file object
            pasted_text: Pasted text string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not uploaded_file and not pasted_text:
            return False, "Please upload a file or paste text to analyze."
        
        if uploaded_file:
            # Validate file
            if not validate_file_upload(uploaded_file.getvalue(), uploaded_file.name):
                return False, f"❌ Invalid file. Please upload a valid PDF, DOCX, or MP3 file (max {self.max_file_size // (1024*1024)}MB)."
        
        return True, ""
    
    def get_file_info(self, uploaded_file) -> dict:
        """
        Get file information for display.
        
        Args:
            uploaded_file: Uploaded file object
            
        Returns:
            Dictionary with file information
        """
        if not uploaded_file:
            return {}
        
        return {
            'name': uploaded_file.name,
            'size': uploaded_file.size,
            'type': uploaded_file.name.split('.')[-1].lower()
        }
    
    def display_file_info(self, uploaded_file) -> None:
        """Display file information."""
        if uploaded_file:
            file_info = self.get_file_info(uploaded_file)
            st.info(f"📄 **File**: {file_info['name']} ({file_info['size']:,} bytes)")
    
    def get_file_content(self, uploaded_file) -> bytes:
        """Get file content as bytes."""
        if uploaded_file:
            return uploaded_file.getvalue()
        return b""
