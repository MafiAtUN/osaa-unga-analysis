# UN GA Daily Readouts

A production-ready Streamlit application for analyzing UN General Assembly speeches using AI. This application has been completely refactored for better maintainability, performance, and security.

**Developed by:** Mafizul Islam  
**Data Expert and Team Lead**  
**Strategic Management Unit (Data)**  
**Office of the Special Adviser on Africa**  

**Copyright:** © 2025 Mafizul Islam. All rights reserved.

## ✨ Key Features

### 🔍 **Advanced Analysis Capabilities**
- **Speech Analysis**: Upload PDF, DOCX, or MP3 files for AI-powered analysis
- **Document Context Analysis**: Combine uploaded documents with UNGA corpus (1946-2024)
- **Cross-Year Analysis**: Compare speeches across multiple years (1946-2025)
- **Multi-language Support**: Automatic translation to English using UN terminology
- **Country Classification**: Auto-classifies African Member States vs Development Partners
- **Semantic Search**: AI-powered vector search through 78 years of speeches
- **Contextual Analysis**: Historical context integration with current documents

### 📊 **Data Visualization & Analytics**
- **Interactive Visualizations**: Advanced charts, heatmaps, and data exploration tools
- **Data Explorer**: Comprehensive visualization of speech data availability and trends
- **Historical Corpus**: Access to 78 years of UNGA speeches (1946-2024)
- **Real-time Analytics**: Live analysis with comprehensive insights
- **Trend Analysis**: Multi-year trend visualization and comparison
- **Statistical Dashboards**: Country-wise and year-wise analytics
- **Custom Visualizations**: Exportable charts and interactive graphs

### 🔒 **Enterprise Security & Performance**
- **Input Sanitization**: Advanced security measures for all user inputs
- **Rate Limiting**: Protection against abuse and overuse
- **Prompt Safety**: AI prompt validation and security checks
- **Authentication**: Secure login system with password protection
- **File Validation**: Comprehensive file upload security
- **Data Encryption**: Secure storage and transmission of sensitive data
- **Audit Logging**: Comprehensive logging for security and compliance

### 📤 **Export & Integration Features**
- **Export Options**: Download analyses as DOCX or Markdown files
- **API Integration**: Azure OpenAI and Whisper API support
- **Vector Storage**: Efficient DuckDB-based document storage
- **Error Insights**: Comprehensive error tracking and analysis
- **Batch Processing**: Multiple file analysis and batch export
- **API Endpoints**: RESTful API for programmatic access

## 🏢 Enterprise Features

### **Production-Ready Architecture**
- **Modular Design**: Clean separation of concerns with 88% code reduction
- **Scalable Infrastructure**: Handles large datasets and concurrent users
- **Security First**: Comprehensive security measures and audit logging
- **Performance Optimized**: Efficient vector search and real-time processing

### **Advanced AI Capabilities**
- **36+ Analysis Questions**: Comprehensive question sets across 13 categories
- **223+ Countries**: Automatic classification and detection
- **78 Years of Data**: Complete UNGA corpus (1946-2024)
- **Multi-language Processing**: Automatic translation and analysis
- **Semantic Search**: AI-powered vector similarity matching

### **Professional Tools**
- **Comprehensive Logging**: Detailed error tracking and performance monitoring
- **Database Management**: Automated setup with sample and full database options
- **Export Capabilities**: Multiple format support (DOCX, Markdown, JSON)
- **API Integration**: Azure OpenAI and Whisper API support
- **Error Diagnostics**: Advanced troubleshooting and system health monitoring

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
   # Choose between sample database (quick start) or full database (802MB)
   ```

4. **Run the application**:
   ```bash
   streamlit run app.py
   ```

5. **Access the app**: Open http://localhost:8501 in your browser

## 🗄️ Database Setup

### **Database Options**

The UNGA Analysis App uses a vector database to store and search through 78 years of UN General Assembly speeches (1946-2024). Due to GitHub's file size limits, the following large files are not included in the repository:

- **Full database**: 802MB (vector database with embeddings)
- **Raw speech files**: 215MB (11,109 individual speech files)
- **Total excluded**: ~1GB of data

#### **Option 1: Sample Database (Recommended for Testing)**
- **Size**: ~1.8MB
- **Content**: 5 sample speeches from different countries
- **Setup**: Automatically created with `python setup_database.py`
- **Use Case**: Quick testing and development

#### **Option 2: Full Database (Production Use)**
- **Size**: ~802MB
- **Content**: Complete UNGA corpus (1946-2024)
- **Setup**: Created when you first run the application
- **Use Case**: Full functionality with all historical data

### **Database Setup Process**

1. **Run the setup script**:
   ```bash
   python setup_database.py
   ```

2. **Choose your option**:
   - **Option 1**: Use sample database (quick start)
   - **Option 2**: Create full database (requires processing time)
   - **Option 3**: Keep existing database

3. **For full database creation**:
   - The app will automatically process all UNGA speeches
   - Estimated time: 10-30 minutes
   - Progress is shown in the application interface

### **Raw Speech Files**

The application includes access to the complete UNGA corpus (1946-2024) with 11,109 individual speech files:

- **Total size**: 215MB of raw text files
- **Coverage**: 78 years of UN General Assembly speeches
- **Format**: Individual .txt files organized by session and country
- **Languages**: Multiple languages with automatic translation support
- **Access**: Files are processed into the vector database for analysis

**Note**: Raw speech files are not included in the GitHub repository due to size limits. The application will automatically download and process them when creating the full database.

### **Database Features**
- **Vector Search**: Semantic search through speeches using AI embeddings
- **Historical Coverage**: 78 years of UNGA speeches (1946-2024)
- **Multi-language Support**: Automatic translation and processing
- **Efficient Storage**: DuckDB-based vector database
- **Real-time Updates**: New speeches can be added dynamically

## 📱 Application Tabs

### 🆕 **New Analysis**
- Upload speech files (PDF, DOCX, MP3) or paste text directly
- Auto-classify countries as African Member States or Development Partners
- Get comprehensive AI-powered analysis with historical context
- Export results as DOCX or Markdown files

### 📚 **All Analyses**
- View and manage all previous analyses
- Search and filter by country, date, or content
- Export individual or batch analyses
- Track analysis history and trends

### 📊 **Data Explorer**
- Visualize speech data availability across 78 years (1946-2024)
- Interactive charts and statistics
- Filter by country, year, or region
- Explore data patterns and trends

### 🔄 **Cross-Year Analysis**
- Compare speeches across multiple years
- Select countries or country groups
- Choose from 13 analysis categories
- Generate comparative insights and trends

### 📈 **Visualizations**
- Advanced data visualization tools
- Interactive charts and heatmaps
- Customizable analysis parameters
- Export visualizations as images

### 📄 **Document Context Analysis**
- Upload multiple documents for analysis
- Combine with UNGA corpus for historical context
- Get comprehensive document-based insights
- Advanced document processing capabilities
- Semantic similarity matching with historical speeches
- Contextual recommendations and insights

### 🔍 **Error Insights & Monitoring**
- Comprehensive error tracking and analysis
- System performance monitoring
- Debug information and logs
- Troubleshooting assistance
- Real-time system health monitoring
- Performance metrics and analytics
- Automated error reporting and resolution

## 🏗️ Architecture

The application has been completely refactored with a clean, modular architecture:

```
src/unga_analysis/
├── config/                    # Configuration and data
│   ├── questions.py          # 36+ analysis questions and prompts
│   ├── countries.py          # 223+ countries and detection logic
│   └── env.template          # Environment variables template
├── core/                     # Core business logic
│   ├── llm.py               # AI/LLM integration and analysis
│   ├── classify.py           # Country classification logic
│   ├── prompts.py           # Prompt engineering and templates
│   └── auth.py              # Authentication and security
├── data/                     # Data processing and storage
│   ├── ingest.py            # File processing and text extraction
│   ├── simple_vector_storage.py  # Vector database management
│   └── cross_year_analysis.py    # Historical analysis
├── ui/                       # User interface components
│   ├── auth.py              # Authentication UI
│   ├── components/           # Reusable UI components
│   │   ├── upload.py        # File upload component
│   │   └── country_selection.py  # Country selection UI
│   └── tabs/                 # Tab-specific functionality
│       ├── data_explorer_tab.py      # Data visualization
│       ├── document_context_analysis_tab.py  # Document analysis
│       └── error_insights_tab.py     # Error tracking
└── utils/                    # Utility functions
    ├── security.py          # Security and validation
    ├── export_utils.py      # Export functionality
    └── logging_config.py    # Logging and monitoring
```

### 🔧 **Refactoring Benefits**
- **88% size reduction** in main app file (3,071 → 500 lines)
- **Modular design** for easy maintenance and testing
- **Clean separation** of concerns (UI, business logic, data)
- **Reusable components** for consistent user experience
- **Enhanced security** with dedicated security module
- **Comprehensive logging** for debugging and monitoring

## Requirements

- Python 3.8+
- Streamlit
- OpenAI API access
- DuckDB for vector storage

## Environment Variables

Create a `.env` file with:

```env
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_ENDPOINT=your_endpoint
WHISPER_API_KEY=your_whisper_key
WHISPER_ENDPOINT=your_whisper_endpoint
APP_PASSWORD=your_app_password
```

## 🚀 Development & Deployment

### **Recent Improvements**
- **Complete refactoring** for better maintainability and performance
- **Enhanced security** with comprehensive input validation and rate limiting
- **Modular architecture** with clean separation of concerns
- **Comprehensive testing** with 100% functionality preservation
- **Production-ready** with proper error handling and logging

### **Key Technical Features**
- **36+ analysis questions** across 13 categories
- **223+ countries** with automatic classification
- **78 years of data** (1946-2024) with vector search
- **Multi-format support** (PDF, DOCX, MP3, TXT)
- **Real-time analysis** with Azure OpenAI integration
- **Advanced security** with input sanitization and prompt safety

### **Testing & Quality Assurance**
- **Comprehensive test suite** covering all functionality
- **Security validation** for all user inputs
- **Performance optimization** with efficient data structures
- **Error handling** with detailed logging and monitoring
- **Cross-platform compatibility** tested on multiple environments

## 🔧 Troubleshooting

### **Common Issues**
- **"Azure OpenAI client is required"**: Ensure your `.env` file has correct API credentials
- **Database lock errors**: Restart the application if you see DuckDB lock errors
- **Import errors**: Make sure all dependencies are installed with `pip install -r requirements.txt`
- **Authentication issues**: Check that `APP_PASSWORD` is set in your `.env` file
- **Database not found**: Run `python setup_database.py` to set up your database
- **Large database size**: Use the sample database for testing, full database for production

### **Performance Tips**
- **Large files**: For files >50MB, consider splitting into smaller chunks
- **Multiple uploads**: Process files one at a time for better performance
- **Browser compatibility**: Use modern browsers (Chrome, Firefox, Safari) for best experience

### **Database Troubleshooting**
- **Check database status**: Run `python check_database.py` to see your current setup
- **Sample database**: Use `python setup_database.py` and choose option 1 for quick testing
- **Full database**: Choose option 2 for complete functionality (requires 802MB)
- **Database corruption**: Delete `unga_vector.db` and run setup again

### **Support**
- Check the **Error Insights** tab for detailed error information
- Review application logs in the `logs/` directory
- Ensure all environment variables are properly configured
- Use `python check_database.py` to diagnose database issues

## 📄 License

Built for UN OSAA | Developed by SMU Data Team

---

**🎉 Ready to analyze UNGA speeches with AI-powered insights!**