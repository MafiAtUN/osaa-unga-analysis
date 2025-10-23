# UNGA Analysis App - API Documentation

## Overview

The UNGA Analysis App provides a comprehensive API for analyzing United Nations General Assembly speeches. This document outlines the available endpoints, data structures, and usage examples.

## Core Modules

### Authentication API

#### User Authentication
```python
from src.unga_analysis.core.user_auth import UserAuthManager

# Initialize authentication manager
auth_manager = UserAuthManager()

# Register new user
user = auth_manager.register_user(
    email="user@example.com",
    password="secure_password",
    full_name="John Doe",
    title="Analyst",
    office="UN Office",
    purpose="Research"
)

# Authenticate user
authenticated = auth_manager.authenticate_user("user@example.com", "password")

# Get current user
current_user = auth_manager.get_current_user()
```

### Database API

#### Speech Database Operations
```python
from src.unga_analysis.data.simple_vector_storage import simple_vector_storage as db_manager

# Search speeches
speeches = db_manager.search_speeches(
    query_text="climate change",
    countries=["United States", "China"],
    years=[2020, 2021, 2022],
    limit=50
)

# Semantic search
semantic_results = db_manager.semantic_search(
    query_text="sustainable development",
    similarity_threshold=0.7,
    limit=20
)

# Get speech by ID
speech = db_manager.get_speech_by_id(speech_id)

# Add new speech
new_speech = db_manager.add_speech(
    country_name="France",
    year=2023,
    session=78,
    speech_text="Speech content...",
    word_count=500
)
```

### Country Management API

#### Country Operations
```python
from src.unga_analysis.utils.country_manager import country_manager

# Get all countries
all_countries = country_manager.get_all_countries()

# Get African countries
african_countries = country_manager.get_african_countries()

# Get development partners
dev_partners = country_manager.get_development_partners()

# Search countries
search_results = country_manager.search_countries("United")

# Get country statistics
stats = country_manager.get_country_stats()
```

### Analysis API

#### Cross-Year Analysis
```python
from src.unga_analysis.data.cross_year_analysis import CrossYearAnalysisManager

# Initialize analysis manager
analysis_manager = CrossYearAnalysisManager()

# Analyze cross-year trends
trends = analysis_manager.analyze_cross_year_trends(
    query="climate change",
    countries=["United States", "China"],
    years=[2015, 2020, 2025]
)

# Search speeches by criteria
speeches = analysis_manager.search_speeches_by_criteria(
    query_text="sustainable development",
    countries=["Germany", "France"],
    years=[2020, 2021, 2022]
)
```

#### Enhanced Search Engine
```python
from src.unga_analysis.core.enhanced_search_engine import get_enhanced_search_engine

# Get search engine instance
search_engine = get_enhanced_search_engine()

# Perform enhanced search
results = search_engine.search(
    query="What are the main themes in African countries' speeches?",
    search_type="comprehensive"
)

# Get search suggestions
suggestions = search_engine.get_search_suggestions("climate")
```

### Visualization API

#### Chart Generation
```python
from src.unga_analysis.utils.visualization import UNGAVisualizationManager

# Initialize visualization manager
viz_manager = UNGAVisualizationManager(db_manager)

# Generate country comparison chart
chart = viz_manager.create_country_comparison_chart(
    countries=["United States", "China", "Russia"],
    years=[2020, 2021, 2022]
)

# Generate trend analysis
trend_chart = viz_manager.create_trend_analysis(
    query="climate change",
    years=list(range(2015, 2025))
)
```

## Data Structures

### Speech Object
```python
{
    "id": int,
    "country_name": str,
    "country_code": str,
    "year": int,
    "session": int,
    "speech_text": str,
    "word_count": int,
    "embedding": List[float],
    "metadata": dict,
    "is_african_member": bool,
    "source_filename": str,
    "created_at": datetime
}
```

### User Object
```python
{
    "id": str,
    "email": str,
    "full_name": str,
    "title": str,
    "office": str,
    "purpose": str,
    "status": str,  # "pending", "approved", "denied"
    "created_at": datetime,
    "approved_at": datetime,
    "approved_by": str,
    "last_login": datetime,
    "login_count": int
}
```

### Analysis Result
```python
{
    "query": str,
    "countries": List[str],
    "years": List[int],
    "results": List[Speech],
    "summary": str,
    "key_themes": List[str],
    "sentiment": str,
    "confidence": float,
    "created_at": datetime
}
```

## Error Handling

### Common Exceptions
```python
# Database errors
try:
    speeches = db_manager.search_speeches(query="test")
except DatabaseError as e:
    print(f"Database error: {e}")

# Authentication errors
try:
    user = auth_manager.authenticate_user("email", "password")
except AuthenticationError as e:
    print(f"Authentication failed: {e}")

# Search errors
try:
    results = search_engine.search("query")
except SearchError as e:
    print(f"Search failed: {e}")
```

## Performance Considerations

### Caching
- Country lists are cached for performance
- Search results are cached for repeated queries
- Database connections are pooled

### Optimization
- Use appropriate limits for search queries
- Index frequently searched fields
- Batch database operations when possible

### Memory Management
- Large datasets are processed in chunks
- Embeddings are loaded on demand
- Session state is managed efficiently

## Security

### Authentication
- Passwords are hashed using bcrypt
- Sessions are managed securely
- Admin access is restricted

### Data Protection
- Input validation on all endpoints
- SQL injection prevention
- XSS protection in UI components

## Examples

### Complete Analysis Workflow
```python
# 1. Authenticate user
auth_manager = UserAuthManager()
user = auth_manager.authenticate_user("user@example.com", "password")

# 2. Search for speeches
speeches = db_manager.search_speeches(
    query_text="climate change",
    countries=["United States", "China"],
    years=[2020, 2021, 2022]
)

# 3. Perform cross-year analysis
analysis_manager = CrossYearAnalysisManager()
trends = analysis_manager.analyze_cross_year_trends(
    query="climate change",
    countries=["United States", "China"],
    years=[2020, 2021, 2022]
)

# 4. Generate visualization
viz_manager = UNGAVisualizationManager(db_manager)
chart = viz_manager.create_trend_analysis(
    query="climate change",
    years=[2020, 2021, 2022]
)
```

### Batch Processing
```python
# Process multiple countries
countries = ["United States", "China", "Russia", "Germany"]
results = {}

for country in countries:
    speeches = db_manager.search_speeches(
        countries=[country],
        years=[2023]
    )
    results[country] = len(speeches)

print(f"Results: {results}")
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **Database Connection**: Check database file permissions
3. **Memory Issues**: Reduce batch sizes for large datasets
4. **Performance**: Use appropriate search limits

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable debug logging
from src.unga_analysis.config.logging import setup_logging
setup_logging()
```

## Support

For technical support and questions:
- **Email**: islam50@un.org
- **Documentation**: See `docs/` directory
- **Issues**: Create an issue in the repository