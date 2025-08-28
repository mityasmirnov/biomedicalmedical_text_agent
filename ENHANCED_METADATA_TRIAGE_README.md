# Enhanced Metadata Triage Module

## Overview

The Enhanced Metadata Triage Module provides comprehensive functionality for searching PubMed, retrieving article metadata, and storing results in a database. This module extends the existing metadata triage functionality with enhanced features including database integration, caching, and comprehensive metadata extraction.

## Features

### 🔍 **Enhanced PubMed Client (`pubmed_client2.py`)**
- **Comprehensive Metadata Extraction**: Retrieves paper title, abstract, journal, PMID, authors, year, and additional metadata
- **Enhanced Article Objects**: Includes publication year/month/day, language, country, grant info, chemical substances, and more
- **Caching Support**: Built-in database caching for improved performance and reduced API calls
- **Rate Limiting**: Respects NCBI API rate limits with configurable request throttling
- **Batch Processing**: Efficient batch processing of large result sets
- **Error Handling**: Robust error handling and retry mechanisms

### 🗄️ **Enhanced Metadata Orchestrator (`enhanced_metadata_orchestrator.py`)**
- **Database Integration**: Direct integration with SQLite database for persistent storage
- **Complete Pipeline**: Orchestrates the entire metadata triage workflow
- **Search Tracking**: Tracks search queries and results for analysis
- **Statistics Generation**: Comprehensive statistics about stored articles and searches
- **Flexible Output**: Supports both database storage and CSV/JSON export

### 📊 **Database Schema**
- **`pubmed_articles`**: Comprehensive article metadata storage
- **`search_queries`**: Search query tracking and analytics
- **Indexed Fields**: Optimized queries on PMID, search query, journal, and publication date
- **Metadata Fields**: Support for classification results, concept scores, and deduplication status

## Installation and Setup

### Prerequisites
- Python 3.7+
- Built-in modules: `sqlite3`, `json`, `pathlib`, `datetime`, `uuid`, `hashlib`
- Optional: `pandas`, `requests` (for full functionality)

### Directory Structure
```
src/metadata_triage/
├── enhanced_metadata_orchestrator.py    # Enhanced orchestrator with DB integration
├── pubmed_client2.py                    # Enhanced PubMed client
├── enhanced_metadata_orchestrator_simple.py  # Simplified version (no external deps)
├── pubmed_client.py                     # Original PubMed client
├── metadata_orchestrator.py             # Original orchestrator
└── __init__.py                          # Module exports
```

## Usage Examples

### 1. Basic PubMed Search and Storage

```python
from metadata_triage.enhanced_metadata_orchestrator import EnhancedMetadataOrchestrator

# Initialize orchestrator
orchestrator = EnhancedMetadataOrchestrator(
    db_path="data/database/biomedical_data.db"
)

# Search and store metadata
result = orchestrator.search_and_store_pubmed_metadata(
    query="leigh syndrome case reports",
    max_results=100,
    save_to_csv=True,
    output_dir="data/metadata_triage"
)

print(f"Found {result['articles_found']} articles")
print(f"Stored {result['articles_stored']} articles")
```

### 2. Enhanced PubMed Client Usage

```python
from metadata_triage.pubmed_client2 import create_enhanced_pubmed_client

# Create enhanced client
client = create_enhanced_pubmed_client(
    email="your.email@example.com",  # Optional: for higher rate limits
    api_key="your_api_key",          # Optional: for higher rate limits
    db_path="data/database/biomedical_data.db",  # For caching
    enable_caching=True
)

# Search for articles
articles = client.fetch_articles_by_query(
    query="leigh syndrome case reports",
    max_results=100,
    include_abstracts=True,
    use_cache=True
)

# Save to CSV
client.save_to_csv(articles, "leigh_syndrome_articles.csv")

# Get statistics
stats = client.get_statistics(articles)
print(f"Open access rate: {stats.get('open_access_rate', 0):.1%}")
```

### 3. Complete Pipeline Execution

```python
# Run complete metadata triage pipeline
result = orchestrator.run_complete_pipeline(
    query="leigh syndrome case reports",
    max_results=1000,
    include_europepmc=True,
    output_dir="data/metadata_triage/complete_pipeline",
    save_intermediate=True
)

if result['success']:
    print(f"Pipeline completed: {result['total_articles']} articles processed")
```

### 4. Database Query and Analysis

```python
# Retrieve stored articles
articles = orchestrator.get_stored_articles(
    query="leigh syndrome",  # Optional filter
    limit=50,
    offset=0
)

# Get specific article by PMID
article = orchestrator.get_article_by_pmid("12345678")

# Get comprehensive statistics
stats = orchestrator.get_search_statistics()
print(f"Total articles: {stats['total_articles']}")
print(f"Top journals: {stats['top_journals']}")
print(f"Recent searches: {stats['recent_searches']}")
```

## Command Line Usage

### Enhanced Metadata Orchestrator

```bash
# Basic search and storage
python -m metadata_triage.enhanced_metadata_orchestrator "leigh syndrome case reports"

# With custom parameters
python -m metadata_triage.enhanced_metadata_orchestrator \
    "leigh syndrome case reports" \
    --max-results 500 \
    --db-path data/database/custom.db \
    --output-dir data/custom_output
```

### Simplified Version (No External Dependencies)

```bash
# Test the simplified version
python test_standalone_metadata_triage.py

# Run simplified orchestrator
python src/metadata_triage/enhanced_metadata_orchestrator_simple.py "leigh syndrome case reports"
```

## Database Schema Details

### `pubmed_articles` Table
```sql
CREATE TABLE pubmed_articles (
    id TEXT PRIMARY KEY,                    -- Unique article ID
    pmid TEXT UNIQUE NOT NULL,              -- PubMed ID
    title TEXT,                             -- Article title
    sort_title TEXT,                        -- Sortable title
    last_author TEXT,                       -- Last author name
    journal TEXT,                           -- Journal name
    authors TEXT,                           -- All authors
    pub_type TEXT,                          -- Publication type
    pmc_link TEXT,                          -- PMC link
    doi TEXT,                               -- DOI
    abstract TEXT,                          -- Article abstract
    pub_date TEXT,                          -- Publication date
    mesh_terms TEXT,                        -- MeSH terms
    keywords TEXT,                          -- Keywords
    search_query TEXT,                      -- Search query used
    source TEXT DEFAULT 'PubMed',           -- Data source
    fetch_date TIMESTAMP,                   -- When metadata was fetched
    classification_result TEXT,             -- Classification results (JSON)
    concept_scores TEXT,                    -- Concept scoring results (JSON)
    deduplication_status TEXT,              -- Deduplication status
    created_at TIMESTAMP,                   -- Record creation time
    updated_at TIMESTAMP                    -- Record update time
);
```

### `search_queries` Table
```sql
CREATE TABLE search_queries (
    id TEXT PRIMARY KEY,                    -- Unique query ID
    query_text TEXT NOT NULL,               -- Search query text
    max_results INTEGER,                    -- Maximum results requested
    total_found INTEGER,                    -- Total articles found
    articles_fetched INTEGER,               -- Articles actually fetched
    search_date TIMESTAMP,                  -- When search was performed
    status TEXT DEFAULT 'completed',        -- Search status
    metadata TEXT                           -- Additional metadata (JSON)
);
```

## Metadata Fields

### Core PubMed Fields
- **PMID**: PubMed identifier
- **Title**: Article title
- **Abstract**: Article abstract
- **Journal**: Journal name
- **Authors**: Author list
- **Publication Date**: Publication date
- **MeSH Terms**: Medical Subject Headings
- **Keywords**: Article keywords

### Enhanced Fields
- **Publication Year/Month/Day**: Parsed publication date
- **Language**: Article language
- **Country**: Publication country
- **Grant Info**: Funding information
- **Chemical Substances**: Chemical compounds mentioned
- **Open Access**: Whether article is open access
- **Full Text Available**: Whether full text is available
- **PMC Link**: PubMed Central link
- **DOI**: Digital Object Identifier

## Configuration

### Environment Variables
```bash
# Optional: For higher PubMed API rate limits
export PUBMED_EMAIL="your.email@example.com"
export PUBMED_API_KEY="your_api_key"

# Optional: For Europe PMC integration
export EUROPEPMC_EMAIL="your.email@example.com"
```

### Database Configuration
```python
# Custom database path
orchestrator = EnhancedMetadataOrchestrator(
    db_path="path/to/custom/database.db"
)

# Custom output directories
result = orchestrator.search_and_store_pubmed_metadata(
    query="query",
    output_dir="custom/output/path"
)
```

## Testing

### Run Test Suite
```bash
# Test the enhanced module (requires pandas/requests)
python test_enhanced_metadata_triage.py

# Test the simplified module (no external dependencies)
python test_standalone_metadata_triage.py

# Test the demonstration
python demo_enhanced_metadata_triage.py
```

### Test Coverage
The test suite covers:
- ✅ Database initialization and schema creation
- ✅ Sample article storage and retrieval
- ✅ Search query tracking
- ✅ Statistics generation
- ✅ Complete pipeline execution
- ✅ Leigh syndrome case report searches
- ✅ Error handling and edge cases

## Performance and Optimization

### Caching Strategy
- **Query-level caching**: Caches search results for 24 hours
- **Database storage**: Persistent storage of all retrieved metadata
- **Batch processing**: Efficient handling of large result sets

### Rate Limiting
- **PubMed API**: 10 requests/second with API key, 3 without
- **Automatic throttling**: Built-in rate limiting to respect API limits
- **Configurable delays**: Adjustable delays between requests

### Database Optimization
- **Indexed fields**: Fast queries on commonly searched fields
- **Efficient queries**: Optimized SQL queries for large datasets
- **Connection pooling**: Reuses database connections

## Troubleshooting

### Common Issues

1. **Module Import Errors**
   ```bash
   # Ensure src directory is in Python path
   export PYTHONPATH="${PYTHONPATH}:/path/to/workspace/src"
   ```

2. **Database Permission Errors**
   ```bash
   # Check directory permissions
   ls -la data/database/
   # Ensure write permissions
   chmod 755 data/database/
   ```

3. **API Rate Limiting**
   ```python
   # Use email and API key for higher limits
   client = create_enhanced_pubmed_client(
       email="your.email@example.com",
       api_key="your_api_key"
   )
   ```

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable debug logging for troubleshooting
orchestrator = EnhancedMetadataOrchestrator()
```

## Integration with Existing Systems

### Backward Compatibility
- All existing `metadata_triage` functionality is preserved
- Enhanced modules can be used alongside original modules
- Gradual migration path available

### API Integration
```python
# Use with existing API endpoints
from metadata_triage.enhanced_metadata_orchestrator import EnhancedMetadataOrchestrator

# Initialize and use in existing code
orchestrator = EnhancedMetadataOrchestrator()
# ... existing code continues to work
```

### Database Integration
- Integrates with existing `src/database` structure
- Compatible with existing database schemas
- Can extend existing tables with new fields

## Future Enhancements

### Planned Features
- **Europe PMC Integration**: Full integration with Europe PMC API
- **Abstract Classification**: LLM-based abstract classification
- **Concept Scoring**: HPO and UMLS concept scoring
- **Deduplication**: Advanced article deduplication algorithms
- **Full-text Download**: PMC full-text article download
- **Citation Analysis**: Citation network analysis
- **Journal Impact Factors**: Integration with journal metrics

### Extensibility
- **Plugin Architecture**: Modular design for easy extension
- **Custom Metadata**: Support for custom metadata fields
- **API Extensions**: Easy addition of new data sources
- **Export Formats**: Support for additional export formats

## Contributing

### Development Setup
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run tests: `python test_enhanced_metadata_triage.py`
4. Make changes and test thoroughly
5. Submit pull request with detailed description

### Code Style
- Follow PEP 8 guidelines
- Include comprehensive docstrings
- Add type hints for all functions
- Write tests for new functionality

## License

This module is part of the Biomedical Text Agent project and follows the same licensing terms.

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review existing GitHub issues
3. Create a new issue with detailed error information
4. Include system information and error logs

---

**Note**: This enhanced module provides a robust foundation for PubMed metadata retrieval and analysis. It maintains backward compatibility while adding significant new functionality for database integration, caching, and enhanced metadata extraction.
