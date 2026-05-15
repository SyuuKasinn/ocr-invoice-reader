"""
Enhanced Invoice Data Extractor V2
Handles complex multi-language invoices with better pattern recognition
"""
import re
from typing import Dict, List, Optional, Tuple
from pathlib import Path


class InvoiceExtractorV2:
    """Enhanced invoice extractor with better multi-language support"""

    def __init__(self):
        # Enhanced patterns for better accuracy
        self.patterns = {
            'invoice_no': [
                r'INVOICE\s*NO[.:]?\s*([A-Z0-9-]+)',
                r'INV\s*NO[.:]?\s*([A-Z0-9-]+)',
                r'INVNO[\s|]+([A-Z0-9]+)',
                r'Invoice\s*Number[:\s]+([A-Z0-9-]+)',
                r'发票号[码]?[:\s]+([A-Z0-9-]+)',
            ],
            'date': [
                # ISO format: 2025-09-24
                r'DATE[:\s_]+(\d{4}[-/]\d{1,2}[-/]\d{1,2})',
                # US format: 09/24/2025 or 9/24/25
                r'DATE[:\s_]+(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
                # With underscore: DATE:_2025/9/24
                r'DATE[:：][_\s]*(\d{4}[-/]\d{1,2}[-/]\d{1,2})',
                # Month abbreviation: 24-Sep-25, 01-Jan-2025
                r'DATE[:\s]*(\d{1,2}-[A-Za-z]{3}-\d{2,4})',
                # Piped format: DATE | 2025-9-24
                r'DATE\s*\|\s*(\d{4}[-/]\d{1,2}[-/]\d{1,2})',
                # Japanese style
                r'日期[:\s]+(\d{4}[-/]\d{1,2}[-/]\d{1,2})',
            ],
            'tracking_no': [
                # Piped format first (more specific): Tracking No: | 506-538-938-065
                r'Tracking\s*No[.:]?\s*\|\s*([0-9-]+)',
                r'Tracking\s*No[.:]?\s*([0-9-]+)',
                r'Air\s*Waybill\s*No[.:]?\s*\|\s*([0-9-]+)',
                r'Air\s*Waybill\s*No[.:]?\s*([0-9-]+)',
                r'AWB\s*No[.:]?\s*([0-9-]+)',
                r'追[送]*番号[:\s：]*([A-Z0-9:-]+)',
                r'运单号[:\s]+([0-9-]+)',
                # Generic piped number (last resort)
                r'No[.:]?\s*\|\s*([0-9-]+)',
            ],
            'shipper': [
                r'(?:SHIPPER|发货人)[:\s\|]+([^\n]+(?:CO[.,]?LTD|CORPORATION|INC|LIMITED|株式会社|有限会社))',
                r'(?:FROM|寄件人)[:\s]+([^\n]+)',
            ],
            'consignee': [
                # Match only the company name line, stop at TEL or next section
                r'(?:CONSIGNEE|收货人|收件人)[:\s\|]+([A-Z][A-Z\s&.,]+(?:CO[.,]?LTD|CORPORATION|INC|LIMITED|株式会社|有限会社))(?:\s|$)',
                r'(?:TO|至)[:\s]+([^\n]+?)(?:\s+(?:TEL|Tel|ADDRESS|Address)|\n|$)',
                r'MESSRS[.:\s]+([A-Z][A-Z\s&.,]+(?:CO[.,]?LTD|CORPORATION|INC))(?:\s|$)',
            ],
            'company': [
                # Match company at start of line
                r'^([A-Z][A-Z\s&.,]+(?:CO[.,]?LTD|CORPORATION|INC|LIMITED))',
                # Japanese companies
                r'^([^\n]+(?:株式会社|有限会社|合同会社))',
                # Chinese companies
                r'^([^\n]+(?:有限公司|股份有限公司))',
            ],
            'total_amount': [
                # Piped format: Total | 135600
                r'Total\s*\|\s*([\d,]+\.?\d*)',
                r'Total[:\s]+\$?([\d,]+\.?\d*)',
                r'Total\s*Amount[:\s]+\$?([\d,]+\.?\d*)',
                r'Grand\s*Total[:\s]+\$?([\d,]+\.?\d*)',
                r'合计[:\s]+([\d,]+\.?\d*)',
            ],
            'tel': [
                r'Tel[:\s]+([\d\s+-]+)',
                r'TEL[:\s:]+([\d+-]+)',
                r'电话[:\s]+([\d\s+-]+)',
            ],
            'fax': [
                r'Fax[:\s]+([\d\s+-]+)',
                r'FAX[:\s:]+([\d+-]+)',
                r'传真[:\s]+([\d\s+-]+)',
            ],
        }

    def extract_from_file(self, txt_path: str) -> Dict:
        """Extract invoice data from TXT file"""
        with open(txt_path, 'r', encoding='utf-8') as f:
            text = f.read()
        return self.extract_from_text(text)

    def extract_from_text(self, text: str) -> Dict:
        """Extract invoice data from text content with enhanced logic"""

        # Clean text: remove excessive pipes and spaces
        cleaned_text = self._clean_text(text)

        result = {
            'invoice_no': None,
            'date': None,
            'tracking_no': None,
            'shipper': None,
            'consignee': None,
            'company': None,
            'total_amount': None,
            'currency': 'USD',
            'tel': None,
            'fax': None,
            'items': [],
            'raw_text_snippet': text[:300] if text else None,
        }

        # Extract basic fields with priority order
        for field, patterns in self.patterns.items():
            for pattern in patterns:
                match = re.search(pattern, cleaned_text, re.IGNORECASE | re.MULTILINE)
                if match:
                    value = match.group(1).strip()
                    # Clean up the extracted value
                    value = self._clean_value(value)
                    if value:  # Only set if not empty after cleaning
                        result[field] = value
                        break

        # Smart currency detection
        result['currency'] = self._detect_currency(text)

        # Extract shipper/consignee details
        result['shipper_details'] = self._extract_party_details(text, 'SHIPPER|发货人|FROM')
        result['consignee_details'] = self._extract_party_details(text, 'CONSIGNEE|收货人|TO|MESSRS')

        # Extract line items from tables
        items = self._extract_items(text)
        result['items'] = items
        result['items_count'] = len(items)

        # Use first company found if no shipper/consignee
        if not result['company']:
            result['company'] = result.get('shipper') or result.get('consignee')

        return result

    def _clean_text(self, text: str) -> str:
        """Clean OCR artifacts from text"""
        # Remove excessive pipes used as separators
        text = re.sub(r'\s*\|\s*', ' | ', text)
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        return text

    def _clean_value(self, value: str) -> str:
        """Clean extracted value"""
        # Remove trailing pipes and separators
        value = re.sub(r'[\|]+$', '', value)
        # Remove excessive whitespace
        value = re.sub(r'\s+', ' ', value)
        return value.strip()

    def _detect_currency(self, text: str) -> str:
        """Smart currency detection"""
        # Count currency mentions
        jpy_count = len(re.findall(r'JPY|¥|円', text))
        usd_count = len(re.findall(r'USD|\$', text))
        cny_count = len(re.findall(r'CNY|RMB|元', text))

        if jpy_count > max(usd_count, cny_count):
            return 'JPY'
        elif cny_count > max(usd_count, jpy_count):
            return 'CNY'
        else:
            return 'USD'

    def _extract_party_details(self, text: str, party_keyword: str) -> Dict:
        """Extract shipper or consignee details as a structured block"""
        pattern = rf'(?:{party_keyword})[:\s\|]+(.*?)(?=(?:SHIPPER|CONSIGNEE|收货人|发货人|Tel|TEL|电话)|$)'
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)

        if not match:
            return {}

        party_text = match.group(1).strip()

        # Extract sub-fields
        details = {
            'name': None,
            'address': None,
            'tel': None,
            'fax': None,
        }

        # Extract name (first line usually)
        lines = [l.strip() for l in party_text.split('\n') if l.strip()]
        if lines:
            details['name'] = lines[0]
            # Address is usually the next few lines
            if len(lines) > 1:
                details['address'] = ' '.join(lines[1:3])

        # Extract tel/fax within this block
        tel_match = re.search(r'Tel[:\s]+([\d\s+-]+)', party_text, re.IGNORECASE)
        if tel_match:
            details['tel'] = tel_match.group(1).strip()

        fax_match = re.search(r'Fax[:\s]+([\d\s+-]+)', party_text, re.IGNORECASE)
        if fax_match:
            details['fax'] = fax_match.group(1).strip()

        return details

    def _extract_items(self, text: str) -> List[Dict]:
        """Extract line items from invoice tables"""
        items = []

        # Look for table regions
        table_pattern = r'\[Region \d+ - table\](.*?)(?=\[Region|\Z)'
        tables = re.findall(table_pattern, text, re.DOTALL)

        for table_text in tables:
            lines = table_text.strip().split('\n')

            for line in lines:
                # Skip header lines
                if any(keyword in line.upper() for keyword in
                       ['ITEM NO', 'DESCRIPTION', 'QTY', 'QUANTITY', 'PRICE', 'AMOUNT', 'UNIT']):
                    continue

                # Skip very short lines
                if len(line.strip()) < 5:
                    continue

                # Try to extract structured data
                parts = [p.strip() for p in line.split('|') if p.strip()]

                if len(parts) >= 2:
                    # Extract all numeric values
                    numbers = re.findall(r'[\d,]+\.?\d*', line)

                    if numbers:
                        item = {
                            'line': line.strip(),
                            'parts': parts,
                            'numbers': numbers,
                        }

                        # Try to identify quantity and amount
                        # Usually: last number = amount, second to last = quantity or unit price
                        if len(numbers) >= 2:
                            item['quantity'] = numbers[-2].replace(',', '')
                            item['amount'] = numbers[-1].replace(',', '')
                        elif len(numbers) == 1:
                            item['amount'] = numbers[0].replace(',', '')

                        items.append(item)

        return items

    def format_for_database(self, data: Dict) -> Dict:
        """Format extracted data for database insertion"""
        db_data = {
            'invoice_number': data.get('invoice_no'),
            'invoice_date': data.get('date'),
            'tracking_number': data.get('tracking_no'),
            'shipper_name': data.get('shipper'),
            'consignee_name': data.get('consignee'),
            'company_name': data.get('company'),
            'total_amount': self._parse_amount(data.get('total_amount')),
            'currency': data.get('currency', 'USD'),
            'phone': data.get('tel'),
            'fax': data.get('fax'),
            'item_count': data.get('items_count', 0),
            'created_at': None,
        }

        # Add detailed party info if available
        if data.get('shipper_details'):
            db_data['shipper_address'] = data['shipper_details'].get('address')
            db_data['shipper_tel'] = data['shipper_details'].get('tel')

        if data.get('consignee_details'):
            db_data['consignee_address'] = data['consignee_details'].get('address')
            db_data['consignee_tel'] = data['consignee_details'].get('tel')

        return db_data

    def _parse_amount(self, amount_str: Optional[str]) -> Optional[float]:
        """Parse amount string to float"""
        if not amount_str:
            return None
        try:
            clean_str = amount_str.replace(',', '').replace(' ', '')
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
                    # Escape single quotes
                    value = value.replace("'", "''")
                    values.append(f"'{value}'")
                else:
                    values.append(str(value))

        if not fields:
            return "-- No data to insert"

        fields_str = ', '.join(fields)
        values_str = ', '.join(values)

        sql = f"INSERT INTO {table_name} ({fields_str}) VALUES ({values_str});"
        return sql


def extract_invoice_from_txt(txt_path: str) -> Dict:
    """Convenience function to extract invoice from TXT file"""
    extractor = InvoiceExtractorV2()
    return extractor.extract_from_file(txt_path)
