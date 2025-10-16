# UN GA Speech Analysis Platform

A comprehensive Streamlit application for analyzing UN General Assembly speeches with AI-powered insights, cross-year analysis, and advanced visualizations. Features a complete historical corpus (1946-2024) with semantic search capabilities.

**Developed by: Mafizul Islam ([@MafiAtUN](https://github.com/MafiAtUN))**

## 🚀 Key Features

### Core Analysis
- **Multi-format Support**: PDF, DOCX, MP3 files or direct text input
- **AI-Powered Analysis**: Generate structured UN-style readouts with SDG mapping
- **Interactive Chat**: Ask questions about analyzed speeches
- **Export Options**: Download analyses as DOCX or Markdown

### Historical Corpus & Cross-Year Analysis
- **Complete Historical Database**: 22,216+ speeches from 1946-2024 (78 years)
- **Semantic Search**: Vector-based similarity search using sentence transformers
- **Cross-Year Analysis**: Analyze trends across decades with AI insights
- **Country & Regional Analysis**: Compare speeches by country, region, or coalition
- **Gender & Equality Analysis**: Specialized analysis of gender-related discourse

### Advanced Visualizations
- **Issue Salience Over Time**: Track topic evolution across decades
- **Country Position Mapping**: Semantic positioning of countries in policy space
- **Similar Speech Analysis**: Find countries with similar rhetorical patterns
- **Topic Composition**: Breakdown of speech content by themes
- **Keyword Trajectories**: Track phrase evolution over time
- **Sentiment & Tone Analysis**: Emotional and rhetorical tone tracking
- **Network Analysis**: Country-topic and co-mention networks
- **Event-Aligned Timelines**: Connect speeches to historical events

### Technical Features
- **Vector Database**: DuckDB with embeddings for fast semantic search
- **Language Detection & Translation**: Automatic translation to English
- **Security**: Password protection and input validation
- **Modular Architecture**: Clean separation of concerns

## 📊 Database Statistics

- **Total Speeches**: 22,216+
- **Time Period**: 1946-2024 (78 years)
- **Countries**: 193+ UN member states
- **Languages**: Multi-language support with auto-translation
- **Storage**: DuckDB vector database with embeddings

## 🛠️ Installation & Setup

### 1. Local Installation

```bash
# Clone repository
git clone https://github.com/MafiAtUN/osaa-unga-80.git
cd osaa-unga-80

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp env.template .env
# Edit .env with your API keys

# Run application
streamlit run app.py
```

### 2. Docker Installation

```bash
# Build and run with Docker
docker build -t unga-app .
docker run -p 8502:8502 \
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

## ⚙️ Configuration

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

## 🤖 AI Model Options

### Default: Azure OpenAI
- GPT-4 and GPT-3.5 models
- Whisper for audio transcription
- Enterprise security and compliance

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

## 📖 Usage Guide

### 1. New Speech Analysis
1. **Access**: Navigate to `http://localhost:8502`
2. **Login**: Enter application password
3. **Upload**: Upload file or paste speech text
4. **Configure**: Select country and classification
5. **Analyze**: Click "Analyze Speech" to generate readout
6. **Chat**: Ask questions about the analysis
7. **Export**: Download results in various formats

### 2. Cross-Year Analysis
1. **Select Analysis Type**: Choose "Individual Countries" or "Country Groups"
2. **Choose Countries**: Select specific countries or groups
3. **Pick Questions**: Select from 12 categories of analytical questions
4. **Customize Prompt**: Modify the analysis prompt as needed
5. **Analyze**: Get comprehensive cross-year insights
6. **View Results**: See detailed analysis with tables and statistics

### 3. Data Explorer
1. **Browse Corpus**: Explore the complete historical database
2. **Filter by**: Year, country, region, or keywords
3. **View Statistics**: See data availability and coverage
4. **Search**: Use semantic search to find relevant speeches

### 4. Advanced Visualizations
1. **Issue Salience**: Track topic evolution over time
2. **Country Positions**: Map countries in semantic space
3. **Similarity Analysis**: Find countries with similar rhetoric
4. **Network Analysis**: Explore country-topic relationships

## 🏗️ Project Structure

```
osaa-unga-80/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── env.template             # Environment variables template
├── artifacts/               # Assets and corpus data
│   ├── logo/               # Logos and branding
│   └── unga-1946-2024-corpus/  # Historical speech corpus
├── tabs/                    # Modular UI components
│   └── cross_year_analysis_tab.py
├── prompts.py               # LLM prompts and templates
├── classify.py              # Classification logic
├── ingest.py                # File processing and ingestion
├── llm.py                   # LLM integration (Azure OpenAI)
├── simple_vector_storage.py # DuckDB vector database with embeddings
├── cross_year_analysis.py   # Cross-year analysis with semantic search
├── data_ingestion.py        # Data ingestion system
├── visualization.py         # Advanced visualization components
├── sdg_utils.py             # SDG processing utilities
├── export_utils.py          # Export functionality
├── unga_vector.db          # DuckDB database file
└── README.md               # This file
```

## 🔍 Analysis Categories

### 1. Issue Salience Over Time
- Climate change evolution from 1946-2025
- Topic frequency and emergence patterns
- Regional priority differences

### 2. Country Positioning & Ideological Shifts
- Semantic similarity analysis
- Rhetorical position mapping
- Ideological movement tracking

### 3. Similar Speech Analysis
- Cross-country rhetorical similarity
- Regional alignment patterns
- Historical comparison

### 4. Regional & Coalition Comparisons
- G77, EU, AU, BRICS analysis
- Regional priority differences
- Alliance rhetoric patterns

### 5. Topic Composition Analysis
- Speech content breakdown
- Theme distribution by country
- Temporal topic evolution

### 6. Keyword & Phrase Trajectories
- Term emergence tracking
- Phrase evolution analysis
- Buzzword identification

### 7. Sentiment, Tone & Emotion
- Optimism/pessimism tracking
- Emotional tone analysis
- Crisis response patterns

### 8. Country-Topic Networks
- Bipartite network analysis
- Issue ownership mapping
- Cross-issue linkages

### 9. Co-mention & Entity Networks
- Country co-mention patterns
- Organization relationships
- Alliance signaling

### 10. Event-Aligned Timeline Analysis
- Crisis response tracking
- Historical event correlation
- Policy shift identification

### 11. Speaker & Protocol Metadata
- Head-of-state vs minister patterns
- Gender representation analysis
- Speaking time distribution

### 12. Cross-Year & Cross-Topic Comparison
- Decade-by-decade analysis
- North-South comparisons
- Theme evolution tracking

### 13. Gender & Equality Analysis
- Gender-related term frequency
- Women's rights discourse evolution
- Gender mainstreaming tracking
- Female leadership analysis

## 🔒 Security Features

- **Input Sanitization**: Comprehensive validation and cleaning
- **Rate Limiting**: 5 attempts per 5 minutes
- **File Security**: 50MB limit, PDF/DOCX/MP3 only
- **LLM Protection**: Jailbreak protection and content filtering
- **Authentication**: Password-based access control
- **Data Privacy**: Secure handling of sensitive UN content

## 📊 Database Schema

### Speeches Table
- `id`: Unique identifier
- `country`: Country name
- `year`: Speech year
- `speaker`: Speaker name and title
- `speech_text`: Full speech content
- `translated_text`: English translation
- `language`: Original language
- `region`: Geographic region
- `word_count`: Speech length
- `embedding`: Vector representation (384 dimensions)

### Analysis Results Table
- `id`: Unique identifier
- `country`: Analyzed country
- `year`: Analysis year
- `analysis_type`: Type of analysis
- `results`: Analysis output
- `timestamp`: Creation time

## 🚀 Performance Features

- **Vector Search**: Fast semantic similarity using DuckDB
- **Caching**: Intelligent result caching
- **Batch Processing**: Efficient bulk operations
- **Memory Management**: Optimized for large datasets
- **Concurrent Access**: Multi-user support

## 🔧 Development

### Running Locally
```bash
# Start development server
streamlit run app.py

# Run with specific port
streamlit run app.py --server.port 8502
```

### Testing
```bash
# Run tests (when implemented)
python -m pytest tests/

# Test specific modules
python -m pytest tests/test_analysis.py
```

### Adding New Features
1. Create new modules in appropriate directories
2. Update `app.py` to include new functionality
3. Add tests for new features
4. Update documentation

## 📈 Recent Updates

### Version 2.0 (Current)
- ✅ Complete historical corpus integration (1946-2024)
- ✅ Advanced cross-year analysis with AI insights
- ✅ Comprehensive visualization suite
- ✅ Semantic search with vector embeddings
- ✅ Gender & equality analysis framework
- ✅ Modular architecture with clean separation
- ✅ Enhanced security and performance

### Version 1.0 (Previous)
- Basic speech analysis and SDG mapping
- Simple export functionality
- Azure OpenAI integration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Support

- **Issues**: Create an issue in the GitHub repository
- **Documentation**: Check the repository wiki
- **Contact**: Mafizul Islam ([@MafiAtUN](https://github.com/MafiAtUN))
- **Email**: [Your email address]

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **UN General Assembly**: For providing the historical speech corpus
- **Harvard Dataverse**: For hosting the UNGA dataset
- **Azure OpenAI**: For providing AI capabilities
- **Streamlit**: For the excellent web framework
- **DuckDB**: For high-performance vector database capabilities

---

**Copyright © 2025 Mafizul Islam ([@MafiAtUN](https://github.com/MafiAtUN)). All rights reserved.**

**Ready for production deployment with comprehensive UN speech analysis capabilities!** 🚀

## 🌐 Live Demo

Access the live application at: [Your deployment URL]

## 📊 System Requirements

- **Python**: 3.9+
- **Memory**: 8GB RAM minimum (16GB recommended)
- **Storage**: 2GB for corpus data
- **Network**: Stable internet for AI API calls