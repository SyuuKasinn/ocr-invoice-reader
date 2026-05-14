# 🎉 New Features: REST API & CSV Export

## Overview

Version 2.2.0 introduces two major features to make OCR Invoice Reader more API-friendly and data-analysis ready:

1. **🌐 REST API** - Full-featured web service with FastAPI
2. **📊 CSV Export** - Export results to CSV for analysis

---

## 🚀 Quick Demo

### REST API in 3 Steps

```bash
# 1. Install with API support
pip install -e ".[api]"

# 2. Start API server
ocr-api

# 3. Use the API
curl -X POST "http://localhost:8000/api/v1/extract?lang=ch" \
  -F "file=@invoice.pdf"
```

**Interactive Docs**: http://localhost:8000/docs

### CSV Export in 3 Lines

```python
from ocr_invoice_reader.extractors.document_extractor import DocumentExtractor

extractor = DocumentExtractor(use_gpu=False, lang='ch')
documents = extractor.batch_extract('invoices/', 'results/')
# CSV files automatically generated! ✓
```

---

## 🌐 REST API Features

### What You Get

✅ **Synchronous Extraction** - Upload and get results immediately  
✅ **Asynchronous Batch Processing** - Process multiple files in background  
✅ **Enhanced Structure Analysis** - Detailed table and region detection  
✅ **CSV Download** - Export results directly from API  
✅ **Task Management** - Track processing status  
✅ **Interactive Docs** - Swagger UI and ReDoc

### API Endpoints

| Endpoint | What It Does |
|----------|--------------|
| `POST /api/v1/extract` | Extract single document (instant) |
| `POST /api/v1/extract/batch` | Process multiple files (background) |
| `GET /api/v1/result/{id}/csv` | Download as CSV |
| `GET /docs` | Interactive API documentation |

### Python Client Example

```python
import requests

# Extract document
response = requests.post(
    "http://localhost:8000/api/v1/extract",
    files={"file": open("invoice.pdf", "rb")},
    params={"lang": "ch"}
)

result = response.json()
print(f"Amount: {result['document']['total_amount']}")

# Download CSV
task_id = result["task_id"]
csv_data = requests.get(
    f"http://localhost:8000/api/v1/result/{task_id}/csv?mode=summary"
)

with open("result.csv", "wb") as f:
    f.write(csv_data.content)
```

---

## 📊 CSV Export Features

### Two Export Modes

**1. Summary Mode** - One row per document
- Document-level information
- Sender/receiver details
- Total amounts and currency
- Confidence scores

**2. Items Mode** - One row per line item
- Individual product/service entries
- Quantities and prices
- Links back to document via document_number

### Usage Examples

**Command Line:**
```bash
# Batch processing auto-generates CSV
ocr-extract --input-dir invoices/ --output-dir results/

# Results:
# - results/extraction_summary.csv
# - results/extraction_items.csv
```

**Python API:**
```python
# Single document
document.save_to_csv('output.csv', mode='summary')

# Multiple documents
from ocr_invoice_reader.models.base import BaseDocument
BaseDocument.save_multiple_to_csv(documents, 'all.csv', mode='items')
```

**Via REST API:**
```bash
curl "http://localhost:8000/api/v1/result/{task_id}/csv?mode=summary" \
  -o results.csv
```

### CSV Output Preview

**Summary CSV:**
```csv
document_type,document_number,sender_company,receiver_company,total_amount
invoice,INV-001,ABC Corp,XYZ Ltd,10000
invoice,INV-002,ABC Corp,DEF Inc,15000
```

**Items CSV:**
```csv
document_number,item_index,description,quantity,unit_price,amount
INV-001,1,Product A,10,1000,10000
INV-001,2,Product B,5,2000,10000
INV-002,1,Product C,20,750,15000
```

---

## 🔗 Integration Examples

### Web Application

```javascript
// Frontend upload
const formData = new FormData();
formData.append('file', fileInput.files[0]);

const response = await fetch('http://localhost:8000/api/v1/extract', {
  method: 'POST',
  body: formData
});

const data = await response.json();
console.log('Extracted:', data.document);
```

### Data Pipeline

```python
import pandas as pd
import requests

# Extract via API
response = requests.post(
    "http://localhost:8000/api/v1/extract",
    files={"file": open("invoice.pdf", "rb")}
)
task_id = response.json()["task_id"]

# Download CSV
csv_response = requests.get(
    f"http://localhost:8000/api/v1/result/{task_id}/csv"
)

# Analyze with pandas
df = pd.read_csv(io.StringIO(csv_response.text))
print(f"Total: {df['total_amount'].sum()}")
```

### Automation Script

```python
from pathlib import Path
from ocr_invoice_reader.extractors.document_extractor import DocumentExtractor

def daily_invoice_processing():
    """Process today's invoices"""
    extractor = DocumentExtractor(use_gpu=False, lang='ch')
    
    # Batch process
    documents = extractor.batch_extract(
        input_path='incoming/',
        output_dir='processed/today/',
        visualize=False
    )
    
    # CSV files auto-generated!
    print(f"✓ Processed {len(documents)} invoices")
    print(f"✓ CSV saved to: processed/today/")

# Run daily
daily_invoice_processing()
```

---

## 📖 Documentation

| Resource | Link |
|----------|------|
| REST API Guide | [docs/API_USAGE.md](docs/API_USAGE.md) |
| Quick Start | [docs/QUICKSTART_API_CSV.md](docs/QUICKSTART_API_CSV.md) |
| API Client Example | [examples/api_client_example.py](examples/api_client_example.py) |
| CSV Export Example | [examples/csv_export_example.py](examples/csv_export_example.py) |
| Change Log | [CHANGES_v2.2.md](CHANGES_v2.2.md) |

---

## 🎯 Use Cases

### 1. Accounting System Integration
Extract → Export CSV → Import to QuickBooks/Xero

### 2. Business Intelligence
Batch process → CSV export → Power BI/Tableau analysis

### 3. Web Service Backend
REST API → Frontend integration → Real-time processing

### 4. Automated Workflows
Folder monitoring → Auto-extract → Generate reports

---

## 🚀 Getting Started

### Installation

```bash
# Basic installation
pip install -e .

# With API support
pip install -e ".[api]"
```

### Start API Server

```bash
ocr-api

# Custom configuration
ocr-api --host 0.0.0.0 --port 8080 --workers 4
```

### Try It Out

```bash
# Test extraction
curl -X POST "http://localhost:8000/api/v1/extract?lang=ch" \
  -F "file=@test_invoice.pdf"

# Visit interactive docs
open http://localhost:8000/docs
```

---

## 💡 Tips

### Performance
- Use `use_gpu=true` for 3-10x faster processing
- Enable multiple workers for production: `ocr-api --workers 4`
- Batch processing is more efficient than individual files

### CSV Analysis
- Use pandas for advanced analysis: `pip install pandas`
- Summary mode for document-level reports
- Items mode for product/SKU analysis

### Production Deployment
- Add authentication (OAuth2/JWT)
- Use database for persistent storage (not in-memory)
- Implement rate limiting
- Set up monitoring and logging

---

## 🆘 Support

- 📚 **Documentation**: See [docs/](docs/) folder
- 💬 **Issues**: [GitHub Issues](https://github.com/SyuuKasinn/ocr-invoice-reader/issues)
- 📧 **Examples**: See [examples/](examples/) folder

---

## ✨ What's Next?

Try it out and let us know what you think! 

```bash
# Install
pip install -e ".[api]"

# Start server
ocr-api

# Visit docs
open http://localhost:8000/docs
```

Happy extracting! 🎉
