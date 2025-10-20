# UNGA Analysis Framework

A professional-grade framework for analyzing United Nations General Assembly speeches using advanced natural language processing and machine learning techniques.

## 🚀 Features

- **Advanced Speech Analysis**: Comprehensive analysis using OpenAI's GPT models
- **Semantic Search**: Vector-based search through speech content
- **Interactive Visualizations**: Dynamic charts and analytics
- **Multi-format Export**: PDF, Excel, JSON export capabilities
- **Cross-Year Analysis**: Compare speeches across different years
- **SDG Integration**: Sustainable Development Goals analysis
- **Multi-language Support**: Translation and language detection
- **Professional Architecture**: Modular, scalable, and maintainable codebase

## 📦 Installation

### Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd osaa-unga-80

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package
pip install -e .

# Configure environment
cp src/unga_analysis/config/env.template .env
# Edit .env with your API credentials

# Run the application
streamlit run app.py
```

### Development Installation

```bash
# Install with development dependencies
pip install -e ".[dev]"

# Set up pre-commit hooks
pre-commit install

# Run tests
pytest
```

## 🏗️ Architecture

### Package Structure

```
src/unga_analysis/
├── core/           # Core functionality
│   ├── llm.py      # LLM operations
│   ├── prompts.py  # Prompt templates
│   ├── classify.py # Classification logic
│   ├── auth.py     # Authentication
│   └── startup.py  # Application startup
├── data/           # Data management
│   ├── data_ingestion.py      # Data ingestion
│   ├── ingest.py              # File processing
│   ├── simple_vector_storage.py  # Vector database
│   └── cross_year_analysis.py    # Cross-year analysis
├── utils/          # Utilities
│   ├── visualization.py       # Charts and graphs
│   ├── export_utils.py        # Export functionality
│   ├── sdg_utils.py          # SDG analysis
│   ├── data_limitation_handler.py  # Data handling
│   └── utils.py              # General utilities
├── ui/             # User interface
│   ├── ui_components.py    # UI components
│   └── tabs/                 # Tab modules
└── config/         # Configuration
    └── env.template         # Environment template
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with the following variables:

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_API_BASE=https://your-resource.openai.azure.com/
OPENAI_API_VERSION=2024-02-15-preview
OPENAI_DEPLOYMENT_NAME=your_deployment_name

# Optional: Custom settings
MAX_TOKENS=4000
TEMPERATURE=0.7
```

## 🚀 Usage

### Main Application

```bash
streamlit run app.py
```

### Programmatic Usage

```python
from src.unga_analysis.core.llm import run_analysis
from src.unga_analysis.data.simple_vector_storage import simple_vector_storage

# Initialize database
db = simple_vector_storage

# Run analysis
results = run_analysis(text, model="gpt-4")
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/unga_analysis

# Run specific test file
pytest tests/test_core.py
```

## 📊 Development

### Code Quality

```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy src/

# Run all quality checks
pre-commit run --all-files
```

### Project Management

```bash
# Install development dependencies
pip install -e ".[dev]"

# Set up pre-commit hooks
pre-commit install

# Build package
python -m build
```

## 🚀 Deployment

### Azure App Service

1. **Prepare for deployment**
   ```bash
   chmod +x scripts/azure-deploy.sh
   ./scripts/azure-deploy.sh
   ```

2. **Configure Azure App Service**
   - Set environment variables in Azure Portal
   - Configure startup command: `streamlit run app.py --server.port 8000`
   - Set Python version to 3.9+

### Docker Deployment

```bash
# Build Docker image
docker build -t unga-analysis .

# Run container
docker run -p 8501:8501 unga-analysis
```

## 📚 Documentation

- [API Reference](docs/API.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Architecture Overview](docs/README.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add type hints to all functions
- Write comprehensive tests
- Update documentation for new features
- Use meaningful commit messages

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Contact the SMU Data Team
- Check the documentation in the `docs/` directory

## 🙏 Acknowledgments

- UN General Assembly for providing the speech data
- OpenAI for the GPT models
- Streamlit for the web framework
- The open-source community for various libraries and tools

## 📈 Roadmap

- [ ] Enhanced visualization capabilities
- [ ] Real-time collaboration features
- [ ] Advanced analytics dashboard
- [ ] API endpoints for external integration
- [ ] Mobile application support
