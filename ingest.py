"""
Text extraction utilities for PDF, DOCX, and MP3 files.
"""

import io
import logging
from typing import Optional, Union
from openai import AzureOpenAI
from pypdf import PdfReader
import pdfminer.high_level
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
import docx
try:
    import pydub
    from pydub import AudioSegment
except ImportError:
    # pydub requires additional system dependencies for audio processing
    # For now, we'll handle this gracefully
    pydub = None
    AudioSegment = None

logger = logging.getLogger(__name__)

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extract text from PDF file bytes.
    First tries pypdf, falls back to pdfminer.six if pages return empty.
    
    Args:
        file_bytes: PDF file as bytes
        
    Returns:
        Extracted text as string
    """
    try:
        # Try pypdf first
        pdf_file = io.BytesIO(file_bytes)
        reader = PdfReader(pdf_file)
        
        text_parts = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text.strip():  # Only add non-empty pages
                text_parts.append(page_text)
        
        if text_parts:
            return "\n\n".join(text_parts)
        
        # If pypdf didn't extract anything, try pdfminer.six
        logger.warning("pypdf extracted no text, trying pdfminer.six")
        
    except Exception as e:
        logger.warning(f"pypdf failed: {e}, trying pdfminer.six")
    
    try:
        # Fallback to pdfminer.six
        pdf_file = io.BytesIO(file_bytes)
        text = pdfminer.high_level.extract_text(pdf_file)
        return text
        
    except Exception as e:
        logger.error(f"Both PDF extraction methods failed: {e}")
        raise Exception(f"Failed to extract text from PDF: {e}")

def extract_text_from_docx(file_bytes: bytes) -> str:
    """
    Extract text from DOCX file bytes.
    
    Args:
        file_bytes: DOCX file as bytes
        
    Returns:
        Extracted text as string
    """
    try:
        doc_file = io.BytesIO(file_bytes)
        doc = docx.Document(doc_file)
        
        text_parts = []
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text_parts.append(paragraph.text)
        
        return "\n\n".join(text_parts)
        
    except Exception as e:
        logger.error(f"Failed to extract text from DOCX: {e}")
        raise Exception(f"Failed to extract text from DOCX: {e}")

def transcribe_mp3_with_openai(file_bytes: bytes, client: AzureOpenAI) -> str:
    """
    Transcribe MP3 file using Azure OpenAI Whisper API.
    
    Args:
        file_bytes: MP3 file as bytes
        client: Azure OpenAI client instance
        
    Returns:
        Transcribed text as string
    """
    try:
        # Create a file-like object from bytes
        audio_file = io.BytesIO(file_bytes)
        audio_file.name = "audio.mp3"
        
        # Use Azure OpenAI Whisper API
        transcript = client.audio.transcriptions.create(
            model="whisper-001",  # Use the correct model name for this endpoint
            file=audio_file,
            response_format="text"
        )
        
        return transcript
        
    except Exception as e:
        logger.error(f"Failed to transcribe MP3 with Azure OpenAI: {e}")
        raise Exception(f"Failed to transcribe MP3: {e}")

def extract_text_from_mp3_local(file_bytes: bytes) -> str:
    """
    Local MP3 processing (fallback if OpenAI API is not available).
    This requires ffmpeg to be installed.
    
    Args:
        file_bytes: MP3 file as bytes
        
    Returns:
        Extracted text as string (placeholder - would need speech recognition)
    """
    if AudioSegment is None:
        logger.warning("pydub not available - using placeholder")
        return "[Audio file detected. Use OpenAI Whisper API for transcription.]"
    
    try:
        # Load audio file
        audio_file = io.BytesIO(file_bytes)
        audio = AudioSegment.from_file(audio_file, format="mp3")
        
        # For now, just return a placeholder
        # In a full implementation, you'd use speech recognition here
        logger.warning("Local MP3 transcription not implemented - using placeholder")
        return f"[Audio file detected, duration: {len(audio)}ms. Use OpenAI Whisper API for transcription.]"
        
    except Exception as e:
        logger.error(f"Failed to process MP3 locally: {e}")
        raise Exception(f"Failed to process MP3 locally: {e}")

def extract_text_from_file(file_bytes: bytes, filename: str, 
                          client: Optional[AzureOpenAI] = None) -> str:
    """
    Extract text from file based on file extension.
    
    Args:
        file_bytes: File as bytes
        filename: Original filename
        client: OpenAI client for audio transcription
        
    Returns:
        Extracted text as string
    """
    filename_lower = filename.lower()
    
    if filename_lower.endswith('.pdf'):
        return extract_text_from_pdf(file_bytes)
    elif filename_lower.endswith('.docx'):
        return extract_text_from_docx(file_bytes)
    elif filename_lower.endswith('.mp3'):
        if client:
            return transcribe_mp3_with_openai(file_bytes, client)
        else:
            return extract_text_from_mp3_local(file_bytes)
    else:
        raise ValueError(f"Unsupported file type: {filename}")

def validate_text_length(text: str, max_tokens: int = 25000) -> bool:
    """
    Validate if text length is within token limits.
    
    Args:
        text: Text to validate
        max_tokens: Maximum number of tokens allowed
        
    Returns:
        True if within limits, False otherwise
    """
    # Rough estimation: 1 token ≈ 4 characters
    estimated_tokens = len(text) // 4
    return estimated_tokens <= max_tokens

def chunk_text_if_needed(text: str, max_chunk_size: int = 20000) -> list[str]:
    """
    Split text into chunks if it's too long.
    
    Args:
        text: Text to chunk
        max_chunk_size: Maximum size of each chunk (in characters)
        
    Returns:
        List of text chunks
    """
    if len(text) <= max_chunk_size:
        return [text]
    
    chunks = []
    current_chunk = ""
    
    # Split by paragraphs first
    paragraphs = text.split('\n\n')
    
    for paragraph in paragraphs:
        if len(current_chunk) + len(paragraph) <= max_chunk_size:
            current_chunk += paragraph + '\n\n'
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = paragraph + '\n\n'
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks
