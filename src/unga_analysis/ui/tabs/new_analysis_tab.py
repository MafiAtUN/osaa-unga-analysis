"""
New Analysis Tab Module
Handles the main analysis interface for new speech uploads
"""

import streamlit as st
from datetime import datetime
from typing import Optional, Dict, Any
from ..ui_components import (
    render_upload_section, 
    render_paste_section, 
    render_country_selection,
    render_speech_date_selection,
    render_classification_selection,
    render_sidebar_metadata_section,
    render_analysis_suggestions,
    render_chat_interface,
    render_export_section
)
from ..enhanced_ui_components import (
    render_info_card, render_success_card, render_warning_card, 
    render_error_card, render_step_guide, render_loading_spinner,
    render_tooltip_help, render_progress_bar
)
from ...core.auth import validate_file_upload, check_rate_limit
from ...data.simple_vector_storage import simple_vector_storage as db_manager


def check_existing_data(country: str, year: int) -> Optional[Dict[str, Any]]:
    """Check if data already exists for the given country and year."""
    try:
        # Query the database for existing speeches
        query = """
            SELECT id, country_name, year, speech_text, word_count, created_at
            FROM speeches 
            WHERE country_name = ? AND year = ?
            ORDER BY created_at DESC
            LIMIT 1
        """
        result = db_manager.conn.execute(query, [country, year]).fetchone()
        
        if result:
            return {
                'id': result[0],
                'country': result[1],
                'year': result[2],
                'text': result[3],
                'word_count': result[4],
                'created_at': result[5]
            }
        return None
    except Exception as e:
        st.error(f"Error checking existing data: {e}")
        return None


def process_analysis(uploaded_file, pasted_text, country, speech_date, classification, model):
    """
    Comprehensive analysis workflow:
    1. Check if speech exists in database
    2. If exists, load from database
    3. If not, extract text from file/paste
    4. Translate to English if needed
    5. Store in database
    6. Run analysis
    """
    from ...data.data_ingestion import data_ingestion_manager
    from ...core.llm import run_analysis
    
    try:
        year = speech_date.year
        
        # Step 1: Check if speech already exists in database
        with st.spinner("🔍 Checking if speech exists in database..."):
            existing_data = check_existing_data(country, year)
        
        if existing_data:
            st.success(f"✅ Speech found in database! Using existing data for {country} ({year})")
            speech_text = existing_data['text']
            word_count = existing_data['word_count']
        else:
            st.info("📝 Speech not found in database. Processing new speech...")
            
            # Step 2: Extract text from file or paste
            with st.spinner("📄 Extracting text from source..."):
                if uploaded_file:
                    file_name = uploaded_file.name
                    file_extension = file_name.split('.')[-1].lower()
                    
                    if file_extension in ['pdf']:
                        # Extract from PDF
                        from ...utils.file_processing import extract_text_from_pdf
                        speech_text = extract_text_from_pdf(uploaded_file.getvalue())
                    elif file_extension in ['docx', 'doc']:
                        # Extract from DOCX
                        from ...utils.file_processing import extract_text_from_docx
                        speech_text = extract_text_from_docx(uploaded_file.getvalue())
                    elif file_extension in ['mp3', 'wav', 'm4a']:
                        # Extract from audio
                        from ...utils.file_processing import extract_text_from_audio
                        speech_text = extract_text_from_audio(uploaded_file.getvalue(), file_extension)
                    elif file_extension in ['txt']:
                        # Plain text
                        speech_text = uploaded_file.getvalue().decode('utf-8')
                    else:
                        st.error(f"❌ Unsupported file type: {file_extension}")
                        return None
                else:
                    # Use pasted text
                    speech_text = pasted_text
            
            if not speech_text or len(speech_text.strip()) < 50:
                st.error("❌ Extracted text is too short or empty. Please check your input.")
                return None
            
            st.success(f"✅ Text extracted successfully ({len(speech_text)} characters)")
            
            # Step 3: Translate to English if needed
            with st.spinner("🌐 Checking language and translating if needed..."):
                try:
                    from langdetect import detect
                    detected_lang = detect(speech_text[:500])  # Check first 500 chars
                    
                    if detected_lang != 'en':
                        st.info(f"🌐 Detected language: {detected_lang}. Translating to English...")
                        from deep_translator import GoogleTranslator
                        
                        # Translate in chunks (Google Translator has limits)
                        max_chunk_size = 4000
                        translated_chunks = []
                        
                        for i in range(0, len(speech_text), max_chunk_size):
                            chunk = speech_text[i:i+max_chunk_size]
                            translated_chunk = GoogleTranslator(source=detected_lang, target='en').translate(chunk)
                            translated_chunks.append(translated_chunk)
                        
                        speech_text = ' '.join(translated_chunks)
                        st.success(f"✅ Text translated from {detected_lang} to English")
                    else:
                        st.success("✅ Text is already in English")
                except Exception as e:
                    st.warning(f"⚠️ Could not detect/translate language: {e}. Proceeding with original text.")
            
            # Calculate word count
            word_count = len(speech_text.split())
            
            # Step 4: Store in database
            with st.spinner("💾 Storing speech in database..."):
                try:
                    from ...data.data_ingestion import (
                        COUNTRY_CODE_MAPPING,
                        data_ingestion_manager,
                        get_additional_region_groupings_for_code,
                        get_regions_for_code,
                    )

                    country_code = None
                    for code, name in COUNTRY_CODE_MAPPING.items():
                        if name == country:
                            country_code = code
                            break

                    if not country_code:
                        st.warning(f"⚠️ Could not find country code for {country}. Using default.")
                        country_code = "UNK"

                    region_list = get_regions_for_code(country_code)
                    primary_region = region_list[0] if region_list else "Unknown"
                    additional_regions = get_additional_region_groupings_for_code(country_code)
                    is_african = data_ingestion_manager.is_african_member(country)

                    metadata = {
                        "country_code": country_code,
                        "regions": {
                            "primary": primary_region,
                            "additional": additional_regions,
                        },
                        "ingested_via": "new_analysis_tab",
                    }

                    db_manager.save_speech_data(
                        country_code=country_code,
                        country_name=country,
                        region=primary_region,
                        session=year - 1945,
                        year=year,
                        speech_text=speech_text,
                        source_filename=uploaded_file.name if uploaded_file else None,
                        is_african_member=is_african,
                        metadata=metadata,
                    )

                    st.success("✅ Speech stored in database for future use!")
                except Exception as e:
                    st.error(f"❌ Error storing in database: {e}")
                    # Continue with analysis even if storage fails
        
        # Step 5: Run AI analysis
        with st.spinner("🤖 Running AI analysis..."):
            # Create sophisticated system and user messages for rich analysis
            system_msg = """You are an expert analyst of UN General Assembly speeches with deep expertise in international relations, diplomacy, geopolitics, and policy analysis.

ANALYSIS FRAMEWORK:
You will analyze a single UNGA speech and provide a comprehensive, visually rich report that extracts maximum insight.

OUTPUT REQUIREMENTS:
1. **Structure your analysis** using clear markdown hierarchy (###, ####)
2. **Create visual artifacts** including:
   - Summary table of key themes with prominence ratings
   - Timeline of policy positions if multiple periods mentioned
   - Relationship mapping (who mentioned as partners/allies)
   - Priority ranking table
3. **Use rich formatting**:
   - **Bold** for key findings and country names
   - *Italics* for specific terms and concepts
   - > Blockquotes for powerful/notable direct quotes
   - Tables with | separators for structured data
   - Bullet points and numbered lists
   - Emojis strategically (📊 🌍 💡 🔍 ⚠️ ✅ 🎯)

REQUIRED OUTPUT SECTIONS:

### 🎯 Executive Summary
[3-4 sentences capturing the speech's core message and stance]

### 📊 Key Themes Analysis
| Theme | Prominence | Key Points | Evidence/Quote |
|-------|-----------|------------|----------------|
| Theme 1 | High/Med/Low | Summary | "Quote" (para X) |

### 🌍 International Relations & Partnerships
- **Allies/Partners mentioned:** [List with context]
- **Tensions/Concerns raised:** [List with specifics]
- **Multilateral commitments:** [List positions]

**Relationship Map:**
```
Strong Support: [Countries/Orgs]
Cooperation: [Countries/Orgs]  
Concerns: [Countries/Issues]
```

### 🏆 Policy Positions & Priorities
**Ranked by emphasis in speech:**

| Rank | Policy Area | Position Summary | Specific Commitments |
|------|-------------|------------------|---------------------|
| 1    | ...         | ...              | ...                 |

### 💬 Notable Quotes & Rhetoric
> "Most impactful quote 1"
> — Context and significance

> "Most impactful quote 2"  
> — Context and significance

### 🔍 Deeper Analysis
#### Tone & Diplomatic Style
[Assessment of rhetorical approach]

#### Historical Context
[References to past events, comparing to previous positions if relevant]

#### Regional/Global Positioning
[How this speech positions the country globally]

### 💡 Key Insights
1. **Primary insight:** [Explanation]
2. **Secondary insight:** [Explanation]
3. **Implications:** [Forward-looking analysis]

### ✅ Summary & Takeaways
[Concise synthesis of what matters most]

CRITICAL RULES:
- Quote directly from speech (use "..." and cite location)
- Create at least 2-3 tables
- Make every table information-dense
- Use emojis to improve scannability
- Provide page/paragraph references when quoting
- Bold all country names and organization names
- Show relationships and connections, not just lists"""
            
            user_msg = f"""**SPEECH TO ANALYZE**

**Country:** {country}
**Year:** {year}
**Word Count:** {word_count:,} words
**Classification:** {classification}

**Full Speech Text:**
{speech_text}

**Your Task:**
Provide a comprehensive, visually rich analysis following the exact structure and requirements specified in your instructions. Create tables, extract quotes, identify patterns, and deliver actionable insights.

**Begin your structured analysis now:**"""
            
            # Get Azure OpenAI client
            from ...core.openai_client import get_openai_client
            client = get_openai_client()
            
            if not client:
                st.error("❌ AI service is not available. Please check API configuration.")
                return None
            
            # Use the deployment name from environment or selected model
            import os
            deployment_name = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME', model)
            st.info(f"🤖 Using AI deployment: {deployment_name}")
            
            analysis_result = run_analysis(
                system_msg=system_msg,
                user_msg=user_msg,
                model=deployment_name,  # Use the actual deployment name
                client=client
            )
        
        if not analysis_result:
            st.error("❌ Analysis failed. Please try again.")
            return None
        
        # Prepare analysis data
        analysis_data = {
            'country': country,
            'date': speech_date.isoformat(),
            'year': year,
            'classification': classification,
            'word_count': word_count,
            'model': model,
            'output_markdown': analysis_result,
            'speech_text': speech_text[:1000] + "..." if len(speech_text) > 1000 else speech_text,  # Store excerpt
            'full_text': speech_text,
            'timestamp': datetime.now().isoformat()
        }
        
        # Step 6: Save analysis to database for "All Analyses" tab
        with st.spinner("💾 Saving analysis to database..."):
            try:
                analysis_id = db_manager.save_analysis(
                    country=country,
                    classification=classification,
                    raw_text=speech_text,
                    output_markdown=analysis_result,
                    prompt_used=f"Analysis of {country} ({year}) speech",
                    sdgs=None,  # Could be extracted from analysis if needed
                    africa_mentioned=None,  # Could be detected from analysis
                    speech_date=speech_date.isoformat(),
                    source_filename=uploaded_file.name if uploaded_file else "pasted_text",
                    metadata={
                        'model': model,
                        'word_count': word_count,
                        'year': year,
                        'analysis_type': 'single_speech'
                    }
                )
                
                analysis_data['analysis_id'] = analysis_id
                st.success(f"✅ Analysis saved to database (ID: {analysis_id}) and available in 'All Analyses' tab!")
                
            except Exception as e:
                st.warning(f"⚠️ Could not save to database: {e}. Analysis will still be shown.")
        
        st.success("✅ Analysis completed successfully!")
        return analysis_data
        
    except Exception as e:
        st.error(f"❌ Error during analysis: {e}")
        import traceback
        st.error(traceback.format_exc())
        return None


def render_new_analysis_tab():
    """Render the enhanced new analysis tab."""
    # Initialize session state
    if 'analysis_history' not in st.session_state:
        st.session_state.analysis_history = []
    
    # Add "Start New Analysis" button if there are existing results
    if 'current_analysis_data' in st.session_state and st.session_state.current_analysis_data:
        if st.button("➕ Start New Analysis", type="secondary", use_container_width=True, key="new_analysis_reset"):
            # Clear current analysis
            st.session_state.current_analysis_data = None
            st.session_state.selected_question = ""
            st.session_state.chat_input_value = ""
            st.rerun()
    
    # Create two columns for upload and paste
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📁 Upload File")
        uploaded_file = render_upload_section()
    
    with col2:
        st.markdown("### 📝 Paste Text")
        pasted_text = render_paste_section()
    
    # Check if either input is provided
    if not uploaded_file and not pasted_text:
        render_warning_card(
            "No Content Provided",
            "Please upload a file or paste text to begin analysis. The system needs content to analyze."
        )
        return
    
    # Validate file if uploaded
    if uploaded_file:
        if not validate_file_upload(uploaded_file.getvalue(), uploaded_file.name):
            st.error("❌ Invalid file. Please check file size and type.")
            return
    
    # Country and metadata selection
    st.markdown("---")
    st.markdown("### 🏷️ Speech Information")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        country = render_country_selection()
    
    with col2:
        speech_date = render_speech_date_selection()
    
    with col3:
        classification = render_classification_selection(country)
    
    # Check for existing data if country and year are selected
    existing_data = None
    if country and speech_date:
        year = speech_date.year
        existing_data = check_existing_data(country, year)
        
        if existing_data:
            st.info(f"ℹ️ **Note:** Speech for {country} ({year}) already exists in database ({existing_data['word_count']:,} words). Click 'Start Analysis' to analyze it.")
    
    # Model selection
    st.markdown("### 🤖 AI Model Selection")
    from ...core.llm import get_available_models
    available_models = get_available_models()
    
    if available_models:
        model = st.selectbox(
            "Choose AI Model:",
            options=available_models,
            key="new_analysis_model_select",
            index=0,
            help="Select the AI model for analysis"
        )
    else:
        model = "model-router-osaa-2"
        st.warning("⚠️ Using default model. AI service may not be available.")
    
    # Analysis button
    st.markdown("---")
    
    # Check rate limit
    user_id = st.session_state.get('user_id', 'anonymous')
    if not check_rate_limit(user_id):
        st.error("❌ Rate limit exceeded. Please wait before making another request.")
        return
    
    if st.button("🚀 Start Analysis", type="primary", use_container_width=True, key="new_analysis_start"):
        if not country:
            st.error("❌ Please select a country name.")
            return
        
        if not classification:
            st.error("❌ Please select a classification.")
            return
        
        # Process the analysis
        analysis_data = process_analysis(
            uploaded_file=uploaded_file,
            pasted_text=pasted_text,
            country=country,
            speech_date=speech_date,
            classification=classification,
            model=model
        )
        
        if analysis_data:
            # Add to analysis history
            st.session_state.analysis_history.append(analysis_data)
            
            # Store in session state for persistence across reruns
            st.session_state.current_analysis_data = analysis_data
        else:
            st.error("❌ Analysis failed. Please try again.")
    
    # Display analysis results if they exist (even after rerun)
    if 'current_analysis_data' in st.session_state and st.session_state.current_analysis_data:
        render_analysis_results(st.session_state.current_analysis_data)
    
    # Render sidebar metadata
    render_sidebar_metadata_section(uploaded_file, pasted_text)


def render_analysis_results(analysis_data: Dict[str, Any]):
    """Render the analysis results."""
    st.markdown("---")
    st.markdown("## 📊 Analysis Results")
    
    # Display basic info
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🏳️ Country", analysis_data['country'])
    with col2:
        st.metric("📅 Date", analysis_data['date'])
    with col3:
        st.metric("🏷️ Classification", analysis_data['classification'])
    with col4:
        st.metric("📝 Word Count", f"{analysis_data['word_count']:,}")
    
    # Display the speech text in a downloadable text box
    st.markdown("### 📄 Original Speech Text")
    
    # Get the full speech text
    speech_text = analysis_data.get('full_text', analysis_data.get('speech_text', ''))
    
    col1, col2 = st.columns([4, 1])
    with col1:
        st.text_area(
            "Speech Content:",
            value=speech_text,
            height=300,
            key="speech_text_display",
            help="Original speech text - you can copy or download this"
        )
    
    with col2:
        # Download button
        st.markdown("<br>", unsafe_allow_html=True)  # Spacing
        st.download_button(
            label="📥 Download Speech",
            data=speech_text,
            file_name=f"{analysis_data['country']}_{analysis_data['year']}_speech.txt",
            mime="text/plain",
            use_container_width=True
        )
        
        # Copy to clipboard info
        st.info("💡 You can also select and copy text from the box")
    
    # Display the analysis
    st.markdown("---")
    st.markdown("### 🤖 AI Analysis")
    st.markdown(analysis_data['output_markdown'])
    
    # Analysis suggestions
    st.markdown("---")
    render_analysis_suggestions(analysis_data['country'], analysis_data['classification'])
    
    # Chat interface
    render_chat_interface(
        analysis_data['output_markdown'],
        analysis_data['country'],
        analysis_data['classification']
    )
    
    # Export section
    render_export_section(analysis_data)
    
    # Store in session state for other tabs
    st.session_state.current_analysis = analysis_data
