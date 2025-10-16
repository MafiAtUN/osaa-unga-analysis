"""
Analysis Module
Handles speech analysis, processing, and AI interactions
"""

import streamlit as st
import logging
from datetime import datetime
from typing import Optional, Dict, Any, Tuple
from llm import run_analysis, get_available_models, OpenAIError
from prompts import build_user_prompt, get_question_set
from data_ingestion import data_ingestion_manager

logger = logging.getLogger(__name__)


def process_analysis_with_text(extracted_text: str, country: str, speech_date, classification: str, model: str = "model-router-osaa-2") -> Optional[Dict[str, Any]]:
    """Process analysis with extracted text."""
    try:
        # Validate text length
        if len(extracted_text.strip()) < 100:
            st.error("❌ Text is too short for meaningful analysis. Please provide a longer speech.")
            return None
        
        # Get question set based on classification
        question_set = get_question_set(classification)
        
        # Build the prompt
        user_prompt = build_user_prompt(extracted_text, classification, country)
        
        # Run the analysis
        with st.spinner("🧠 AI is analyzing the speech..."):
            analysis_result = run_analysis(
                user_prompt=user_prompt,
                model=model,
                max_retries=3
            )
        
        if analysis_result:
            # Calculate word count
            word_count = len(extracted_text.split())
            
            # Create analysis data
            analysis_data = {
                'country': country,
                'date': speech_date,
                'classification': classification,
                'text': extracted_text,
                'word_count': word_count,
                'output_markdown': analysis_result,
                'model_used': model,
                'timestamp': datetime.now().isoformat()
            }
            
            # Save to database
            try:
                from simple_vector_storage import simple_vector_storage as db_manager
                analysis_id = db_manager.save_analysis(
                    country=country,
                    speech_date=speech_date,
                    classification=classification,
                    speech_text=extracted_text,
                    analysis_result=analysis_result,
                    word_count=word_count
                )
                analysis_data['analysis_id'] = analysis_id
                logger.info(f"Analysis saved with ID: {analysis_id}")
            except Exception as e:
                logger.error(f"Failed to save analysis to database: {e}")
            
            return analysis_data
        else:
            st.error("❌ Analysis failed. Please try again.")
            return None
            
    except OpenAIError as e:
        st.error(f"❌ AI service error: {e}")
        return None
    except Exception as e:
        logger.error(f"Analysis processing failed: {e}")
        st.error(f"❌ Analysis failed: {e}")
        return None


def process_analysis(uploaded_file, pasted_text: str, country: str, speech_date, classification: str, model: str = "model-router-osaa-2") -> Optional[Dict[str, Any]]:
    """Process analysis from uploaded file or pasted text."""
    try:
        extracted_text = ""
        
        if uploaded_file:
            # Process uploaded file
            if uploaded_file.name.lower().endswith('.txt'):
                # Handle text files with language detection
                st.info("📄 **Text File Detected** - Detecting language and translating if needed...")
                
                with st.spinner("🌍 Detecting language and translating if needed..."):
                    result = data_ingestion_manager.process_uploaded_file(
                        uploaded_file.getvalue(),
                        uploaded_file.name
                    )
                    
                    if result['success']:
                        extracted_text = result['translated_text']
                        
                        # Show language detection results
                        if result['translation_applied']:
                            st.success(f"🌍 **Language Detected:** {result['detected_language']} → **Translated to English**")
                            st.info(f"📊 Original: {result['text_length']} chars | Translated: {result['translated_length']} chars")
                        else:
                            st.success(f"🌍 **Language Detected:** {result['detected_language']} (No translation needed)")
                    else:
                        st.error(f"❌ Processing failed: {result['error']}")
                        return None
                        
            elif uploaded_file.name.lower().endswith('.mp3'):
                # Handle audio files
                st.info("🎵 **Audio File Detected** - Transcribing to text...")
                
                # Create progress bar
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    # Update progress
                    progress_bar.progress(20)
                    status_text.text("🎵 Starting audio transcription...")
                    
                    # Get Whisper client
                    from utils import get_whisper_client
                    whisper_client = get_whisper_client()
                    
                    if whisper_client:
                        # Transcribe audio
                        progress_bar.progress(50)
                        status_text.text("🎵 Transcribing audio...")
                        
                        # Use the existing transcription logic
                        from ingest import extract_text_from_file
                        extracted_text = extract_text_from_file(
                            uploaded_file.getvalue(), 
                            uploaded_file.name, 
                            whisper_client
                        )
                        
                        if extracted_text:
                            progress_bar.progress(80)
                            status_text.text("🌍 Detecting language and translating if needed...")
                            
                            # Process with language detection
                            result = data_ingestion_manager.process_uploaded_file(
                                extracted_text.encode('utf-8'),
                                uploaded_file.name.replace('.mp3', '.txt')
                            )
                            
                            if result['success']:
                                extracted_text = result['translated_text']
                                
                                if result['translation_applied']:
                                    st.success(f"🌍 **Language Detected:** {result['detected_language']} → **Translated to English**")
                                else:
                                    st.success(f"🌍 **Language Detected:** {result['detected_language']} (No translation needed)")
                            
                            # Complete the progress
                            progress_bar.progress(100)
                            status_text.text("✅ Audio transcription completed!")
                        else:
                            st.error("❌ Audio transcription failed.")
                            return None
                    else:
                        st.error("❌ Audio transcription service not available.")
                        return None
                        
                except Exception as e:
                    st.error(f"❌ Audio processing failed: {e}")
                    return None
                    
            else:
                # Handle PDF and Word documents
                file_type = "PDF" if uploaded_file.name.lower().endswith('.pdf') else "Word Document"
                st.info(f"📄 **{file_type} Detected** - Extracting text and detecting language...")
                
                with st.spinner(f"📖 Reading {file_type.lower()} content and detecting language... (This may take a few seconds)"):
                    result = data_ingestion_manager.process_uploaded_file(
                        uploaded_file.getvalue(),
                        uploaded_file.name
                    )
                    
                    if result['success']:
                        extracted_text = result['translated_text']
                        
                        if result['translation_applied']:
                            st.success(f"🌍 **Language Detected:** {result['detected_language']} → **Translated to English**")
                            st.info(f"📊 Original: {result['text_length']} chars | Translated: {result['translated_length']} chars")
                        else:
                            st.success(f"🌍 **Language Detected:** {result['detected_language']} (No translation needed)")
                    else:
                        st.error(f"❌ Processing failed: {result['error']}")
                        return None
        
        elif pasted_text:
            # Process pasted text
            extracted_text = pasted_text.strip()
            
            # Process with language detection
            st.info("🌍 **Detecting language and translating if needed...**")
            with st.spinner("🌍 Processing text..."):
                result = data_ingestion_manager.process_uploaded_file(
                    extracted_text.encode('utf-8'),
                    'pasted_text.txt'
                )
                
                if result['success']:
                    extracted_text = result['translated_text']
                    
                    if result['translation_applied']:
                        st.success(f"🌍 **Language Detected:** {result['detected_language']} → **Translated to English**")
                    else:
                        st.success(f"🌍 **Language Detected:** {result['detected_language']} (No translation needed)")
                else:
                    st.warning("⚠️ Language detection failed, proceeding with original text.")
        
        if not extracted_text:
            st.error("❌ No text extracted. Please check your file or try again.")
            return None
        
        # Store extracted text in session state
        st.session_state.extracted_text = extracted_text
        
        # Process the analysis
        return process_analysis_with_text(extracted_text, country, speech_date, classification, model)
        
    except Exception as e:
        logger.error(f"Analysis processing failed: {e}")
        st.error(f"❌ Analysis failed: {e}")
        return None


def process_chat_question(question: str, analysis_context: str, country: str, classification: str, model: str = "model-router-osaa-2") -> Tuple[Optional[str], Optional[str]]:
    """Process a chat question about the analysis."""
    try:
        # Validate inputs
        if not question.strip():
            return None, "Question cannot be empty"
        
        if not analysis_context.strip():
            return None, "No analysis context available"
        
        # Build chat prompt
        from prompts import build_chat_prompt
        chat_prompt = build_chat_prompt(question, analysis_context, country, classification)
        
        # Run the analysis
        response = run_analysis(
            user_prompt=chat_prompt,
            model=model,
            max_retries=2
        )
        
        if response:
            return response, None
        else:
            return None, "Failed to generate response"
            
    except Exception as e:
        logger.error(f"Chat question processing failed: {e}")
        return None, str(e)
