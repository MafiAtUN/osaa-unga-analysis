# UN GA Daily Readouts

A Streamlit application for analyzing UN General Assembly speeches using AI.

**Developed by:** Mafizul Islam  
**Data Expert and Team Lead**  
**Strategic Management Unit (Data)**  
**Office of the Special Adviser on Africa**  

**Copyright:** © 2025 Mafizul Islam. All rights reserved.

## Features

- **Speech Analysis**: Upload PDF, DOCX, or MP3 files for AI analysis
- **Document Context**: Combine with UNGA corpus (1946-2024)
- **Cross-Year Analysis**: Compare speeches across multiple years
- **Data Visualization**: Interactive charts and analytics
- **Security**: Input sanitization and authentication
- **Export**: Download analyses in multiple formats

## Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables**:
   ```bash
   cp env.template .env
   # Edit .env with your API keys
   ```

3. **Set up the database**:
   ```bash
   python setup_database.py
   ```

4. **Run the application**:
   ```bash
   streamlit run app.py
   ```

## Database

- **Sample Database**: 1.8MB (5 sample speeches) - included
- **Full Database**: 802MB (complete corpus) - created on first run
- **Raw Files**: 215MB (11,109 speeches) - excluded from repository

## Requirements

- Python 3.8+
- Azure OpenAI API key
- Whisper API key (optional, for audio transcription)

## Security

- API keys stored in `.env` file (excluded from Git)
- Database files and virtual environment excluded
- Use environment variables in production