# Enhanced Patent Search Agent

A powerful Python agent for searching patents on patents.google.com with automatic PDF download capabilities and an intuitive query interface.

## Features

🔍 **Multiple Search Types**
- Keyword search
- Patent number lookup
- Inventor search
- Assignee/company search
- Chemical compound search

📄 **PDF Download**
- Automatic PDF download for patents
- Batch download with progress tracking
- Local file management
- Size and storage monitoring

⚡ **Performance**
- Rate limiting to respect server resources
- Parallel downloads for efficiency
- Session management with connection pooling
- Error handling and retries

🎯 **User-Friendly Interface**
- Command-line interface
- Interactive mode
- JSON output for automation
- Progress indicators

## Quick Start

### 1. Installation

```bash
# Clone or navigate to the patent_search_system directory
cd patent_search_system

# Install dependencies
pip install -r requirements.txt

# Run setup
python setup_enhanced_agent.py
```

### 2. Configuration (Optional)

For enhanced search capabilities, get a free API key from [SearchAPI.io](https://www.searchapi.io/) and add it to your `.env` file:

```bash
# Edit .env file
SEARCHAPI_KEY=your_api_key_here
```

### 3. Usage Examples

#### Command Line Interface

```bash
# Search by keywords and download PDFs
python patent_cli.py search-keywords "FOXP2" "autism" --download-pdfs --max-results 10

# Look up specific patent
python patent_cli.py lookup-patent US10123456B2 --download-pdf

# Search by inventor
python patent_cli.py search-inventor "John Smith" --max-results 15

# Search by company
python patent_cli.py search-assignee "Google Inc" --max-results 20

# Search chemical compounds
python patent_cli.py search-chemical "caffeine" --max-results 10

# Check download status
python patent_cli.py status

# Clean up old files
python patent_cli.py cleanup --days 30

# Interactive mode
python patent_cli.py interactive
```

#### Python API

```python
from enhanced_patent_agent import EnhancedPatentAgent

# Create agent
agent = EnhancedPatentAgent()

# Search by keywords
results = agent.search_patents({
    'search_type': 'keywords',
    'keywords': ['FOXP2', 'autism'],
    'max_results': 20,
    'include_pdfs': True
})

print(f"Found {results['total_results']} patents")

# Look up specific patent
patent_result = agent.search_patents({
    'search_type': 'patent_number',
    'patent_number': 'US10123456B2',
    'include_pdf': True
})

# Check downloads
status = agent.get_download_status()
print(f"Downloaded {status['total_pdfs']} PDFs ({status['total_size_mb']} MB)")
```

## Directory Structure

```
patent_search_system/
├── enhanced_patent_agent.py    # Main agent implementation
├── patent_cli.py              # Command-line interface
├── setup_enhanced_agent.py    # Setup and verification script
├── requirements.txt           # Python dependencies
├── .env                      # Configuration file (created by setup)
├── patent_data/              # Downloaded files directory
│   └── downloaded_pdfs/      # PDF files stored here
├── logs/                     # Application logs
└── cache/                    # Temporary cache files
```

## Search Types

### 1. Keyword Search
Search patents containing specific keywords in title, abstract, or claims.

```bash
python patent_cli.py search-keywords "machine learning" "neural network" --max-results 25
```

### 2. Patent Number Lookup
Get detailed information about a specific patent by its number.

```bash
python patent_cli.py lookup-patent US10123456B2 --download-pdf
```

### 3. Inventor Search
Find all patents by a specific inventor.

```bash
python patent_cli.py search-inventor "Geoffrey Hinton" --max-results 30
```

### 4. Assignee Search
Search patents assigned to a specific company or organization.

```bash
python patent_cli.py search-assignee "Microsoft Corporation" --max-results 50
```

### 5. Chemical Search
Search for patents related to specific chemical compounds.

```bash
python patent_cli.py search-chemical "aspirin" --molecular-formula "C9H8O4"
```

## PDF Download Features

- **Automatic Download**: PDFs are automatically downloaded during search
- **Smart Naming**: Files are named using patent numbers
- **Duplicate Detection**: Existing files are not re-downloaded
- **Progress Tracking**: Real-time download progress
- **Size Monitoring**: Track storage usage
- **Cleanup Tools**: Remove old files to save space

## Configuration Options

The `.env` file supports the following options:

```bash
# API Keys
SEARCHAPI_KEY=your_searchapi_key_here
USPTO_API_KEY=your_uspto_key_here

# Download Settings
MAX_DOWNLOAD_SIZE_MB=100
DOWNLOAD_TIMEOUT_SECONDS=60

# Rate Limiting
MIN_REQUEST_INTERVAL=1.0
MAX_CONCURRENT_DOWNLOADS=3

# Storage
CLEANUP_AFTER_DAYS=30
MAX_STORAGE_GB=10
```

## Advanced Features

### Batch Processing
```python
# Process multiple search queries
queries = [
    {'search_type': 'keywords', 'keywords': ['AI', 'machine learning']},
    {'search_type': 'keywords', 'keywords': ['blockchain', 'cryptocurrency']},
    {'search_type': 'assignee', 'assignee_name': 'IBM'}
]

for query in queries:
    results = agent.search_patents(query)
    print(f"Query: {query} - Found: {results['total_results']} patents")
```

### Custom Output
```bash
# Save results to JSON file
python patent_cli.py search-keywords "quantum computing" --output results.json

# Use results in other applications
python -c "
import json
with open('results.json') as f:
    data = json.load(f)
    for patent in data['patents']:
        print(f'{patent['patent_number']}: {patent['title']}')
"
```

## Error Handling

The agent includes comprehensive error handling:

- **Network Issues**: Automatic retries with exponential backoff
- **Rate Limiting**: Respects server limits and API quotas
- **File Errors**: Handles disk space and permission issues
- **API Errors**: Graceful fallbacks and informative error messages

## Troubleshooting

### Common Issues

1. **"SearchAPI key not configured"**
   - Get a free key from SearchAPI.io
   - Add it to your .env file
   - The agent will work with web scraping fallback

2. **"PDF download failed"**
   - Some patents may not have PDFs available
   - Check internet connection
   - Verify patent number format

3. **"No results found"**
   - Try different keywords
   - Check spelling
   - Use broader search terms

### Getting Help

```bash
# Check system status
python setup_enhanced_agent.py

# View help
python patent_cli.py --help
python patent_cli.py search-keywords --help

# Check download status
python patent_cli.py status
```

## Performance Tips

1. **Use API Key**: SearchAPI provides faster and more reliable results
2. **Limit Results**: Start with smaller result sets (10-20 patents)
3. **Batch Downloads**: Download PDFs in smaller batches
4. **Regular Cleanup**: Use cleanup command to manage storage

## License

This enhanced patent search agent is provided as-is for research and educational purposes. Please respect patent database terms of service and rate limits.

## Contributing

Feel free to submit issues, feature requests, or improvements to the patent search agent.