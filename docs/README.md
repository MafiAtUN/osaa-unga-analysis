# UNGA Analysis Documentation

## Overview

The UNGA Analysis framework is a professional-grade application for analyzing United Nations General Assembly speeches using advanced natural language processing and machine learning techniques.

## Architecture

### Package Structure

```
src/unga_analysis/
├── core/           # Core functionality (LLM, prompts, classification)
├── data/           # Data management and processing
├── utils/          # Utility functions and helpers
├── ui/             # User interface components
└── config/         # Configuration management
```

### Core Components

- **LLM Operations**: OpenAI integration for speech analysis
- **Data Processing**: Vector storage and retrieval using DuckDB
- **Visualization**: Interactive charts and analytics
- **Export**: Multiple format support for results

## Installation

```bash
pip install -e .
```

## Usage

```bash
streamlit run app.py
```

## Development

```bash
pip install -e ".[dev]"
pre-commit install
pytest
```

## API Reference

See individual module documentation for detailed API references.
