"""
OpenAI Client Module
Handles Azure OpenAI client creation and configuration
"""

import os
import streamlit as st
from typing import Optional
from openai import AzureOpenAI


def get_openai_client() -> Optional[AzureOpenAI]:
    """Get Azure OpenAI client for Chat Completions API (Analysis)."""
    api_key = os.getenv('AZURE_OPENAI_API_KEY')
    azure_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
    api_version = os.getenv('AZURE_OPENAI_API_VERSION', '2024-08-01-preview')
    
    if not api_key or not azure_endpoint:
        st.error("Azure OpenAI credentials not configured")
        return None
    
    return AzureOpenAI(api_key=api_key, azure_endpoint=azure_endpoint, api_version=api_version)


def get_whisper_client() -> Optional[AzureOpenAI]:
    """Get Azure OpenAI client for Whisper API (Audio transcription)."""
    api_key = os.getenv('WHISPER_API_KEY')
    azure_endpoint = os.getenv('WHISPER_ENDPOINT')
    api_version = os.getenv('WHISPER_API_VERSION', '2024-08-01-preview')
    
    if not api_key or not azure_endpoint:
        st.error("Whisper API credentials not configured")
        return None
    
    return AzureOpenAI(api_key=api_key, azure_endpoint=azure_endpoint, api_version=api_version)
