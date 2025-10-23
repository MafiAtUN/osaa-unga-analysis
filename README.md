# UNGA Analysis App

**Production-ready analysis platform for UN General Assembly speeches**

[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## 🎯 Overview

The UNGA Analysis App is a comprehensive platform for analyzing United Nations General Assembly speeches from 1946 to 2025. It provides advanced AI-powered analysis, cross-year trend analysis, document context analysis, and interactive visualizations for UN member states and development partners.

## ✨ Features

### 🔐 **Authentication & User Management**
- Secure user registration and authentication
- Admin portal for user management
- Role-based access control
- Session management

### 📊 **Core Analysis Features**
- **New Analysis**: AI-powered speech analysis with multiple models
- **Cross-Year Analysis**: Historical trend analysis across 80 years
- **Document Context**: Upload and analyze documents with context
- **Database Chat**: Direct interaction with UNGA database
- **Visualizations**: Interactive charts and graphs
- **Data Explorer**: Comprehensive data exploration tools

### 🌍 **Data Coverage**
- **11,093 speeches** from 1946-2025
- **199 countries** represented
- **80 years** of historical data
- **Complete embeddings** for semantic search
- **African vs Development Partner** classification

### 🤖 **AI Capabilities**
- Multiple AI model support (GPT-4, Claude, etc.)
- Semantic search with embeddings
- Document classification
- Sentiment analysis
- Topic extraction
- Cross-reference analysis

## 🏗️ Architecture

```
unga_analysis/
├── src/unga_analysis/          # Main application package
│   ├── core/                   # Core business logic
│   │   ├── auth.py            # Authentication
│   │   ├── classify.py        # Document classification
│   │   ├── enhanced_search_engine.py  # Advanced search
│   │   ├── llm.py             # LLM integration
│   │   ├── openai_client.py   # OpenAI client
│   │   ├── prompts.py         # AI prompts
│   │   ├── startup.py         # Application startup
│   │   └── user_auth.py       # User authentication
│   ├── data/                   # Data management
│   │   ├── cross_year_analysis.py  # Cross-year analysis
│   │   ├── data_ingestion.py  # Data ingestion
│   │   ├── ingest.py          # Data processing
│   │   └── simple_vector_storage.py  # Vector database
│   ├── ui/                     # User interface
│   │   ├── auth_interface.py   # Authentication UI
│   │   ├── components/         # UI components
│   │   ├── tabs/              # Tab implementations
│   │   ├── ui_components.py   # UI utilities
│   │   └── unified_search_interface.py  # Search interface
│   ├── utils/                  # Utilities
│   │   ├── country_manager.py  # Country management
│   │   ├── export_utils.py     # Export functionality
│   │   ├── logging_config.py  # Logging configuration
│   │   ├── security.py        # Security utilities
│   │   ├── utils.py           # General utilities
│   │   └── visualization.py   # Visualization utilities
│   └── config/                 # Configuration
│       ├── countries.py        # Country definitions
│       └── questions.py        # Analysis questions
├── tests/                      # Test suite
├── docs/                       # Documentation
├── scripts/                    # Deployment scripts
├── artifacts/                  # Data artifacts
├── requirements.txt           # Dependencies
├── main.py                    # Application entry point
└── README.md                  # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd unga-analysis-app
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv unga80
   source unga80/bin/activate  # On Windows: unga80\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env.template .env
   # Edit .env with your configuration
   ```

5. **Initialize database**
   ```bash
   python setup_database.py
   ```

6. **Run the application**
   ```bash
   python main.py
   # Or: streamlit run main.py
   ```

### Default Admin Access

- **Email**: `islam50@un.org`
- **Password**: `OSAAKing!`

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Admin Configuration
ADMIN_EMAIL=islam50@un.org
ADMIN_PASSWORD=OSAAKing!

# Database Configuration
DATABASE_URL=sqlite:///unga_vector.db
USER_DATABASE_URL=sqlite:///user_auth.db

# Application Configuration
APP_NAME=UNGA Analysis App
APP_VERSION=1.0.0
DEBUG=False
```

### Database Setup

The application uses two databases:

1. **`unga_vector.db`**: Main speech database with embeddings
2. **`user_auth.db`**: User authentication database

## 📊 Data Management

### Database Population

The application comes with a complete UNGA corpus (1946-2025):

- **Total Speeches**: 11,093
- **Countries**: 199
- **Years**: 1946-2025 (80 years)
- **Embeddings**: 100% coverage for semantic search

### Data Quality

- ✅ No duplicates
- ✅ Complete country mapping
- ✅ Proper African vs Development Partner classification
- ✅ Full temporal coverage
- ✅ Semantic search capabilities

## 🎨 User Interface

### Main Tabs

1. **📝 New Analysis**: Create new speech analyses
2. **🌍 Cross-Year Analysis**: Historical trend analysis
3. **📄 Document Context**: Upload and analyze documents
4. **📚 All Analyses**: View past analyses
5. **📊 Visualizations**: Interactive charts and graphs
6. **🗺️ Data Explorer**: Explore the database
7. **🗄️ Database Chat**: Chat with the database
8. **🔍 Error Insights**: System monitoring
9. **🛡️ Admin Portal**: User management (admin only)

### Features by User Type

- **Regular Users**: All analysis and visualization features
- **Admin Users**: Additional user management capabilities

## 🔒 Security

- Secure password hashing
- Session management
- Input validation
- SQL injection prevention
- XSS protection
- CSRF protection

## 🧪 Testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=src tests/
```

## 📈 Performance

- **Database**: Optimized with proper indexing
- **Search**: Semantic search with embeddings
- **Caching**: Efficient country and data caching
- **Memory**: Optimized for large datasets

## 🚀 Deployment

### Local Development

```bash
streamlit run main.py --server.port 8501
```

### Production Deployment

See `docs/DEPLOYMENT.md` for detailed deployment instructions.

## 📚 Documentation

- [API Documentation](docs/API.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Logging Configuration](docs/LOGGING.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏢 Organization

**Built for UN OSAA (Office of the Special Adviser on Africa)**

- **Supports**: PDF, DOCX, MP3 file formats
- **Auto-classifies**: African Member States vs Development Partners
- **Developed by**: SMU Data Team

## 🆘 Support

For support and questions:

- **Email**: islam50@un.org
- **Documentation**: See `docs/` directory
- **Issues**: Create an issue in the repository

---

**🇺🇳 UNGA Analysis App - Empowering UN Member States with Data-Driven Insights**