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

### Database Options

The UNGA Analysis App uses a vector database to store and search through 78 years of UN General Assembly speeches (1946-2024). Due to GitHub's file size limits, the following large files are not included in the repository:

- **Full database**: 802MB (vector database with embeddings)
- **Raw speech files**: 215MB (11,109 individual speech files)
- **Total excluded**: ~1GB of data

#### Option 1: Sample Database (Recommended for Testing)
- **Size**: ~1.8MB
- **Content**: 5 sample speeches from different countries
- **Setup**: Automatically created with `python setup_database.py`
- **Use Case**: Quick testing and development

#### Option 2: Full Database (Production Use)
- **Size**: ~802MB
- **Content**: Complete UNGA corpus (1946-2024)
- **Setup**: Created when you first run the application
- **Use Case**: Full functionality with all historical data

### Database Setup Process

1. **For sample database**:
   - Run `python setup_database.py`
   - Choose option 1 for sample database
   - Database created in ~30 seconds

2. **For full database creation**:
   - The app will automatically process all UNGA speeches
   - Estimated time: 10-30 minutes
   - Progress is shown in the application interface

### Raw Speech Files

The application includes access to the complete UNGA corpus (1946-2024) with 11,109 individual speech files:

- **Total size**: 215MB of raw text files
- **Coverage**: 78 years of UN General Assembly speeches
- **Format**: Individual .txt files organized by session and country
- **Languages**: Multiple languages with automatic translation support
- **Access**: Files are processed into the vector database for analysis

**Note**: Raw speech files are not included in the GitHub repository due to size limits. The application will automatically download and process them when creating the full database.

## Requirements

- Python 3.8+
- Azure OpenAI API key
- Whisper API key (optional, for audio transcription)

## Security

- API keys stored in `.env` file (excluded from Git)
- Database files and virtual environment excluded
- Use environment variables in production