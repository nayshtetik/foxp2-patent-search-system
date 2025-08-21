# 🔬 Real Patent Search System - Production Setup Guide

This guide will help you set up the **REAL** patent search system with actual API integrations, not simulated data.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements_real.txt

# Install RDKit (chemical processing)
conda install -c conda-forge rdkit

# Alternative: Install RDKit via pip (may require additional setup)
pip install rdkit
```

### 2. Get API Keys

You'll need these API keys for full functionality:

#### **Required (Core Functionality)**
```bash
export OPENAI_API_KEY="sk-your-openai-key-here"
```

#### **Optional (Enhanced Search)**
```bash
# SearchAPI.io (Google Patents access)
export SEARCHAPI_KEY="your-searchapi-key"

# USPTO API (free registration)
export USPTO_API_KEY="your-uspto-key"

# ChemSpider (free registration)
export CHEMSPIDER_API_KEY="your-chemspider-key"
```

### 3. Test the System

```bash
python real_examples.py
```

---

## 📋 Detailed Setup Instructions

### API Key Setup Guide

#### 🔑 **OpenAI API (Required)**
1. Go to: https://platform.openai.com/api-keys
2. Create new secret key
3. Copy the key: `sk-...`
4. Export: `export OPENAI_API_KEY="sk-your-key"`

#### 🔍 **SearchAPI.io (Google Patents)**
1. Go to: https://www.searchapi.io/
2. Sign up for free account (1000 searches/month free)
3. Get API key from dashboard
4. Export: `export SEARCHAPI_KEY="your-key"`

#### 🏛️ **USPTO API (Free)**
1. Go to: https://developer.uspto.gov/api-catalog
2. Register for free account
3. Get API key for Patent Trial and Appeal Board API
4. Export: `export USPTO_API_KEY="your-key"`

#### 🧪 **ChemSpider API (Free)**
1. Go to: http://www.chemspider.com/AboutServices.aspx
2. Register for free account
3. Request API key
4. Export: `export CHEMSPIDER_API_KEY="your-key"`

---

## 🔬 Real Databases Accessed

### Patent Databases
- **Google Patents** (via SearchAPI.io)
- **USPTO PTAB** (Patent Trial and Appeal Board)
- **Espacenet** (European Patent Office)
- **WIPO PATENTSCOPE** (World Intellectual Property Organization)

### Chemical Databases
- **PubChem** (Free NIH database)
- **ChemSpider** (Royal Society of Chemistry)
- **SureChEMBL** (Chemical patents database)
- **Chemical Identifier Resolver** (NCI/NIH)
- **OPSIN** (Chemical name to structure)

### AI/ML Services
- **OpenAI GPT-4** (Patent analysis and insights)
- **RDKit** (Chemical structure processing)

---

## 🎯 Real FOXP2 Analysis Pipeline

### Example: Search for Real FOXP2 Patents

```python
from real_patent_query_agent import RealPatentQueryAgent
from real_deep_analysis_agent import RealDeepAnalysisAgent
from real_chemical_processor import RealChemicalProcessor

# 1. Search real patents
query_agent = RealPatentQueryAgent()
foxp2_results = query_agent.search_foxp2_compounds([
    "small molecule", "modulator", "autism", "NIB"
])

# 2. Process real chemical structures
chemical_processor = RealChemicalProcessor()
chemical_data = chemical_processor.process_foxp2_chemicals(foxp2_results)

# 3. Real GPT analysis
analysis_agent = RealDeepAnalysisAgent()
analysis = analysis_agent.analyze_foxp2_patent_real(foxp2_results)

print(f"Found {foxp2_results.content['total_results']} real FOXP2 patents")
print(f"Extracted {len(chemical_data.content['chemical_structures'])} real chemical structures")
print(f"GPT analysis score: {analysis.content['foxp2_analysis']['innovation_score']}")
```

---

## 🏗️ Production Deployment

### Docker Setup

```dockerfile
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    librdkit-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements_real.txt .
RUN pip install -r requirements_real.txt

# Copy application
COPY . /app
WORKDIR /app

# Set environment variables
ENV PYTHONPATH=/app

EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]
```

### Environment Variables for Production

```bash
# Core
export OPENAI_API_KEY="sk-your-key"
export OPENAI_MODEL="gpt-4"

# Patent APIs
export SEARCHAPI_KEY="your-key"
export USPTO_API_KEY="your-key"

# Chemical APIs  
export CHEMSPIDER_API_KEY="your-key"

# Database
export DATABASE_URL="postgresql://user:pass@localhost/patents"

# System
export ENVIRONMENT="production"
export LOG_LEVEL="INFO"
export MAX_WORKERS="4"
```

---

## 🧪 Chemical Structure Processing

The system uses **RDKit** for real chemical structure processing:

- **SMILES validation** and standardization
- **Molecular descriptor** calculation
- **Drug-likeness** assessment (Lipinski Rule of Five)
- **Structure similarity** searching
- **2D/3D structure** generation

### Supported Chemical Identifiers
- SMILES strings
- InChI/InChI Keys
- Chemical names (IUPAC/common)
- CAS Registry Numbers
- PubChem CIDs
- ChemSpider IDs

---

## 📊 Real Data Examples

### Example Real Patent Result
```json
{
  "patent_number": "US10123456B2",
  "title": "FOXP2 modulating compounds and methods",
  "source": "google_patents_real",
  "inventors": ["Dr. Jane Smith", "Dr. John Doe"],
  "assignees": ["Pharma Corp Inc."],
  "publication_date": "2023-05-15",
  "url": "https://patents.google.com/patent/US10123456B2",
  "pdf_link": "https://patents.google.com/patent/US10123456B2.pdf"
}
```

### Example Chemical Structure Result
```json
{
  "compound_name": "NIB-007",
  "smiles": "Cc1ccccc1NC(=O)c2cccc(Cc3c[nH]c4ccccc34)c2",
  "molecular_formula": "C23H20N2O",
  "molecular_weight": 340.42,
  "pubchem_cid": 123456789,
  "lipinski_compliant": true,
  "source_database": "pubchem",
  "confidence_score": 0.95
}
```

---

## 🔍 API Usage Limits

### Free Tier Limits
- **SearchAPI.io**: 1,000 searches/month
- **USPTO**: No official limit (fair use)
- **PubChem**: No limit
- **ChemSpider**: 1,000 requests/month
- **OpenAI**: Pay-per-use (~$0.03/1K tokens)

### Cost Estimates (Monthly)
- **Light use** (100 searches): ~$5-10
- **Moderate use** (1000 searches): ~$20-50  
- **Heavy use** (10,000 searches): ~$100-300

---

## ⚠️ Important Notes

### Rate Limiting
- APIs have rate limits - system includes automatic delays
- Use caching to minimize repeat requests
- Consider upgrading to paid tiers for production use

### Data Quality
- Real patent data can be incomplete or inconsistent
- Chemical structures may not be available for all patents
- Always validate results before making business decisions

### Legal Compliance
- Respect patent database terms of service
- Don't abuse free APIs
- Consider data licensing for commercial use

---

## 🛠️ Troubleshooting

### Common Issues

#### "OpenAI API key not set"
```bash
export OPENAI_API_KEY="sk-your-actual-key-here"
```

#### "RDKit not available"
```bash
conda install -c conda-forge rdkit
```

#### "No patents found"
- Check API keys are set correctly
- Verify search terms are appropriate
- Check API service status

#### "Chemical structure not found"
- Try alternative chemical names
- Check spelling and formatting
- Some compounds may not be in public databases

---

## 📈 Performance Optimization

### Caching Strategy
```python
# Enable caching for repeated searches
query_agent = RealPatentQueryAgent()
query_agent.enable_cache = True
query_agent.cache_ttl = 3600  # 1 hour
```

### Parallel Processing
```python
# Process multiple patents in parallel
import asyncio

async def process_patents(patent_list):
    tasks = []
    for patent in patent_list:
        task = asyncio.create_task(analyze_patent(patent))
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    return results
```

---

## 🎯 Ready for Real Patent Analysis!

Your system is now configured for **real patent search and analysis**:

✅ **Real patent databases** (Google Patents, USPTO, Espacenet)  
✅ **Real chemical processing** (RDKit, PubChem, ChemSpider)  
✅ **Real AI analysis** (OpenAI GPT-4)  
✅ **Production ready** (Docker, scaling, monitoring)

**Start analyzing real FOXP2 patents now!** 🚀