# UN GA Daily Readouts

A Streamlit application for analyzing UN General Assembly speeches with AI-powered insights. Upload PDF, DOCX, or MP3 files, or paste text directly to generate structured readouts with SDG mapping and historical analysis.

**Developed by: SMU Data Team**

## Features

- **Multi-format Support**: PDF, DOCX, MP3 files or direct text input
- **AI Analysis**: Generate structured UN-style readouts
- **SDG Detection**: Automatic Sustainable Development Goals identification
- **Historical Analysis**: Access to 78 years of UNGA speeches (1946-2024)
- **Interactive Chat**: Ask questions about analyzed speeches
- **Export Options**: Download analyses as DOCX or Markdown
- **Security**: Password protection and input validation

## Quick Start

### 1. Local Installation

```bash
# Clone repository
git clone https://github.com/MafiAtUN/osaa-unga-analysis.git
cd osaa-unga-analysis

# Create virtual environment
python3 -m venv osaaunga
source osaaunga/bin/activate  # On Windows: osaaunga\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp env.template .env
# Edit .env with your API keys

# Run application
streamlit run app.py
```

### 2. Docker Installation

```bash
# Build and run with Docker
docker build -t unga-app .
docker run -p 8501:8501 \
  -e AZURE_OPENAI_API_KEY="your-api-key" \
  -e AZURE_OPENAI_ENDPOINT="https://your-resource.cognitiveservices.azure.com/" \
  -e APP_PASSWORD="your-password" \
  unga-app
```

### 3. Azure Deployment

```bash
# Deploy to Azure App Service
git remote add azure https://your-app.scm.azurewebsites.net/your-app.git
git push azure main

# Set startup command in Azure Portal:
# streamlit run app.py --server.port $PORT --server.address 0.0.0.0
```

## Configuration

### Required Environment Variables

```bash
AZURE_OPENAI_API_KEY=your-azure-openai-api-key
AZURE_OPENAI_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
APP_PASSWORD=your-secure-password
```

### Optional Variables

```bash
AZURE_OPENAI_API_VERSION=2024-12-01-preview
RATE_LIMIT_ATTEMPTS=5
MAX_FILE_SIZE=52428800
```

## AI Model Options

### Default: Azure OpenAI
- GPT-4 and GPT-3.5 models
- Whisper for audio transcription
- Enterprise security

### Alternative Providers

**OpenAI (Direct):**
```python
# Modify llm.py
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
```

**Anthropic Claude:**
```bash
pip install anthropic
# Set ANTHROPIC_API_KEY environment variable
```

**Google Gemini:**
```bash
pip install google-generativeai
# Set GEMINI_API_KEY environment variable
```

**Local Models (Ollama):**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama2
```

## Usage

1. **Access**: Navigate to `http://localhost:8501`
2. **Login**: Enter application password
3. **Upload**: Upload file or paste speech text
4. **Configure**: Select country and classification
5. **Analyze**: Click "Analyze Speech" to generate readout
6. **Chat**: Ask questions about the analysis
7. **Export**: Download results in various formats

## Project Structure

```
osaa-unga-80/
├── app.py                    # Main application
├── app_professional.py       # Professional demo version
├── requirements.txt          # Dependencies
├── env.template             # Environment template
├── web.config               # Azure configuration
├── startup.sh               # Startup script
├── artifacts/               # Assets and corpus data
├── prompts.py               # LLM prompts
├── corpus_integration.py    # Corpus management
├── classify.py              # Classification logic
├── ingest.py                # File processing
├── llm.py                   # LLM integration
├── storage.py               # Database operations
├── sdg_utils.py             # SDG processing
└── export_utils.py          # Export functionality
```

## Security Features

- Input sanitization and validation
- Rate limiting (5 attempts per 5 minutes)
- Secure file uploads (50MB limit, PDF/DOCX/MP3 only)
- LLM jailbreak protection
- Password-based authentication

## UNGA Historical Corpus

**Important**: Download the UNGA corpus for full functionality:

1. Visit: [Harvard Dataverse - UNGA Corpus](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/0TJX8Y)
2. Download and extract to: `artifacts/logo/unga-1946-2024-corpus/`

## Development

```bash
# Run locally
streamlit run app.py

# Test different models
# Modify llm.py for different AI providers
```

## Support

- Create an issue in the GitHub repository
- Check documentation in the repository
- Contact the development team

---

**Copyright © 2025 MafiAtUN. All rights reserved.**

**Ready for production deployment on Azure App Service!** 🚀