# UN GA Daily Readouts

A production-ready Streamlit application for analyzing UN General Assembly speeches with advanced historical analysis capabilities. The app extracts text from PDF, Word documents, or MP3 audio files, automatically classifies entities as African Member States or Development Partners, and generates structured readouts using AI models with **complete access to all UNGA speeches from 1946 to 2024** - enabling unprecedented comparative analysis across nearly eight decades of diplomatic history.

**Developed by: SMU Data Team**

## 🚀 Features

- **🔐 Password Protection**: Secure access with authentication
- **💬 Interactive Chat**: Ask questions about analyzed speeches with AI-powered responses
- **📚 Historical Analysis**: Access to 78 years of UNGA speeches (1946-2024) for comparative analysis
- **🌍 Expert Translation**: Automatic translation from any language to English using UN terminology
- **🔍 Web Search Integration**: Enhanced responses with web search for additional context
- **📊 Smart Suggestions**: Pre-built question suggestions for comprehensive analysis
- **📈 Trend Analysis**: Compare current speeches with historical data

## Core Features

- **Multi-format Support**: Upload PDF, DOCX, or MP3 files or paste text directly
- **Auto-classification**: Automatically detects African Union member states vs Development Partners
- **AI Analysis**: Uses AI models to generate structured UN-style readouts
- **SDG Detection**: Automatically identifies mentioned Sustainable Development Goals
- **Database Storage**: SQLite database with full search and filtering capabilities
- **Export Options**: Download analyses as DOCX or Markdown files
- **Azure Ready**: Designed for deployment on Azure App Service

## Tech Stack

- **Python 3.11+**
- **Streamlit** - Web UI framework
- **Azure OpenAI API** - GPT models and Whisper transcription
- **SQLAlchemy** - Database ORM
- **pypdf/pdfminer.six** - PDF text extraction
- **python-docx** - Word document processing
- **pydub** - Audio file handling
- **tiktoken** - Token counting
- **python-dotenv** - Environment variable management
- **requests** - Web search integration
- **UNGA Corpus Integration** - Historical speech analysis (1946-2024)

## Installation

### Prerequisites

**Important**: This application requires the UNGA Historical Corpus (1946-2024) for full functionality. Due to GitHub's storage limitations, the corpus is not included in this repository.

### UNGA Historical Corpus Setup

1. **Download the UNGA Corpus:**
   - Visit: [Harvard Dataverse - UNGA Corpus](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/0TJX8Y)
   - Download the complete dataset
   - Extract to: `artifacts/logo/unga-1946-2024-corpus/`

2. **Expected Corpus Structure:**
   ```
   artifacts/logo/unga-1946-2024-corpus/
   ├── Session 01 - 1946/
   │   ├── USA_01_1946.txt
   │   ├── GBR_01_1946.txt
   │   └── ...
   ├── Session 02 - 1947/
   │   ├── USA_02_1947.txt
   │   └── ...
   └── Session 79 - 2024/
       ├── USA_79_2024.txt
       └── ...
   ```

3. **Corpus Features:**
   - **78 Years**: 1946-2024 UNGA speeches
   - **200+ Countries**: Complete country coverage
   - **File Format**: `{COUNTRY_CODE}_{SESSION}_{YEAR}.txt`
   - **Size**: ~2GB total (not included in repository)

## 🚀 Installation Options

### Option 1: Local Development

#### Prerequisites
- Python 3.11 or higher
- Git
- AI API access (Azure OpenAI, OpenAI, Anthropic, etc.)

#### Step-by-Step Local Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/MafiAtUN/osaa-unga-analysis.git
   cd osaa-unga-analysis
   ```

2. **Create and activate virtual environment:**
   ```bash
   # Create virtual environment
   python3 -m venv osaaunga
   
   # Activate virtual environment
   # On macOS/Linux:
   source osaaunga/bin/activate
   # On Windows:
   osaaunga\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download and setup UNGA corpus:**
   ```bash
   # Create corpus directory
   mkdir -p artifacts/logo/unga-1946-2024-corpus
   
   # Download from Harvard Dataverse (manual step)
   # Extract the downloaded files to artifacts/logo/unga-1946-2024-corpus/
   ```

5. **Configure API access:**
   
   **Option A: Use environment template:**
   ```bash
   # Copy template and edit
   cp env.template .env
   # Edit .env with your API configuration
   ```
   
   **Option B: Export environment variables:**
   ```bash
   export AZURE_OPENAI_API_KEY="your-azure-openai-api-key-here"
   export AZURE_OPENAI_ENDPOINT="https://your-resource.cognitiveservices.azure.com/"
   export AZURE_OPENAI_API_VERSION="2024-12-01-preview"
   export APP_PASSWORD="your-secure-password"
   ```

6. **Run the application:**
   ```bash
   streamlit run app.py
   ```

The app will be available at `http://localhost:8501`

### Option 2: Docker Deployment

#### Prerequisites
- Docker installed on your system
- Docker Compose (optional, for easier management)

#### Docker Installation

1. **Create Dockerfile:**
   ```dockerfile
   FROM python:3.11-slim

   # Set working directory
   WORKDIR /app

   # Install system dependencies
   RUN apt-get update && apt-get install -y \
       gcc \
       g++ \
       && rm -rf /var/lib/apt/lists/*

   # Copy requirements and install Python dependencies
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   # Copy application code
   COPY . .

   # Create corpus directory
   RUN mkdir -p artifacts/logo/unga-1946-2024-corpus

   # Expose port
   EXPOSE 8501

   # Health check
   HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

   # Run the application
   CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
   ```

2. **Create docker-compose.yml:**
   ```yaml
   version: '3.8'
   
   services:
     unga-app:
       build: .
       ports:
         - "8501:8501"
       environment:
         - AZURE_OPENAI_API_KEY=${AZURE_OPENAI_API_KEY}
         - AZURE_OPENAI_ENDPOINT=${AZURE_OPENAI_ENDPOINT}
         - AZURE_OPENAI_API_VERSION=${AZURE_OPENAI_API_VERSION}
         - APP_PASSWORD=${APP_PASSWORD}
       volumes:
         - ./artifacts:/app/artifacts
       restart: unless-stopped
   ```

3. **Build and run with Docker:**
   ```bash
   # Build the image
   docker build -t unga-app .
   
   # Run the container
   docker run -p 8501:8501 \
     -e AZURE_OPENAI_API_KEY="your-api-key" \
     -e AZURE_OPENAI_ENDPOINT="https://your-resource.cognitiveservices.azure.com/" \
     -e AZURE_OPENAI_API_VERSION="2024-12-01-preview" \
     -e APP_PASSWORD="your-secure-password" \
     -v $(pwd)/artifacts:/app/artifacts \
     unga-app
   ```

4. **Or use Docker Compose:**
   ```bash
   # Create .env file with your API credentials
   echo "AZURE_OPENAI_API_KEY=your-api-key" > .env
   echo "AZURE_OPENAI_ENDPOINT=https://your-resource.cognitiveservices.azure.com/" >> .env
   echo "AZURE_OPENAI_API_VERSION=2024-12-01-preview" >> .env
   echo "APP_PASSWORD=your-secure-password" >> .env
   
   # Run with docker-compose
   docker-compose up -d
   ```

5. **Access the application:**
   - Open your browser to `http://localhost:8501`

### Option 3: Azure App Service Deployment

#### Prerequisites
- Azure subscription
- Azure CLI installed
- Git repository access

#### Azure Deployment Steps

1. **Create Azure App Service:**
   ```bash
   # Create resource group
   az group create --name myResourceGroup --location "East US"
   
   # Create App Service plan
   az appservice plan create \
     --name myAppServicePlan \
     --resource-group myResourceGroup \
     --sku B1 \
     --is-linux
   
   # Create web app
   az webapp create \
     --resource-group myResourceGroup \
     --plan myAppServicePlan \
     --name my-un-ga-app \
     --runtime "PYTHON|3.11"
   ```

2. **Configure environment variables:**
   ```bash
   az webapp config appsettings set \
     --resource-group myResourceGroup \
     --name my-un-ga-app \
     --settings \
     AZURE_OPENAI_API_KEY="your-azure-openai-api-key-here" \
     AZURE_OPENAI_ENDPOINT="https://your-resource.cognitiveservices.azure.com/" \
     AZURE_OPENAI_API_VERSION="2024-12-01-preview" \
     APP_PASSWORD="your-secure-password" \
     WEBSITES_PORT="8501"
   ```

3. **Deploy via Git:**
   ```bash
   # Add Azure remote
   git remote add azure https://my-un-ga-app.scm.azurewebsites.net/my-un-ga-app.git
   
   # Deploy
   git add .
   git commit -m "Deploy UN GA app"
   git push azure main
   ```

4. **Set startup command:**
   ```bash
   az webapp config set \
     --resource-group myResourceGroup \
     --name my-un-ga-app \
     --startup-file "streamlit run app.py --server.port $PORT --server.address 0.0.0.0"
   ```

#### Alternative: ZIP Deployment

1. **Create deployment package:**
   ```bash
   # Create ZIP file
   zip -r app-deployment.zip . -x "*.git*" "*.pyc" "__pycache__/*"
   ```

2. **Deploy via Azure Portal:**
   - Go to your App Service in Azure Portal
   - Navigate to Deployment Center
   - Choose "ZIP Deploy"
   - Upload your ZIP file

#### Azure Configuration

**Application Settings:**
```
AZURE_OPENAI_API_KEY = your-azure-openai-api-key-here
AZURE_OPENAI_ENDPOINT = https://your-resource.cognitiveservices.azure.com/
AZURE_OPENAI_API_VERSION = 2024-12-01-preview
APP_PASSWORD = your-secure-password
WEBSITES_PORT = 8501
```

**Startup Command:**
```
streamlit run app.py --server.port $PORT --server.address 0.0.0.0
```

## 🤖 AI Model Configuration

### Azure OpenAI API (Default)

This application is configured to use **Azure OpenAI API** by default, which provides:

- **GPT-4 and GPT-3.5 models** for text analysis
- **Whisper API** for audio transcription
- **Enterprise-grade security** and compliance
- **High availability** and reliability

#### Azure OpenAI Setup

1. **Create Azure OpenAI Resource:**
   - Go to [Azure Portal](https://portal.azure.com)
   - Create a new "Azure OpenAI" resource
   - Deploy GPT-4 and GPT-3.5-turbo models
   - Note your endpoint and API key

2. **Configure Environment Variables:**
   ```bash
   AZURE_OPENAI_API_KEY=your-azure-openai-api-key
   AZURE_OPENAI_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
   AZURE_OPENAI_API_VERSION=2024-12-01-preview
   ```

### Alternative LLM Providers

If you prefer to use other AI models, you can modify the application to work with different providers:

#### Option 1: OpenAI API (Direct)

**Modify `llm.py`:**
```python
from openai import OpenAI

# Replace Azure OpenAI client with direct OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Update model names
MODEL_NAME = "gpt-4"  # or "gpt-3.5-turbo"
```

**Environment Variables:**
```bash
OPENAI_API_KEY=your-openai-api-key
```

#### Option 2: Anthropic Claude

**Install Claude SDK:**
```bash
pip install anthropic
```

**Modify `llm.py`:**
```python
import anthropic

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def run_analysis_with_claude(text, country, classification):
    response = client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=4000,
        messages=[{
            "role": "user",
            "content": f"Analyze this UN speech: {text}"
        }]
    )
    return response.content[0].text
```

**Environment Variables:**
```bash
ANTHROPIC_API_KEY=your-anthropic-api-key
```

#### Option 3: Google Gemini

**Install Gemini SDK:**
```bash
pip install google-generativeai
```

**Modify `llm.py`:**
```python
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-pro')

def run_analysis_with_gemini(text, country, classification):
    response = model.generate_content(f"Analyze this UN speech: {text}")
    return response.text
```

**Environment Variables:**
```bash
GEMINI_API_KEY=your-gemini-api-key
```

#### Option 4: Local Models (Ollama)

**Install Ollama:**
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model
ollama pull llama2
```

**Modify `llm.py`:**
```python
import requests

def run_analysis_with_ollama(text, country, classification):
    response = requests.post('http://localhost:11434/api/generate',
        json={
            'model': 'llama2',
            'prompt': f'Analyze this UN speech: {text}',
            'stream': False
        }
    )
    return response.json()['response']
```

#### Option 5: Hugging Face Transformers

**Install Transformers:**
```bash
pip install transformers torch
```

**Modify `llm.py`:**
```python
from transformers import pipeline

# Load a text generation model
generator = pipeline('text-generation', model='microsoft/DialoGPT-medium')

def run_analysis_with_hf(text, country, classification):
    response = generator(f"Analyze this UN speech: {text}", max_length=1000)
    return response[0]['generated_text']
```

### Model Comparison

| Provider | Model | Cost | Quality | Speed | Setup |
|----------|-------|------|---------|-------|-------|
| **Azure OpenAI** | GPT-4 | High | Excellent | Fast | Easy |
| **OpenAI** | GPT-4 | High | Excellent | Fast | Easy |
| **Anthropic** | Claude-3 | Medium | Excellent | Medium | Easy |
| **Google** | Gemini-Pro | Low | Good | Fast | Easy |
| **Ollama** | Llama2 | Free | Good | Slow | Medium |
| **Hugging Face** | Various | Free | Variable | Variable | Hard |

## 🔒 Security Features

- **Input Sanitization**: Comprehensive HTML escaping and pattern removal
- **Rate Limiting**: Protection against brute force attacks
- **Authentication**: Secure password-based authentication
- **File Validation**: Secure file uploads with size and type checks
- **Prompt Safety**: LLM injection attack prevention
- **Security Logging**: Comprehensive security event logging

## 📊 Usage

### Basic Workflow

1. **Access the Application**: Navigate to the URL (local: `http://localhost:8501`)
2. **Authentication**: Enter the application password
3. **Upload or Paste**: Upload a file or paste speech text
4. **Configure Analysis**: Select country and classification
5. **Generate Analysis**: Click "Analyze Speech" to generate the readout
6. **Interactive Chat**: Ask questions about the analysis
7. **Export Results**: Download the analysis in various formats

### Advanced Features

- **Historical Comparison**: Compare with past speeches from the corpus
- **SDG Mapping**: Automatic detection of Sustainable Development Goals
- **Multi-language Support**: Automatic translation to English
- **Export Options**: DOCX, Markdown, and JSON formats

## 🛠️ Development

### Project Structure

```
osaa-unga-80/
├── app.py                    # Main application
├── app_professional.py       # Professional demonstration version
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

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Testing

```bash
# Run the application locally
streamlit run app.py

# Test with different models
# Modify llm.py to use different providers
```

## 📚 Documentation

- **README.md**: This file
- **SECURITY.md**: Security documentation
- **LICENSE**: MIT License
- **env.template**: Environment configuration template

## 👨‍💻 Development Team

**SMU Data Team** - UN GA Analysis Platform

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Support

For support and questions:
- Create an issue in the GitHub repository
- Contact the development team
- Check the documentation

---

**Ready for production deployment on Azure App Service!** 🚀
