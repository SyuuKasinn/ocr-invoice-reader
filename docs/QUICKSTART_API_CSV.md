# Quick Start: REST API & CSV Export

## 🚀 New Features

### 1. REST API (v2.2.0+)
Full-featured REST API for document extraction with web service integration.

### 2. CSV Export (v2.2.0+)
Export extraction results to CSV format for analysis and reporting.

---

## 📦 Installation

```bash
# Install with API support
pip install -e ".[api]"
```

---

## 🌐 REST API Usage

### Start the API Server

```bash
ocr-api

# Server starts at: http://localhost:8000
# Docs available at: http://localhost:8000/docs
```

### Quick Test (cURL)

```bash
# Upload and extract a document
curl -X POST "http://localhost:8000/api/v1/extract?lang=ch" \
  -F "file=@invoice.pdf"
```

### Python Client

```python
import requests

# Extract document
url = "http://localhost:8000/api/v1/extract"
files = {"file": open("invoice.pdf", "rb")}
response = requests.post(url, files=files, params={"lang": "ch"})

result = response.json()
print(f"Total: {result['document']['total_amount']}")

# Download as CSV
task_id = result["task_id"]
csv_url = f"http://localhost:8000/api/v1/result/{task_id}/csv?mode=summary"
csv_response = requests.get(csv_url)

with open("result.csv", "wb") as f:
    f.write(csv_response.content)
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/v1/extract` | POST | Extract single document (sync) |
| `/api/v1/extract/enhanced` | POST | Enhanced structure analysis |
| `/api/v1/extract/batch` | POST | Batch extraction (async) |
| `/api/v1/result/{id}` | GET | Get result by task ID |
| `/api/v1/result/{id}/csv` | GET | Download CSV |
| `/api/v1/results` | GET | List recent results |

**Full API documentation**: See [API_USAGE.md](API_USAGE.md)

---

## 📊 CSV Export Usage

### Command Line (Batch Mode)

CSV files are automatically generated when using batch mode:

```bash
ocr-extract --input-dir invoices/ --output-dir results/

# Output:
# results/
#   ├── extraction_summary.csv   # One row per document
#   └── extraction_items.csv     # One row per item
```

### Python API

```python
from ocr_invoice_reader.extractors.document_extractor import DocumentExtractor
from ocr_invoice_reader.models.base import BaseDocument

# Extract document
extractor = DocumentExtractor(use_gpu=False, lang='ch')
document = extractor.extract('invoice.pdf')

# Export as summary CSV (document-level)
document.save_to_csv('result_summary.csv', mode='summary')

# Export as items CSV (line-item level)
document.save_to_csv('result_items.csv', mode='items')

# Export multiple documents
documents = [doc1, doc2, doc3]
BaseDocument.save_multiple_to_csv(
    documents,
    'all_results.csv',
    mode='summary'
)
```

### CSV Formats

**Summary CSV** (one row per document):
```csv
document_type,document_number,date,sender_company,receiver_company,total_amount,currency,confidence
invoice,INV-001,2024-05-14,ABC Company,XYZ Corp,10000,JPY,95.00%
invoice,INV-002,2024-05-15,ABC Company,DEF Corp,15000,JPY,92.50%
```

**Items CSV** (one row per line item):
```csv
document_number,document_type,item_index,description,quantity,unit_price,amount
INV-001,invoice,1,Product A,10,1000,10000
INV-001,invoice,2,Product B,5,2000,10000
INV-002,invoice,1,Product C,20,750,15000
```

---

## 🔗 Integration Examples

### 1. Web Application Integration

```javascript
// Frontend: Upload and extract
const formData = new FormData();
formData.append('file', fileInput.files[0]);

const response = await fetch('http://localhost:8000/api/v1/extract?lang=ch', {
  method: 'POST',
  body: formData
});

const result = await response.json();
console.log('Extracted:', result.document);

// Download CSV
const csvUrl = `http://localhost:8000/api/v1/result/${result.task_id}/csv?mode=summary`;
window.open(csvUrl, '_blank');
```

### 2. Data Pipeline Integration

```python
import requests
import pandas as pd

# Extract multiple documents via API
client = requests.Session()
base_url = "http://localhost:8000"

# Upload batch
files = [("files", open(f, "rb")) for f in pdf_files]
response = client.post(f"{base_url}/api/v1/extract/batch", files=files)
task_id = response.json()["task_id"]

# Wait for completion and download CSV
csv_response = client.get(f"{base_url}/api/v1/result/{task_id}/csv?mode=summary")

# Load into pandas for analysis
df = pd.read_csv(io.StringIO(csv_response.text))
print(df.describe())
```

### 3. Workflow Automation

```python
from pathlib import Path
from ocr_invoice_reader.extractors.document_extractor import DocumentExtractor

def process_invoice_folder(input_dir, output_dir):
    """Automated invoice processing with CSV export"""
    extractor = DocumentExtractor(use_gpu=False, lang='ch')
    
    # Process all PDFs
    documents = extractor.batch_extract(
        input_path=input_dir,
        output_dir=output_dir,
        visualize=False
    )
    
    # CSV files are automatically generated:
    # - {output_dir}/extraction_summary.csv
    # - {output_dir}/extraction_items.csv
    
    print(f"✓ Processed {len(documents)} invoices")
    print(f"✓ CSV files saved to: {output_dir}")
    
    return documents

# Run nightly batch
process_invoice_folder("incoming/", "processed/2024-05-14/")
```

---

## 📈 Analysis with Pandas

```python
import pandas as pd

# Load summary CSV
df = pd.read_csv('extraction_summary.csv')

# Basic statistics
print(f"Total invoices: {len(df)}")
print(f"Total amount: {df['total_amount'].sum()}")
print(f"Average confidence: {df['confidence'].mean()}")

# Group by sender
by_sender = df.groupby('sender_company')['total_amount'].sum()
print("\nTotal by sender:")
print(by_sender)

# Load items CSV for detailed analysis
items_df = pd.read_csv('extraction_items.csv')

# Top products
top_products = items_df.groupby('description')['amount'].sum().sort_values(ascending=False)
print("\nTop 10 products:")
print(top_products.head(10))
```

---

## 🎯 Use Cases

### 1. Accounting System Integration
- Extract invoices via API
- Export to CSV
- Import into accounting software (QuickBooks, Xero, etc.)

### 2. Data Analytics Pipeline
- Batch process historical invoices
- Export CSV for analysis
- Generate business intelligence reports

### 3. Web Service Backend
- Accept uploads via REST API
- Process documents asynchronously
- Return structured JSON or CSV

### 4. Automated Workflows
- Monitor folder for new invoices
- Auto-extract and save CSV
- Trigger downstream processes

---

## 🔧 Configuration

### API Server Options

```bash
# Custom host/port
ocr-api --host 0.0.0.0 --port 8080

# Multiple workers (production)
ocr-api --workers 4

# Development with auto-reload
ocr-api --reload
```

### CSV Export Options

```python
# Mode options
document.save_to_csv('output.csv', mode='summary')  # Document level
document.save_to_csv('output.csv', mode='items')    # Item level

# Batch export
BaseDocument.save_multiple_to_csv(
    documents,
    'batch.csv',
    mode='summary'  # or 'items'
)
```

---

## 📚 More Resources

- **Full API Documentation**: [API_USAGE.md](API_USAGE.md)
- **CSV Examples**: [../examples/csv_export_example.py](../examples/csv_export_example.py)
- **API Client Examples**: [../examples/api_client_example.py](../examples/api_client_example.py)
- **Main README**: [../README.md](../README.md)

---

## 🐛 Troubleshooting

### API Server Won't Start

```bash
# Install API dependencies
pip install -e ".[api]"

# Check if port is already in use
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows
```

### CSV Encoding Issues

```python
# Ensure UTF-8 encoding when opening
import pandas as pd
df = pd.read_csv('output.csv', encoding='utf-8')
```

### Large Batch Processing

For large batches (>50 files), use multiple API calls or increase worker count:

```bash
ocr-api --workers 4  # Production mode
```

---

## ✨ What's Next?

- Check out the [full API documentation](API_USAGE.md)
- Run the [example scripts](../examples/)
- Integrate with your application
- Share your feedback!
