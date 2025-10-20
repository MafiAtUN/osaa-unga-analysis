# API Reference

## Core Module (`src.unga_analysis.core`)

### LLM Operations
- `run_analysis()`: Main analysis function
- `get_available_models()`: List available OpenAI models
- `chunk_and_synthesize()`: Process large texts

### Prompts
- `SYSTEM_MESSAGE`: Default system prompt
- `build_user_prompt()`: Create user prompts
- `get_question_set()`: Get analysis questions

### Classification
- `infer_classification()`: Classify speeches
- `get_au_members()`: Get AU member countries

## Data Module (`src.unga_analysis.data`)

### Data Ingestion
- `data_ingestion_manager`: Main ingestion controller
- `extract_text_from_file()`: Extract text from documents
- `validate_text_length()`: Validate text length

### Storage
- `simple_vector_storage`: Vector database manager
- `cross_year_manager`: Cross-year analysis manager

## Utils Module (`src.unga_analysis.utils`)

### Visualization
- `create_region_distribution_chart()`: Regional analysis charts
- `create_word_count_heatmap()`: Word frequency heatmaps
- `UNGAVisualizationManager`: Main visualization controller

### Export
- `create_export_files()`: Export analysis results
- `format_filename()`: Format output filenames

### SDG Utilities
- `extract_sdgs()`: Extract SDG mentions
- `detect_africa_mention()`: Detect Africa references
- `format_sdgs()`: Format SDG data
