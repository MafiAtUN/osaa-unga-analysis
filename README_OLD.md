# UN GA Daily Readouts

A production-ready Streamlit application for analyzing UN General Assembly speeches with advanced historical analysis capabilities. The app extracts text from PDF, Word documents, or MP3 audio files, automatically classifies entities as African Member States or Development Partners, and generates structured readouts using OpenAI's GPT models with **complete access to all UNGA speeches from 1946 to 2024** - enabling unprecedented comparative analysis across nearly eight decades of diplomatic history.

**Developed by: SMU Data Team**

## 🚀 New Features

- **🔐 Password Protection**: Secure access with authentication
- **💬 Interactive Chat**: Ask questions about analyzed speeches with AI-powered responses
- **📚 Historical Analysis**: Access to 78 years of UNGA speeches (1946-2024) for comparative analysis
- **🌍 Expert Translation**: Automatic translation from any language to English using UN terminology
- **🔍 Web Search Integration**: Enhanced responses with web search for additional context
- **📊 Smart Suggestions**: Pre-built question suggestions for comprehensive analysis
- **📈 Trend Analysis**: Compare current speeches with historical data

## 🔧 Recent Updates

### v2.1.0 - Dropdown Fix & UI Improvements
- **✅ Fixed Suggested Questions Dropdown**: Questions now properly load into the chat input when selected
- **🔄 Improved Session State Management**: Better handling of user interactions and form state
- **⚡ Enhanced Reactivity**: Added proper Streamlit rerun triggers for seamless user experience
- **🎯 Better UX**: Suggested questions are only cleared after user submits, not immediately after selection

## Core Features

- **Multi-format Support**: Upload PDF, DOCX, or MP3 files or paste text directly
- **Auto-classification**: Automatically detects African Union member states vs Development Partners
- **AI Analysis**: Uses OpenAI GPT models to generate structured UN-style readouts
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
- **DuckDuckGo API** - Web search functionality
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
- Azure OpenAI API access (or alternative LLM provider)

#### Step-by-Step Local Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/osaa-unga-80.git
   cd osaa-unga-80
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
   
   **Option A: Use the setup script (Recommended):**
   ```bash
   python setup_env.py
   ```
   
   **Option B: Manual setup:**
   ```bash
   # Create .env file with your API configuration
   echo "AZURE_OPENAI_API_KEY=your-azure-openai-api-key-here" > .env
   echo "AZURE_OPENAI_ENDPOINT=https://your-resource.cognitiveservices.azure.com/" >> .env
   echo "AZURE_OPENAI_API_VERSION=2024-12-01-preview" >> .env
   ```
   
   **Option C: Export environment variables:**
   ```bash
   export AZURE_OPENAI_API_KEY="your-azure-openai-api-key-here"
   export AZURE_OPENAI_ENDPOINT="https://your-resource.cognitiveservices.azure.com/"
   export AZURE_OPENAI_API_VERSION="2024-12-01-preview"
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
     -v $(pwd)/artifacts:/app/artifacts \
     unga-app
   ```

4. **Or use Docker Compose:**
   ```bash
   # Create .env file with your API credentials
   echo "AZURE_OPENAI_API_KEY=your-api-key" > .env
   echo "AZURE_OPENAI_ENDPOINT=https://your-resource.cognitiveservices.azure.com/" >> .env
   echo "AZURE_OPENAI_API_VERSION=2024-12-01-preview" >> .env
   
   # Run with docker-compose
   docker-compose up -d
   ```

5. **Access the application:**
   - Open your browser to `http://localhost:8501`

#### Docker Production Deployment

For production deployment with Docker:

```bash
# Build production image
docker build -t unga-app:production .

# Run with production settings
docker run -d \
  --name unga-app \
  -p 8501:8501 \
  -e AZURE_OPENAI_API_KEY="your-api-key" \
  -e AZURE_OPENAI_ENDPOINT="https://your-resource.cognitiveservices.azure.com/" \
  -e AZURE_OPENAI_API_VERSION="2024-12-01-preview" \
  -v /path/to/corpus:/app/artifacts/logo/unga-1946-2024-corpus \
  --restart unless-stopped \
  unga-app:production
```

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

| Provider | Model | Cost | Quality | Speed | Best For |
|----------|-------|------|---------|-------|----------|
| Azure OpenAI | GPT-4 | High | Excellent | Fast | Production |
| OpenAI | GPT-4 | High | Excellent | Fast | Production |
| Anthropic | Claude-3 | Medium | Excellent | Medium | Research |
| Google | Gemini Pro | Medium | Good | Fast | Budget |
| Ollama | Llama2 | Free | Good | Slow | Local/Privacy |
| Hugging Face | Various | Free | Variable | Variable | Experimentation |

### Switching Between Models

To switch between different AI providers:

1. **Update environment variables** with your chosen provider's credentials
2. **Modify `llm.py`** to use the new client and model
3. **Update prompts** if needed for model-specific formatting
4. **Test thoroughly** to ensure compatibility

### Recommended Configuration

- **Production**: Azure OpenAI or OpenAI API
- **Development**: Local Ollama or Hugging Face models
- **Research**: Anthropic Claude for complex analysis
- **Budget-conscious**: Google Gemini or local models

## Usage

### Authentication

1. **Login**: Enter the application password to access the system
2. **Session**: Stay logged in during your session
3. **Logout**: Click logout button when finished

### New Analysis

1. **Paste Text or Upload File**: Paste text directly (recommended) or upload a PDF, DOCX, or MP3 file
2. **Add Text**: Click "Add Text" button to process the pasted text
3. **Review English Text**: System automatically translates non-English speeches to English using UN terminology
4. **Download Options**: Download the text in TXT, DOCX, or Markdown formats
5. **Select Country/Entity**: Choose the country or entity name and optional speech date
6. **Analyze Text**: Click "Analyze Text" button to generate the readout
7. **View Analysis**: See the analysis results with structured readout
8. **Chat & Questions**: Access interactive chat features with suggestion dropdown for detailed questions

### Interactive Chat & Historical Analysis

1. **After Analysis**: Once a speech is analyzed, use the "Chat with the Text" section
2. **Ask Questions**: Use the chat interface to ask specific questions about the speech
3. **Smart Suggestions**: Choose from pre-built questions in the dropdown menu
4. **Historical Comparison**: Ask comparison questions to get insights from historical speeches
5. **Expert Translation**: The system automatically translates non-English speeches to English

### Chat Features

- **Context-Aware**: Questions are answered based on the analyzed speech content
- **Historical Data**: Access to 78 years of UNGA speeches for comparison
- **Smart Detection**: Automatically identifies when questions need historical context
- **Web Search**: Enhanced responses with additional web information
- **Immediate Display**: Answers appear immediately on screen
- **Chat History**: View all previous questions and answers

### Historical Analysis Examples

**Research & Policy Questions for UN Colleagues:**

#### 🌍 **Decade-by-Decade Evolution Analysis**
- "How has this country's approach to multilateralism evolved from the 1960s to today?"
- "Compare their stance on decolonization in the 1960s with their current position on self-determination"
- "What changes in their development priorities can be seen between the 1980s and 2020s?"

#### 📈 **Trend Analysis Across Multiple Sessions**
- "How has this country's focus on climate change evolved from their first mention to today?"
- "What trends can be observed in their statements about peace and security over the past 20 years?"
- "How has their language about gender equality evolved since the 1990s?"

#### 🔄 **Comparative Diplomatic Analysis**
- "Compare this speech with their speeches from the Cold War era (1960s-1980s)"
- "How did their position on nuclear disarmament change from the 1970s to present?"
- "What evolution can be seen in their approach to African development from the 1990s to now?"

#### 🎯 **Policy Continuity & Change**
- "What are the consistent themes in this country's UNGA statements over the past 30 years?"
- "How has their stance on UN reform evolved since the 2000s?"
- "What new priorities have emerged in their speeches since 2015 (SDGs era)?"

#### 🌐 **Regional & Global Context**
- "How has this country's position on regional integration evolved since the 1990s?"
- "Compare their approach to international cooperation in the 1970s vs. 2020s"
- "What changes in their economic development priorities can be seen over time?"

#### 📊 **Thematic Deep Dives**
- "How has this country's language about human rights evolved since the 1980s?"
- "What evolution can be seen in their approach to technology and digital transformation?"
- "How has their stance on migration and refugees changed over the past 25 years?"

#### 🔍 **Crisis Response Analysis**
- "How did this country respond to global crises in the 1970s vs. 2000s vs. 2020s?"
- "Compare their approach to global health challenges across different decades"
- "What patterns emerge in their crisis response language over time?"

### Standard Analysis Questions

**Current Speech Analysis:**
- "What are the key priorities mentioned in this speech?"
- "How did they address climate change and environmental issues?"
- "What role did they see for multilateralism and international cooperation?"

**Recent Historical Comparison:**
- "Compare this speech with their speeches from the past 5 years"
- "What trends can be observed in this country's UNGA statements over time?"
- "How has their focus on climate change evolved in recent years?"

### Viewing Analyses

- **Browse All**: View all analyses with filtering options
- **Search**: Filter by country, classification, SDGs, or content
- **View Details**: Click to see full analysis with export options
- **Export**: Download as DOCX or Markdown

### Settings

- **API Configuration**: Set OpenAI API key if not in environment
- **Statistics**: View database statistics
- **Deployment Info**: Azure deployment instructions

## Analysis Output

The app generates structured readouts with:

1. **Summary**: Three bullet points (~100 words each) focusing on:
   - Peace and security
   - Sustainable development (SDGs, Agenda 2063, climate)
   - Summit of the Future outcomes

2. **SDG Analysis**: Challenges, opportunities, and explicitly mentioned SDGs

3. **Partnerships**: Financing for Development, Sevilla Commitment, debt issues

4. **Cross-cutting Issues**: Youth, gender, AI, digital divide, inequalities

5. **Multilateralism**: UN80 Initiative, UN reform, Security Council reform

## Historical Corpus Integration

### Corpus Features

- **78 Years of Data**: Complete UNGA speeches from 1946-2024
- **200+ Countries**: Comprehensive country coverage with 3-letter codes
- **Smart Search**: Find historical speeches by country and year
- **Comparative Analysis**: Compare current speeches with historical data
- **Trend Detection**: Identify patterns and evolution over time

### Corpus Structure

```
unga-1946-2024-corpus/
├── Session 01 - 1946/          # 1946 speeches
│   ├── USA_01_1946.txt
│   ├── GBR_01_1946.txt
│   └── ...
├── Session 02 - 1947/          # 1947 speeches
│   └── ...
└── Session 79 - 2024/          # 2024 speeches
    ├── USA_79_2024.txt
    └── ...
```

### Historical Analysis Capabilities

- **Country Evolution**: Track how countries' positions have changed over time
- **Topic Trends**: Analyze how specific topics (climate, development, etc.) have evolved
- **Comparative Insights**: Compare current speeches with historical context
- **Pattern Recognition**: Identify recurring themes and priorities
- **Diplomatic Analysis**: Understand diplomatic language evolution

### 🎓 **Research & Policy Applications**

#### **For UN Researchers:**
- **Longitudinal Studies**: Track policy evolution across 78 years
- **Comparative Analysis**: Compare countries' diplomatic approaches over time
- **Trend Identification**: Identify emerging themes and priorities
- **Historical Context**: Understand current positions through historical lens

#### **For Policy Makers:**
- **Precedent Analysis**: Find historical precedents for current issues
- **Continuity Assessment**: Identify consistent vs. changing positions
- **Crisis Response Patterns**: Analyze how countries respond to global challenges
- **Diplomatic Language Evolution**: Understand how diplomatic discourse has changed

#### **For Academic Research:**
- **Quantitative Analysis**: Word frequency and theme analysis over time
- **Qualitative Insights**: Deep textual analysis of diplomatic language
- **Cross-Country Comparisons**: Compare approaches across different countries
- **Temporal Analysis**: Understand how global issues have evolved in UN discourse

### Corpus Integration System

The application includes a sophisticated corpus management system:

- **Country Code Mapping**: 200+ countries with 3-letter codes
- **Session Management**: Automatic session-to-year conversion
- **Content Analysis**: Word counts, previews, and summaries
- **Smart Search**: Keyword-based historical speech search
- **Error Handling**: Graceful fallback to web search
- **Performance**: Efficient file system access

## Classification Logic

- **African Member States**: 55 AU member countries
- **Development Partners**: All other entities including UN Secretary-General and PGA
- **Auto-detection**: Based on country name matching
- **Manual Override**: Users can override classification

## File Support

- **PDF**: pypdf with pdfminer.six fallback
- **DOCX**: python-docx library
- **MP3**: Azure OpenAI Whisper API transcription
- **Text**: Direct paste option

## Database Schema

```sql
analyses(
    id INTEGER PRIMARY KEY,
    country TEXT,
    classification TEXT,
    speech_date TEXT,
    created_at DATETIME,
    sdgs TEXT,
    africa_mentioned BOOLEAN,
    source_filename TEXT,
    raw_text TEXT,
    prompt_used TEXT,
    output_markdown TEXT
)
```

## Error Handling

- **API Retries**: Exponential backoff for Azure OpenAI API calls
- **Token Limits**: Automatic text chunking for long speeches
- **File Validation**: Error messages for unsupported formats
- **Graceful Degradation**: Fallback options when services are unavailable

## Security Considerations

- **API Keys**: Stored in environment variables (Azure OpenAI configuration)
- **File Upload**: Validated file types and sizes
- **Input Sanitization**: Text processing with safety checks
- **Database**: SQLite with parameterized queries

## Performance Optimization

- **Token Counting**: Pre-validation of input lengths
- **Chunking**: Automatic splitting of long texts
- **Caching**: Session state management
- **Async Processing**: Background analysis processing

## GitHub Storage & Repository Size

### Why the UNGA Corpus is Not Included

- **GitHub Free Limit**: 1GB repository size limit
- **Corpus Size**: ~2GB of historical speeches (1946-2024)
- **Storage Efficiency**: Users download only what they need
- **Academic Source**: Corpus available from Harvard Dataverse

### Repository Contents

**Included in Repository:**
- ✅ Application code and dependencies
- ✅ Configuration files and documentation
- ✅ Database schema and utilities
- ✅ Azure deployment scripts

**Not Included (Download Separately):**
- ❌ UNGA Historical Corpus (1946-2024)
- ❌ Large text files (~2GB)
- ❌ Binary data files

### Getting the Full Dataset

1. **Download from Harvard Dataverse**: [UNGA Corpus](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/0TJX8Y)
2. **Extract to**: `artifacts/logo/unga-1946-2024-corpus/`
3. **Verify Structure**: Ensure proper file organization
4. **Run Application**: Full functionality with historical analysis

## Troubleshooting

### Common Issues

1. **"OpenAI API key not found"**
   - Set OPENAI_API_KEY environment variable
   - Or enter key in Settings tab

2. **"Failed to extract text from PDF"**
   - Try a different PDF or convert to DOCX
   - Check if PDF is image-based (OCR not supported)

3. **"Analysis failed"**
   - Check internet connection
   - Verify OpenAI API key and quota
   - Try with a shorter text

4. **"No historical speeches found"**
   - Ensure UNGA corpus is downloaded and extracted
   - Check corpus directory structure
   - Verify country name spelling

5. **"Corpus integration failed"**
   - Verify corpus files are in correct location
   - Check file permissions
   - Ensure proper directory structure

6. **Azure deployment issues**
   - Verify startup command is set correctly
   - Check application settings for API key
   - Review deployment logs in Azure Portal

### Logs

Enable debug logging by setting:
```bash
export STREAMLIT_LOGGER_LEVEL=debug
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Submit a pull request

## License

This project is developed for UN OSAA use. Please contact the development team for licensing information.

## Support

For technical support or feature requests, please contact the development team or create an issue in the project repository.

## New Features Summary

### 🔐 Security & Authentication
- **Password Protection**: Secure access with configurable authentication
- **Session Management**: Persistent login during session
- **Logout Functionality**: Secure session termination

### 💬 Interactive Chat System
- **AI-Powered Responses**: Ask questions about analyzed speeches
- **Smart Suggestions**: Pre-built question dropdowns
- **Immediate Display**: Answers appear instantly on screen
- **Chat History**: View all previous conversations

### 📚 Historical Analysis (1946-2024)
- **78 Years of Data**: Complete UNGA speech corpus
- **Comparative Analysis**: Compare current vs historical speeches
- **Trend Detection**: Identify patterns over time
- **Country Evolution**: Track diplomatic position changes

### 🌍 Advanced Language Processing
- **Expert Translation**: Automatic translation to English
- **UN Terminology**: Specialized diplomatic language
- **Multilingual Support**: Handle speeches in any language
- **Cultural Context**: UN and diplomatic lingo expertise

### 🔍 Enhanced Search & Analysis
- **Web Search Integration**: Additional context from web
- **Smart Detection**: Automatically identify comparison needs
- **Rich Context**: Historical data + web search results
- **Comprehensive Responses**: Detailed, expert analysis

## 🎯 **Unique Value for UN Colleagues**

### **Unprecedented Historical Access**
- **Complete Archive**: Every UNGA speech from 1946-2024 in one place
- **Instant Analysis**: Compare any current speech with 78 years of historical data
- **Research Power**: Conduct longitudinal studies across nearly eight decades
- **Policy Insights**: Understand how global issues have evolved in UN discourse

### **Research Questions You Can Now Answer**
- "How has the language around climate change evolved in UNGA speeches since the 1970s?"
- "What patterns emerge in how countries discuss multilateralism during different global crises?"
- "How have African countries' priorities shifted since the end of apartheid?"
- "What evolution can be seen in discussions about women's rights from the 1980s to today?"

### **Policy Applications**
- **Precedent Finding**: "How did countries address similar crises in the past?"
- **Continuity Analysis**: "What themes have remained consistent in this country's approach?"
- **Trend Identification**: "What new priorities are emerging in global discourse?"
- **Comparative Diplomacy**: "How do different countries approach the same issues over time?"

---

**Built for UN OSAA | Production-ready | Azure-deployed | Historical Analysis Enabled**

**Corpus Source**: [Harvard Dataverse - UNGA Corpus](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/0TJX8Y)
