# UN GA Daily Readouts

A production-ready Streamlit application for analyzing UN General Assembly speeches. The app extracts text from PDF, Word documents, or MP3 audio files, automatically classifies entities as African Member States or Development Partners, and generates structured readouts using OpenAI's GPT models.

## Features

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

## Installation

### Local Development

1. **Clone and setup virtual environment:**
   ```bash
   cd osaa-unga-80
   python3 -m venv osaaunga
   source osaaunga/bin/activate  # On Windows: osaaunga\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   
   **Option A: Use the setup script (Recommended):**
   ```bash
   python setup_env.py
   ```
   
   **Option B: Manual setup:**
   ```bash
   # Create .env file with your Azure OpenAI configuration
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

4. **Run the application:**
   ```bash
   streamlit run app.py
   ```

The app will be available at `http://localhost:8501`

### Azure App Service Deployment

#### Prerequisites
- Azure subscription
- OpenAI API key
- Git repository (optional)

#### Deployment Steps

1. **Create Azure App Service:**
   ```bash
   az webapp create \
     --resource-group myResourceGroup \
     --plan myAppServicePlan \
     --name my-un-ga-app \
     --runtime "PYTHON|3.11"
   ```

2. **Set Environment Variables:**
   ```bash
   az webapp config appsettings set \
     --resource-group myResourceGroup \
     --name my-un-ga-app \
     --settings AZURE_OPENAI_API_KEY="your-azure-openai-api-key-here" \
     --settings AZURE_OPENAI_ENDPOINT="https://your-resource.cognitiveservices.azure.com/" \
     --settings AZURE_OPENAI_API_VERSION="2024-12-01-preview"
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

4. **Set Startup Command:**
   ```bash
   az webapp config set \
     --resource-group myResourceGroup \
     --name my-un-ga-app \
     --startup-file "streamlit run app.py --server.port $PORT --server.address 0.0.0.0"
   ```

#### Alternative: ZIP Deployment

1. Create a ZIP file containing all project files
2. Upload via Azure Portal:
   - Go to your App Service
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

## Usage

### New Analysis

1. **Upload Document**: Choose a PDF, DOCX, or MP3 file
2. **Or Paste Text**: Alternative to file upload
3. **Enter Metadata**: Country/Entity name and optional speech date
4. **Review Classification**: Auto-detected classification (can be overridden)
5. **Select Model**: Choose OpenAI model (default: gpt-4o)
6. **Analyze**: Click "Analyze Speech" to generate the readout

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

4. **Azure deployment issues**
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

---

**Built for UN OSAA | Production-ready | Azure-deployed**
