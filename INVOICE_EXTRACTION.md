# Invoice Data Extraction for Database Import

This guide explains how to extract structured invoice data from OCR results for database insertion.

## Overview

The invoice extraction tool (`invoice_extractor.py`) parses OCR text files and extracts key invoice fields for database import. It generates:
- **CSV files** for Excel/spreadsheet import
- **JSON files** for API integration
- **SQL files** with INSERT statements for direct database import

## Extracted Fields

The tool extracts the following invoice fields:

| Field | Description |
|-------|-------------|
| `invoice_number` | Invoice/reference number |
| `invoice_date` | Invoice date |
| `tracking_number` | Shipping/tracking number |
| `company_name` | Company name |
| `total_amount` | Total invoice amount (numeric) |
| `currency` | Currency code (USD, JPY, etc.) |
| `phone` | Phone number |
| `fax` | Fax number |
| `item_count` | Number of line items |
| `source_file` | Original TXT filename |
| `source_path` | Full path to source file |

## Quick Start

### 1. Run OCR Extraction

First, process your invoice documents with OCR:

```bash
ocr-enhanced --image invoice.pdf --lang ch --use-cpu
```

This creates a results directory like `results/20260515_104903/` with TXT files.

### 2. Extract Invoice Data

Process all OCR results to generate database-ready files:

```bash
python scripts/extract_invoices.py --dir results/20260515_104903
```

This generates three files:
- `invoices_extracted_TIMESTAMP.csv` - CSV for database import
- `invoices_extracted_TIMESTAMP.json` - JSON format
- `invoices_extracted_TIMESTAMP.sql` - SQL INSERT statements

### 3. Import to Database

**Option A: Using SQL file (MySQL/PostgreSQL)**

```bash
mysql -u username -p database_name < invoices_extracted_20260515_111940.sql
```

**Option B: Using CSV import**

Most databases support CSV import:

```sql
-- MySQL
LOAD DATA INFILE 'invoices_extracted_20260515_111940.csv'
INTO TABLE invoices
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

-- PostgreSQL
COPY invoices FROM 'invoices_extracted_20260515_111940.csv'
DELIMITER ',' CSV HEADER;
```

**Option C: Excel/Google Sheets**

Simply open the CSV file in Excel or import to Google Sheets.

## Usage Examples

### Process Specific Results Directory

```bash
python scripts/extract_invoices.py --dir results/20260515_104903
```

### Specify Custom Output File

```bash
python scripts/extract_invoices.py --dir results/20260515_104903 --output my_invoices.csv
```

### Process All Results at Once

```bash
python scripts/extract_invoices.py --dir results
```

## Output Format

### CSV Output

```csv
invoice_number,invoice_date,company_name,total_amount,currency,phone,fax,item_count
KTB0911-X52-S01-24538,,Importer SANEI SANSYOU CORPORATION,913.0,JPY,,,55
```

### JSON Output

```json
[
  {
    "invoice_number": "KTB0911-X52-S01-24538",
    "company_name": "Importer SANEI SANSYOU CORPORATION",
    "total_amount": 913.0,
    "currency": "JPY",
    "item_count": 55,
    "source_file": "インボイス見本_page_0002.txt"
  }
]
```

### SQL Output

```sql
CREATE TABLE IF NOT EXISTS invoices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    invoice_number VARCHAR(100),
    invoice_date VARCHAR(50),
    company_name VARCHAR(255),
    total_amount DECIMAL(15,2),
    currency VARCHAR(10),
    phone VARCHAR(50),
    fax VARCHAR(50),
    item_count INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO invoices (invoice_number, company_name, total_amount, currency, item_count)
VALUES ('KTB0911-X52-S01-24538', 'Importer SANEI SANSYOU CORPORATION', 913.0, 'JPY', 55);
```

## Database Schema

The SQL output includes a table creation statement. Here's the recommended schema:

```sql
CREATE TABLE invoices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    invoice_number VARCHAR(100),
    invoice_date VARCHAR(50),
    tracking_number VARCHAR(100),
    company_name VARCHAR(255),
    total_amount DECIMAL(15,2),
    currency VARCHAR(10) DEFAULT 'USD',
    phone VARCHAR(50),
    fax VARCHAR(50),
    item_count INT DEFAULT 0,
    source_file VARCHAR(255),
    source_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_invoice_number (invoice_number),
    INDEX idx_company_name (company_name),
    INDEX idx_invoice_date (invoice_date)
);
```

## Programmatic Usage

You can also use the extractor in your Python code:

```python
from ocr_invoice_reader.utils.invoice_extractor import InvoiceExtractor

# Initialize extractor
extractor = InvoiceExtractor()

# Extract from TXT file
data = extractor.extract_from_file('results/page_0002.txt')

# Get database-ready format
db_data = extractor.format_for_database(data)

# Generate SQL INSERT
sql = extractor.generate_sql_insert(data)
print(sql)
```

## Customization

### Modify Extraction Patterns

Edit `ocr_invoice_reader/utils/invoice_extractor.py` to adjust regex patterns:

```python
self.patterns = {
    'invoice_no': [
        r'INVOICE\s*NO[.:]?\s*([A-Z0-9-]+)',
        r'INV\s*NO[.:]?\s*([A-Z0-9-]+)',
        # Add your custom patterns here
    ],
    # ... more patterns
}
```

### Add Custom Fields

To extract additional fields, add patterns and update the database schema:

```python
# In invoice_extractor.py
self.patterns['custom_field'] = [
    r'YOUR_PATTERN_HERE',
]

# In SQL schema
ALTER TABLE invoices ADD COLUMN custom_field VARCHAR(100);
```

## Troubleshooting

### Issue: Missing Invoice Numbers

**Cause**: OCR didn't recognize the invoice number clearly, or the pattern doesn't match.

**Solution**: Check the TXT file and adjust patterns in `invoice_extractor.py`:

```python
'invoice_no': [
    r'INVOICE\s*NO[.:]?\s*([A-Z0-9-]+)',
    r'INV\s*NO[.:]?\s*([A-Z0-9-]+)',
    r'INVNO\s+([A-Z0-9]+)',
    r'Your custom pattern here',
]
```

### Issue: Wrong Currency Detection

**Cause**: Currency symbols not detected correctly.

**Solution**: The tool automatically detects currency from text context:
- Contains "JPY" or "(JPY)" → Japanese Yen
- Contains "$" → US Dollar
- Modify detection logic in `extract_from_text()` method

### Issue: Incorrect Amount Parsing

**Cause**: Number formatting (commas, decimals) varies by locale.

**Solution**: Check `_parse_amount()` method. It removes commas by default:

```python
def _parse_amount(self, amount_str: Optional[str]) -> Optional[float]:
    if not amount_str:
        return None
    try:
        clean_str = amount_str.replace(',', '')  # Remove thousands separator
        return float(clean_str)
    except:
        return None
```

## Performance

- **Processing Speed**: ~100-200 TXT files per second
- **Memory Usage**: Minimal (processes files one at a time)
- **Scalability**: Can handle thousands of invoices

## Integration with Workflow

### Complete Invoice Processing Pipeline

```bash
# Step 1: OCR extraction
ocr-enhanced --image invoices.pdf --lang ch --use-cpu

# Step 2: Extract invoice data
python scripts/extract_invoices.py --dir results/20260515_104903

# Step 3: Import to database
mysql -u root -p invoices_db < invoices_extracted_20260515_111940.sql

# Step 4: Verify import
mysql -u root -p invoices_db -e "SELECT * FROM invoices LIMIT 5;"
```

## Notes

- The tool works best with **clean OCR results** (use `--use-llm` for better accuracy)
- **Multi-page PDFs**: Each page is processed separately, you may need to merge related pages
- **Language Support**: Works with English, Chinese, Japanese invoices
- **Date Formats**: Supports various date formats (YYYY-MM-DD, MM/DD/YYYY, etc.)

## Related Documentation

- [Main README](README.md) - Project overview
- [IMPROVEMENTS.md](IMPROVEMENTS.md) - Recent fixes and enhancements
- [FIX_OCR_SPACES.md](FIX_OCR_SPACES.md) - OCR space correction fix

## Support

For issues or questions about invoice extraction:
1. Check the TXT files in your results directory
2. Review extraction patterns in `invoice_extractor.py`
3. Open an issue on GitHub with sample TXT files
