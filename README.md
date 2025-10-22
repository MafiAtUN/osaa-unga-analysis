# UN GA Daily Readouts

A production-ready Streamlit application for analyzing UN General Assembly speeches using AI.

## Features

- **Speech Analysis**: Upload PDF, DOCX, or MP3 files for AI-powered analysis
- **Multi-language Support**: Automatic translation to English using UN terminology
- **Country Classification**: Auto-classifies African Member States vs Development Partners
- **Cross-Year Analysis**: Compare speeches across multiple years (1946-2025)
- **Interactive Visualizations**: Charts, heatmaps, and data exploration tools
- **Export Options**: Download analyses as DOCX or Markdown files
- **Security**: Input sanitization, rate limiting, and prompt safety

## Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables**:
   ```bash
   cp src/unga_analysis/config/env.template .env
   # Edit .env with your API keys
   ```

3. **Run the application**:
   ```bash
   streamlit run app_refactored.py
   ```

4. **Access the app**: Open http://localhost:8501 in your browser

## Usage

### New Analysis
1. Upload a speech file or paste text
2. Select the country/entity
3. Click "Analyze Speech" to get AI-powered insights

### Cross-Year Analysis
1. Go to the "Cross-Year Analysis" tab
2. Select countries or groups
3. Choose analysis questions
4. Run comparative analysis across years

### Data Explorer
1. Use the "Data Explorer" tab
2. Visualize speech data availability
3. Filter by country, year, or region

## Architecture

The application is built with a modular architecture:

```
src/unga_analysis/
├── config/           # Configuration files
│   ├── questions.py  # Analysis questions and prompts
│   └── countries.py  # Country data and detection
├── core/             # Core analysis logic
├── data/             # Data processing and storage
├── ui/               # User interface components
│   ├── auth.py       # Authentication
│   ├── components/   # Reusable UI components
│   └── tabs/         # Tab-specific functionality
└── utils/            # Utility functions
```

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

## Development

The application has been refactored for better maintainability:

- **Modular structure**: Code organized into logical modules
- **Clean separation**: UI, business logic, and data layers separated
- **Reusable components**: UI components can be imported independently
- **Easy testing**: Each module can be tested separately

## License

Built for UN OSAA | Developed by SMU Data Team