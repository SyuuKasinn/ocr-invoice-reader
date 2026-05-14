# API Usage Guide

## Installation

Install with API support:

```bash
pip install -e ".[api]"
```

This installs FastAPI, uvicorn, and other API dependencies.

## Starting the API Server

### Basic Usage

```bash
# Start server on default port (8000)
ocr-api

# Custom host and port
ocr-api --host 0.0.0.0 --port 8080

# Development mode with auto-reload
ocr-api --reload

# Multiple workers (production)
ocr-api --workers 4
```

### Access Documentation

Once the server is running:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **API Root**: http://localhost:8000/

---

## API Endpoints

### 1. Health Check

**GET** `/health`

Check if the API is running.

**Response:**
```json
{
  "status": "healthy",
  "version": "2.1.0",
  "timestamp": "2024-05-14T10:30:00"
}
```

---

### 2. Extract Document (Synchronous)

**POST** `/api/v1/extract`

Extract structured information from a single document.

**Parameters:**
- `file` (required): Document file (PDF, JPG, PNG)
- `lang` (optional): OCR language - `ch`, `en`, `japan`, `korean` (default: `ch`)
- `use_gpu` (optional): Use GPU acceleration (default: `false`)
- `visualize` (optional): Generate visualization (default: `false`)

**Example (cURL):**
```bash
curl -X POST "http://localhost:8000/api/v1/extract?lang=ch&use_gpu=false" \
  -F "file=@invoice.pdf"
```

**Example (Python):**
```python
import requests

url = "http://localhost:8000/api/v1/extract"
files = {"file": open("invoice.pdf", "rb")}
params = {"lang": "ch", "use_gpu": False}

response = requests.post(url, files=files, params=params)
result = response.json()

print(f"Document Type: {result['document']['document_type']}")
print(f"Total Amount: {result['document']['total_amount']}")
```

**Response:**
```json
{
  "task_id": "abc123-def456",
  "status": "completed",
  "filename": "invoice.pdf",
  "document": {
    "document_type": "invoice",
    "document_number": "INV-2024-001",
    "date": "2024-05-14",
    "sender": {
      "company": "ABC Company",
      "address": "123 Main St"
    },
    "receiver": {
      "company": "XYZ Corp",
      "address": "456 Oak Ave"
    },
    "items": [
      {
        "description": "Product A",
        "quantity": 10,
        "unit_price": 100,
        "amount": 1000
      }
    ],
    "total_amount": 1000,
    "currency": "JPY",
    "confidence": 0.95
  },
  "timestamp": "2024-05-14T10:30:00"
}
```

---

### 3. Enhanced Structure Analysis

**POST** `/api/v1/extract/enhanced`

Extract with enhanced coordinate-based table detection.

**Parameters:**
- `file` (required): Document file
- `lang` (optional): OCR language (default: `ch`)
- `use_gpu` (optional): Use GPU (default: `false`)

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/extract/enhanced?lang=ch" \
  -F "file=@invoice.pdf"
```

**Response:**
```json
{
  "task_id": "xyz789",
  "status": "completed",
  "filename": "invoice.pdf",
  "method": "coordinate_based",
  "regions": [
    {
      "type": "title",
      "bbox": [100, 50, 500, 100],
      "confidence": 0.98,
      "text": "Invoice"
    },
    {
      "type": "table",
      "bbox": [50, 200, 550, 400],
      "confidence": 0.95,
      "text": "Item A | 10 | 100\nItem B | 5 | 200",
      "table_html": "<table>...</table>",
      "rows": 2,
      "columns": 3
    }
  ]
}
```

---

### 4. Batch Extract (Asynchronous)

**POST** `/api/v1/extract/batch`

Process multiple documents in background.

**Parameters:**
- `files[]` (required): Multiple document files (max 50)
- `lang` (optional): OCR language (default: `ch`)
- `use_gpu` (optional): Use GPU (default: `false`)

**Example (Python):**
```python
import requests
import time

url = "http://localhost:8000/api/v1/extract/batch"

files = [
    ("files", open("invoice1.pdf", "rb")),
    ("files", open("invoice2.pdf", "rb")),
    ("files", open("invoice3.pdf", "rb"))
]

response = requests.post(url, files=files, params={"lang": "ch"})
result = response.json()
task_id = result["task_id"]

print(f"Task ID: {task_id}")
print(f"Check status at: {result['check_status']}")

# Poll for completion
while True:
    status_response = requests.get(f"http://localhost:8000/api/v1/result/{task_id}")
    status = status_response.json()
    
    if status["status"] == "completed":
        print(f"Processed {len(status['documents'])} documents")
        break
    elif status["status"] == "failed":
        print(f"Error: {status['error']}")
        break
    else:
        print(f"Progress: {status['processed']}/{status['total_files']}")
        time.sleep(2)
```

**Initial Response:**
```json
{
  "task_id": "batch-123",
  "status": "processing",
  "message": "Processing 3 files in background",
  "check_status": "/api/v1/result/batch-123"
}
```

---

### 5. Get Result

**GET** `/api/v1/result/{task_id}`

Get extraction result by task ID.

**Example:**
```bash
curl "http://localhost:8000/api/v1/result/abc123-def456"
```

---

### 6. Download CSV

**GET** `/api/v1/result/{task_id}/csv?mode=summary`

Download extraction result as CSV file.

**Parameters:**
- `mode` (optional): Export mode - `summary` (one row per document) or `items` (one row per item) (default: `summary`)

**Example:**
```bash
# Summary CSV (one row per document)
curl "http://localhost:8000/api/v1/result/abc123/csv?mode=summary" \
  -o extraction_summary.csv

# Items CSV (one row per item)
curl "http://localhost:8000/api/v1/result/abc123/csv?mode=items" \
  -o extraction_items.csv
```

**Python Example:**
```python
import requests

task_id = "abc123-def456"

# Download summary CSV
response = requests.get(
    f"http://localhost:8000/api/v1/result/{task_id}/csv",
    params={"mode": "summary"}
)

with open("extraction_summary.csv", "wb") as f:
    f.write(response.content)

# Download items CSV
response = requests.get(
    f"http://localhost:8000/api/v1/result/{task_id}/csv",
    params={"mode": "items"}
)

with open("extraction_items.csv", "wb") as f:
    f.write(response.content)
```

**CSV Output (Summary Mode):**
```csv
document_type,document_number,date,sender_company,receiver_company,total_amount,currency,confidence
invoice,INV-2024-001,2024-05-14,ABC Company,XYZ Corp,1000,JPY,95.00%
```

**CSV Output (Items Mode):**
```csv
document_number,document_type,item_index,description,quantity,unit,unit_price,amount
INV-2024-001,invoice,1,Product A,10,pcs,100,1000
INV-2024-001,invoice,2,Product B,5,pcs,200,1000
```

---

### 7. List Results

**GET** `/api/v1/results?limit=10`

List recent extraction results.

**Parameters:**
- `limit` (optional): Maximum results to return (1-100, default: 10)

**Example:**
```bash
curl "http://localhost:8000/api/v1/results?limit=5"
```

---

### 8. Delete Result

**DELETE** `/api/v1/result/{task_id}`

Delete a stored result.

**Example:**
```bash
curl -X DELETE "http://localhost:8000/api/v1/result/abc123-def456"
```

---

## Complete Python Client Example

```python
import requests
import time
from pathlib import Path

class OCRInvoiceClient:
    """Python client for OCR Invoice Reader API"""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def extract_single(self, file_path, lang="ch", use_gpu=False):
        """Extract from single document"""
        url = f"{self.base_url}/api/v1/extract"
        
        with open(file_path, "rb") as f:
            files = {"file": f}
            params = {"lang": lang, "use_gpu": use_gpu}
            response = requests.post(url, files=files, params=params)
            response.raise_for_status()
            return response.json()
    
    def extract_batch(self, file_paths, lang="ch", use_gpu=False, wait=True):
        """Extract from multiple documents"""
        url = f"{self.base_url}/api/v1/extract/batch"
        
        files = [("files", open(fp, "rb")) for fp in file_paths]
        params = {"lang": lang, "use_gpu": use_gpu}
        
        response = requests.post(url, files=files, params=params)
        response.raise_for_status()
        result = response.json()
        
        if wait:
            return self.wait_for_completion(result["task_id"])
        return result
    
    def wait_for_completion(self, task_id, poll_interval=2, timeout=300):
        """Wait for batch processing to complete"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            result = self.get_result(task_id)
            
            if result["status"] == "completed":
                return result
            elif result["status"] == "failed":
                raise Exception(f"Processing failed: {result.get('error')}")
            
            time.sleep(poll_interval)
        
        raise TimeoutError(f"Processing timeout after {timeout}s")
    
    def get_result(self, task_id):
        """Get result by task ID"""
        url = f"{self.base_url}/api/v1/result/{task_id}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    
    def download_csv(self, task_id, output_path, mode="summary"):
        """Download result as CSV"""
        url = f"{self.base_url}/api/v1/result/{task_id}/csv"
        params = {"mode": mode}
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        with open(output_path, "wb") as f:
            f.write(response.content)
        
        return output_path


# Usage example
if __name__ == "__main__":
    client = OCRInvoiceClient()
    
    # Single document extraction
    print("Extracting single document...")
    result = client.extract_single("invoice.pdf", lang="ch")
    print(f"Document Type: {result['document']['document_type']}")
    print(f"Total Amount: {result['document']['total_amount']}")
    
    # Download as CSV
    task_id = result["task_id"]
    client.download_csv(task_id, "result_summary.csv", mode="summary")
    client.download_csv(task_id, "result_items.csv", mode="items")
    print("CSV files downloaded")
    
    # Batch processing
    print("\nProcessing batch...")
    files = ["invoice1.pdf", "invoice2.pdf", "invoice3.pdf"]
    batch_result = client.extract_batch(files, lang="ch")
    print(f"Processed {len(batch_result['documents'])} documents")
    
    # Download batch CSV
    batch_id = batch_result["task_id"]
    client.download_csv(batch_id, "batch_summary.csv", mode="summary")
    print("Batch CSV downloaded")
```

---

## Production Deployment

### Using Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -e ".[api]"

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run API server
CMD ["ocr-api", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### Using systemd

```ini
[Unit]
Description=OCR Invoice Reader API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/ocr-invoice-reader
ExecStart=/usr/local/bin/ocr-api --host 0.0.0.0 --port 8000 --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## Notes

- **Storage**: Results are stored in memory. For production, use a database (Redis, PostgreSQL, etc.)
- **File Size**: Recommended max file size: 10MB per file
- **Rate Limiting**: Not implemented by default. Add middleware for production
- **Authentication**: Not implemented. Add OAuth2/JWT for production
- **GPU**: Set `use_gpu=true` for 3-10x faster processing (requires CUDA)
