"""
Document Context Analysis Tab Module
Handles document-based analysis that combines uploaded documents with UNGA corpus
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Any
import os
import tempfile
from pathlib import Path

# Import existing modules
from src.unga_analysis.data.ingest import extract_text_from_file, validate_text_length
from src.unga_analysis.core.llm import run_analysis, get_available_models
from src.unga_analysis.data.simple_vector_storage import simple_vector_storage as db_manager
from src.unga_analysis.utils.export_utils import create_export_files
from src.unga_analysis.core.prompts import build_user_prompt

# Import OpenAI client creation
import openai
from dotenv import load_dotenv
load_dotenv()


def get_openai_client():
    """Get Azure OpenAI client."""
    api_key = os.getenv('AZURE_OPENAI_API_KEY')
    endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
    api_version = os.getenv('AZURE_OPENAI_API_VERSION', '2024-12-01-preview')
    
    if not api_key or not endpoint:
        raise ValueError("Azure OpenAI credentials not found in environment variables")
    
    return openai.AzureOpenAI(
        api_key=api_key,
        azure_endpoint=endpoint,
        api_version=api_version
    )


def render_document_context_analysis_tab():
    """Render the document context analysis tab."""
    st.header("📄 Document Context Analysis")
    st.markdown("**Upload documents, provide context, and get AI analysis with UNGA corpus (1946-2025)**")
    
    # Initialize session state
    if 'document_analysis_history' not in st.session_state:
        st.session_state.document_analysis_history = []
    
    # Step 1: Document Upload
    st.markdown("### 📁 Step 1: Upload Documents")
    
    uploaded_files = st.file_uploader(
        "Choose files to analyze",
        type=['pdf', 'docx', 'txt', 'mp3', 'wav'],
        accept_multiple_files=True,
        help="Upload PDF, DOCX, TXT, or audio files for analysis"
    )
    
    # Display uploaded files
    if uploaded_files:
        st.markdown("#### 📋 Uploaded Documents")
        for i, file in enumerate(uploaded_files):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"📄 {file.name} ({file.size:,} bytes)")
            with col2:
                if st.button("🗑️", key=f"remove_{i}", help="Remove file"):
                    uploaded_files.pop(i)
                    st.rerun()
            with col3:
                if st.button("👁️", key=f"preview_{i}", help="Preview content"):
                    preview_content(file)
    
    # Step 2: Context and Prompt (only show if files are uploaded)
    if uploaded_files:
        st.markdown("---")
        st.markdown("### 📝 Step 2: Provide Context and Instructions")
        
        # Context input
        st.markdown("**Additional Context (Optional):**")
        additional_context = st.text_area(
            "Provide any additional context or background information:",
            placeholder="e.g., These are daily consolidated speeches from African countries in 2024...",
            height=100,
            help="Any additional context that might help the analysis"
        )
        
        # Main prompt/instructions
        st.markdown("**Analysis Instructions:**")
        analysis_prompt = st.text_area(
            "What do you want the AI to do with these documents?",
            placeholder="e.g., Write a comprehensive paper analyzing the themes in these speeches for African countries in 2024. Focus on development priorities, climate change, and regional cooperation. Format as: Executive Summary, Key Themes, Country Analysis, Recommendations.",
            height=150,
            help="Describe exactly what analysis you want performed"
        )
        
        # Analysis options
        col1, col2 = st.columns(2)
        
        with col1:
            # Time range for historical context
            st.markdown("**Historical Context Range:**")
            year_range = st.slider(
                "Include UNGA speeches from:",
                min_value=1946,
                max_value=2024,
                value=(2000, 2024),
                help="Select the time range for historical context from UNGA corpus"
            )
            
            # Model selection
            available_models = get_available_models()
            if available_models:
                model = st.selectbox(
                    "AI Model:",
                    options=available_models,
                    key="document_context_model_select",
                    index=0,
                    help="Select the AI model for analysis"
                )
            else:
                model = "model-router-osaa-2"
                st.warning("⚠️ Using default model")
        
        with col2:
            # Analysis depth
            analysis_depth = st.selectbox(
                "Analysis Depth:",
                options=["Quick", "Standard", "Deep", "Comprehensive"],
                key="document_context_analysis_depth_select",
                index=2,
                help="Choose the depth of analysis"
            )
            
            # Max historical speeches
            max_context_speeches = st.number_input(
                "Max Historical Speeches:",
                min_value=5,
                max_value=50,
                value=20,
                help="Maximum number of historical speeches to include for context"
            )
        
        # Step 3: Analysis Button
        st.markdown("---")
        
        if st.button("🚀 Start Analysis", type="primary", use_container_width=True):
            if not analysis_prompt.strip():
                st.error("❌ Please provide analysis instructions.")
                return
            
            # Process the analysis
            with st.spinner("🔍 Analyzing documents and gathering historical context..."):
                analysis_result = process_document_analysis_simple(
                    uploaded_files=uploaded_files,
                    analysis_prompt=analysis_prompt,
                    additional_context=additional_context,
                    year_range=year_range,
                    max_context_speeches=max_context_speeches,
                    model=model,
                    analysis_depth=analysis_depth
                )
            
            if analysis_result:
                # Add to analysis history
                st.session_state.document_analysis_history.append(analysis_result)
                
                # Display results
                render_document_analysis_results(analysis_result)
            else:
                st.error("❌ Analysis failed. Please try again.")
    
    else:
        st.info("👆 Please upload documents to begin analysis.")


def preview_content(file):
    """Preview the content of an uploaded file."""
    try:
        # Extract text from file
        text = extract_text_from_file(file.getvalue(), file.name)
        
        # Show preview
        st.markdown("#### 📄 Content Preview")
        preview_text = text[:1000] + "..." if len(text) > 1000 else text
        st.text_area("Content:", preview_text, height=200, disabled=True)
        
        # Show metadata
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("File Size", f"{file.size:,} bytes")
        with col2:
            st.metric("Text Length", f"{len(text):,} characters")
        with col3:
            st.metric("Word Count", f"{len(text.split()):,} words")
            
    except Exception as e:
        st.error(f"❌ Error previewing file: {str(e)}")


def process_document_analysis_simple(
    uploaded_files: List,
    analysis_prompt: str,
    additional_context: str = "",
    year_range: tuple = (2000, 2024),
    max_context_speeches: int = 20,
    model: str = "model-router-osaa-2",
    analysis_depth: str = "Deep"
) -> Optional[Dict[str, Any]]:
    """Process document analysis with UNGA corpus context using custom prompt."""
    
    try:
        # Extract text from all uploaded files
        combined_text = ""
        file_metadata = []
        
        for file in uploaded_files:
            try:
                text = extract_text_from_file(file.getvalue(), file.name)
                if text:
                    combined_text += f"\n\n--- {file.name} ---\n\n{text}"
                    file_metadata.append({
                        'name': file.name,
                        'size': file.size,
                        'text_length': len(text),
                        'word_count': len(text.split())
                    })
            except Exception as e:
                st.warning(f"⚠️ Could not process {file.name}: {str(e)}")
                continue
        
        if not combined_text.strip():
            st.error("❌ No text could be extracted from uploaded files.")
            return None
        
        # Get historical context from UNGA corpus
        historical_context = ""
        similar_speeches = []
        
        # Search for similar content in the corpus
        search_results = db_manager.semantic_search(
            combined_text,
            limit=max_context_speeches
        )
        
        if search_results:
            similar_speeches = search_results
            
            # Filter by year range
            similar_speeches = [
                speech for speech in similar_speeches
                if year_range[0] <= speech.get('year', 0) <= year_range[1]
            ]
            
            # Build historical context
            historical_context = build_historical_context(similar_speeches)
        
        # Build the final analysis prompt
        final_prompt = f"""
        {analysis_prompt}
        
        **Uploaded Documents:**
        {combined_text[:3000]}...
        
        {f"**Additional Context:** {additional_context}" if additional_context else ""}
        
        {historical_context}
        
        **Instructions:**
        - Analyze the uploaded documents according to the user's specific instructions above
        - Use the historical context from UNGA speeches ({year_range[0]}-{year_range[1]}) to provide relevant background
        - Focus on the specific analysis requested by the user
        - Provide a comprehensive response that addresses the user's requirements
        - Format the response clearly and professionally
        """
        
        # Run AI analysis
        system_message = "You are an expert analyst specializing in UN General Assembly speeches and international relations. You have access to a comprehensive database of UNGA speeches from 1946-2025 and can provide detailed analysis combining current documents with historical context."
        
        analysis_result = run_analysis(
            system_msg=system_message,
            user_msg=final_prompt,
            model=model,
            client=get_openai_client()
        )
        
        if analysis_result:
            return {
                'timestamp': datetime.now().isoformat(),
                'analysis_prompt': analysis_prompt,
                'additional_context': additional_context,
                'file_metadata': file_metadata,
                'document_count': len(uploaded_files),
                'total_word_count': len(combined_text.split()),
                'similar_speeches_count': len(similar_speeches),
                'year_range': year_range,
                'analysis_result': {
                    'output_markdown': analysis_result,
                    'raw_output': analysis_result
                },
                'similar_speeches': similar_speeches[:10],  # Store top 10 for display
                'raw_text': combined_text[:5000]  # Store first 5000 chars for reference
            }
        
        return None
        
    except Exception as e:
        st.error(f"❌ Error processing analysis: {str(e)}")
        return None


def build_historical_context(similar_speeches: List[Dict]) -> str:
    """Build historical context from similar speeches."""
    if not similar_speeches:
        return ""
    
    context = "## Historical Context from UNGA Corpus\n\n"
    
    for i, speech in enumerate(similar_speeches[:10], 1):  # Limit to top 10
        context += f"### {i}. {speech.get('country', 'Unknown')} ({speech.get('year', 'Unknown')})\n"
        context += f"**Speaker:** {speech.get('speaker', 'Unknown')}\n"
        context += f"**Similarity Score:** {speech.get('similarity', 0):.3f}\n"
        context += f"**Content:** {speech.get('speech_text', '')[:500]}...\n\n"
    
    return context




def render_document_analysis_results(analysis_result: Dict[str, Any]):
    """Render the document analysis results."""
    st.markdown("---")
    st.markdown("## 📊 Document Analysis Results")
    
    # Display metadata
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📄 Documents", analysis_result['document_count'])
    with col2:
        st.metric("📝 Total Words", f"{analysis_result['total_word_count']:,}")
    with col3:
        st.metric("🔍 Historical Speeches", analysis_result['similar_speeches_count'])
    with col4:
        st.metric("📅 Year Range", f"{analysis_result['year_range'][0]}-{analysis_result['year_range'][1]}")
    
    # Display the user's prompt
    st.markdown("### 📝 Your Analysis Request")
    st.info(f"**Request:** {analysis_result['analysis_prompt']}")
    if analysis_result.get('additional_context'):
        st.info(f"**Additional Context:** {analysis_result['additional_context']}")
    
    # Display the analysis
    st.markdown("### 🤖 AI Analysis Results")
    st.markdown(analysis_result['analysis_result'].get('output_markdown', 'No analysis available'))
    
    # Display similar speeches if available
    if analysis_result['similar_speeches']:
        st.markdown("### 🔍 Historical Context Used")
        st.info(f"Analysis used {len(analysis_result['similar_speeches'])} historical UNGA speeches for context")
        
        with st.expander("View Historical Speeches Used"):
            for i, speech in enumerate(analysis_result['similar_speeches'], 1):
                st.write(f"**{i}. {speech.get('country', 'Unknown')} ({speech.get('year', 'Unknown')})**")
                st.write(f"*Speaker:* {speech.get('speaker', 'Unknown')}")
                st.write(f"*Content:* {speech.get('speech_text', '')[:300]}...")
                st.markdown("---")
    
    # Export options
    st.markdown("### 📥 Export Options")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 Export as DOCX", use_container_width=True):
            export_data = {
                'analysis': analysis_result['analysis_result'],
                'metadata': analysis_result,
                'type': 'document_analysis'
            }
            create_export_files(export_data, "document_analysis")
            st.success("✅ Export files created!")
    
    with col2:
        if st.button("📊 Export as Markdown", use_container_width=True):
            # Create markdown export
            markdown_content = f"# Document Analysis Report\n\n"
            markdown_content += f"**Analysis Request:** {analysis_result['analysis_prompt']}\n"
            if analysis_result.get('additional_context'):
                markdown_content += f"**Additional Context:** {analysis_result['additional_context']}\n"
            markdown_content += f"**Documents Analyzed:** {analysis_result['document_count']}\n"
            markdown_content += f"**Total Words:** {analysis_result['total_word_count']:,}\n"
            markdown_content += f"**Historical Context:** {analysis_result['year_range'][0]}-{analysis_result['year_range'][1]} ({analysis_result['similar_speeches_count']} speeches)\n\n"
            markdown_content += f"## Analysis Results\n\n{analysis_result['analysis_result'].get('output_markdown', '')}\n"
            
            st.download_button(
                label="Download Markdown",
                data=markdown_content,
                file_name=f"document_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown"
            )
    
    with col3:
        if st.button("📈 Export Historical Context", use_container_width=True):
            # Create CSV of similar speeches
            if analysis_result['similar_speeches']:
                df = pd.DataFrame(analysis_result['similar_speeches'])
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"historical_context_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
    
    # Store in session state for other tabs
    st.session_state.current_document_analysis = analysis_result
