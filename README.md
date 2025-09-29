# 🇺🇳 UN GA Daily Readouts

**Professional UN General Assembly Speech Analysis Platform**

A production-ready Streamlit application for analyzing UN General Assembly speeches with AI-powered insights, SDG mapping, and comprehensive security features.

## 🏗️ Architecture

### **Clean Professional Structure**
```
osaa-unga-80/
├── app.py                    # Main production application (2,040 lines)
├── app_professional.py       # Professional demonstration version
├── requirements.txt          # Dependencies
├── README.md                 # Documentation
├── SECURITY.md              # Security documentation
├── LICENSE                  # License
├── env.template             # Environment template
├── web.config               # Azure configuration
├── startup.sh               # Startup script
├── logo.svg                 # Logo
├── artifacts/               # Assets and corpus data
├── prompts.py               # Core modules
├── corpus_integration.py
├── classify.py
├── ingest.py
├── llm.py
├── storage.py
├── sdg_utils.py
└── export_utils.py
```

## 🚀 Quick Start

### **Local Development**
```bash
# Clone repository
git clone https://github.com/MafiAtUN/osaa-unga-analysis.git
cd osaa-unga-analysis

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp env.template .env
# Edit .env with your configuration

# Run application
streamlit run app.py
```

### **Azure Deployment**
```bash
# Deploy to Azure App Service
# Update startup command: streamlit run app.py --server.port $PORT --server.address 0.0.0.0
```

## 🔧 Configuration

### **Environment Variables**
```bash
# Required
AZURE_OPENAI_API_KEY=your-azure-openai-api-key
AZURE_OPENAI_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
APP_PASSWORD=your-secure-password

# Optional
RATE_LIMIT_ATTEMPTS=5
RATE_LIMIT_WINDOW=300
MAX_INPUT_LENGTH=10000
MAX_FILE_SIZE=52428800
```

## 🔒 Security Features

- ✅ **Input Sanitization**: Comprehensive HTML escaping and pattern removal
- ✅ **Rate Limiting**: Protection against brute force attacks
- ✅ **Authentication**: Secure password-based authentication
- ✅ **File Validation**: Secure file uploads with size and type checks
- ✅ **Prompt Safety**: LLM injection attack prevention
- ✅ **Security Logging**: Comprehensive security event logging

## 📊 Features

### **Core Functionality**
- **Speech Analysis**: AI-powered analysis of UN GA speeches
- **SDG Mapping**: Automatic SDG reference detection
- **Country Classification**: African Member State vs Development Partner
- **File Processing**: PDF, DOCX, and MP3 file support
- **Export Capabilities**: Multiple export formats
- **Chat Interface**: Interactive Q&A about analyses

### **Professional Features**
- **Enterprise Security**: Comprehensive security measures
- **Professional UI**: Clean, modern interface
- **Error Handling**: Graceful failure management
- **Logging**: Professional logging and monitoring
- **Configuration**: Environment-based configuration

## 🎯 Applications

### **Production Application** (`app.py`)
- **Full Functionality**: Complete analysis capabilities
- **All Features**: SDG mapping, chat interface, export
- **Production Ready**: Comprehensive security and error handling
- **Use Case**: Azure deployment, production use

### **Professional Demonstration** (`app_professional.py`)
- **Clean Architecture**: Professional code organization
- **Enterprise Security**: Advanced security features
- **Modern UI**: Professional user interface
- **Use Case**: Demonstration, professional showcase

## 🛠️ Development

### **Core Modules**
- `prompts.py` - LLM prompts and templates
- `corpus_integration.py` - Corpus data management
- `classify.py` - Country classification logic
- `ingest.py` - File processing and text extraction
- `llm.py` - LLM integration and analysis
- `storage.py` - Database operations
- `sdg_utils.py` - SDG processing utilities
- `export_utils.py` - Export functionality

### **Security Architecture**
- **Input Validation**: Comprehensive sanitization
- **Rate Limiting**: Time-based attempt limiting
- **Authentication**: Secure user authentication
- **File Security**: Validated file uploads
- **Prompt Safety**: LLM injection protection

## 📈 Performance

- **Optimized Code**: Clean, efficient implementation
- **Error Recovery**: Graceful failure handling
- **Security**: Production-ready security measures
- **Scalability**: Azure App Service ready
- **Monitoring**: Comprehensive logging

## 🔄 Deployment

### **Azure App Service**
1. **Configuration**: Set environment variables
2. **Startup Command**: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
3. **Dependencies**: Install from `requirements.txt`
4. **Security**: Configure authentication and rate limiting

### **Local Development**
1. **Environment**: Set up `.env` file
2. **Dependencies**: Install requirements
3. **Run**: `streamlit run app.py`
4. **Test**: Access at `http://localhost:8501`

## 📚 Documentation

- **README.md**: This file
- **SECURITY.md**: Security documentation
- **LICENSE**: MIT License
- **env.template**: Environment configuration template

## 👨‍💻 Development Team

**SMU Data Team** - Professional UN GA Analysis Platform

## 🏆 Professional Standards

This application demonstrates **enterprise-grade development** with:

- ✅ **Clean Architecture**: Professional code organization
- ✅ **Security First**: Comprehensive security measures
- ✅ **Error Handling**: Graceful failure management
- ✅ **Documentation**: Comprehensive documentation
- ✅ **Testing**: Production-ready deployment
- ✅ **Monitoring**: Professional logging and monitoring

---

**Ready for production deployment on Azure App Service!** 🚀
