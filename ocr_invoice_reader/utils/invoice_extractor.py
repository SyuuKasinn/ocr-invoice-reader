"""
Invoice data extractor from OCR TXT files
Extracts structured invoice data for database insertion
"""
import re
from typing import Dict, List, Optional
from pathlib import Path


class InvoiceExtractor:
    """Extract invoice data from OCR text for database insertion"""

    def __init__(self):
        self.patterns = {
            'invoice_no': [
                r'INVOICE\s*NO[.:]?\s*([A-Z0-9-]+)',
                r'INV\s*NO[.:]?\s*([A-Z0-9-]+)',
                r'INVNO\s+([A-Z0-9]+)',
            ],
            'date': [
                r'DATE[:\s]+(\d{4}[-/]\d{1,2}[-/]\d{1,2})',
                r'DATE[:\s]+(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            ],
            'tracking_no': [
                r'Tracking\s*No[.:]?\s*([0-9-]+)',
                r'追[送]*番号[:\s]*([A-Z0-9:-]+)',
            ],
            'company': [
                r'^([A-Z][A-Z\s&.,]+(?:CO[.,]?LTD|CORPORATION|INC|LIMITED))',
            ],
            'total_amount': [
                r'Total[:\s]+\$?([\d,]+\.?\d*)',
                r'Total\s*Amount[:\s]+\$?([\d,]+\.?\d*)',
            ],
            'tel': [
                r'Tel[:\s]+([\d\s+-]+)',
                r'TEL[:\s]+([\d+-]+)',
            ],
            'fax': [
                r'Fax[:\s]+([\d\s+-]+)',
                r'FAX[:\s]+([\d+-]+)',
            ],
        }

    def extract_from_file(self, txt_path: str) -> Dict:
        """Extract invoice data from TXT file"""
        with open(txt_path, 'r', encoding='utf-8') as f:
            text = f.read()

        return self.extract_from_text(text)

    def extract_from_text(self, text: str) -> Dict:
        """Extract invoice data from text content"""
        result = {
            'invoice_no': None,
            'date': None,
            'tracking_no': None,
            'company': None,
            'total_amount': None,
            'currency': 'USD',
            'tel': None,
            'fax': None,
            'items': [],
            'raw_text_snippet': text[:200] if text else None,
        }

        # Extract basic fields
        for field, patterns in self.patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if match:
                    value = match.group(1).strip()
                    result[field] = value
                    break

        # Detect currency
        if 'JPY' in text or '(JPY)' in text:
            result['currency'] = 'JPY'
        elif '$' in text:
            result['currency'] = 'USD'

        # Extract items from table regions
        items = self._extract_items(text)
        result['items'] = items
        result['items_count'] = len(items)

        return result

    def _extract_items(self, text: str) -> List[Dict]:
        """Extract line items from invoice"""
        items = []

        # Look for table regions
        table_pattern = r'\[Region \d+ - table\](.*?)(?=\[Region|\Z)'
        tables = re.findall(table_pattern, text, re.DOTALL)

        for table_text in tables:
            lines = table_text.strip().split('\n')

            for line in lines:
                # Skip header lines
                if any(keyword in line.upper() for keyword in ['ITEM NO', 'DESCRIPTION', 'QTY', 'PRICE', 'AMOUNT']):
                    continue

                # Try to extract item data
                # Pattern: item_no | description | quantity | price | amount
                parts = [p.strip() for p in line.split('|')]

                if len(parts) >= 3:
                    # Look for numeric values (quantity, price, amount)
                    numbers = re.findall(r'[\d,]+\.?\d*', line)

                    if numbers:
                        item = {
                            'line': line.strip(),
                            'values': numbers,
                        }

                        # Try to identify quantity and amount
                        if len(numbers) >= 2:
                            item['quantity'] = numbers[-2]
                            item['amount'] = numbers[-1]

                        items.append(item)

        return items

    def format_for_database(self, data: Dict) -> Dict:
        """Format extracted data for database insertion"""
        return {
            'invoice_number': data.get('invoice_no'),
            'invoice_date': data.get('date'),
            'tracking_number': data.get('tracking_no'),
            'company_name': data.get('company'),
            'total_amount': self._parse_amount(data.get('total_amount')),
            'currency': data.get('currency'),
            'phone': data.get('tel'),
            'fax': data.get('fax'),
            'item_count': data.get('items_count', 0),
            'created_at': None,  # Should be set by database
        }

    def _parse_amount(self, amount_str: Optional[str]) -> Optional[float]:
        """Parse amount string to float"""
        if not amount_str:
            return None

        try:
            # Remove commas and convert
            clean_str = amount_str.replace(',', '')
            return float(clean_str)
        except:
            return None

    def generate_sql_insert(self, data: Dict, table_name: str = 'invoices') -> str:
        """Generate SQL INSERT statement"""
        db_data = self.format_for_database(data)

        # Filter out None values
        fields = []
        values = []

        for key, value in db_data.items():
            if value is not None and key != 'created_at':
                fields.append(key)
                if isinstance(value, str):
                    values.append(f"'{value}'")
                else:
                    values.append(str(value))

        fields_str = ', '.join(fields)
        values_str = ', '.join(values)

        sql = f"INSERT INTO {table_name} ({fields_str}) VALUES ({values_str});"
        return sql


def extract_invoice_from_txt(txt_path: str) -> Dict:
    """Convenience function to extract invoice from TXT file"""
    extractor = InvoiceExtractor()
    return extractor.extract_from_file(txt_path)


def main():
    """CLI for testing invoice extraction"""
    import sys
    import json

    if len(sys.argv) < 2:
        print("Usage: python invoice_extractor.py <txt_file>")
        sys.exit(1)

    txt_file = sys.argv[1]
    extractor = InvoiceExtractor()

    print("="*60)
    print("INVOICE DATA EXTRACTION")
    print("="*60)

    # Extract data
    data = extractor.extract_from_file(txt_file)

    print("\nExtracted Fields:")
    print("-"*60)
    for key, value in data.items():
        if key != 'items' and key != 'raw_text_snippet':
            print(f"{key:20s}: {value}")

    print(f"\nItems found: {len(data['items'])}")
    for i, item in enumerate(data['items'][:5], 1):
        print(f"  Item {i}: {item.get('line', '')[:60]}")

    # Database format
    print("\n" + "="*60)
    print("DATABASE FORMAT")
    print("="*60)
    db_data = extractor.format_for_database(data)
    print(json.dumps(db_data, indent=2, ensure_ascii=False))

    # SQL INSERT
    print("\n" + "="*60)
    print("SQL INSERT STATEMENT")
    print("="*60)
    sql = extractor.generate_sql_insert(data)
    print(sql)

    # Save to JSON
    output_file = Path(txt_file).with_suffix('.invoice.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'extracted_data': data,
            'database_format': db_data,
            'sql_insert': sql,
        }, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Saved to: {output_file}")


if __name__ == '__main__':
    main()
