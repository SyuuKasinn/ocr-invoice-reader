"""
LLM-based Invoice Data Extractor
Uses structured prompts to extract invoice fields via LLM
"""
import json
import re
from typing import Dict, Optional
from pathlib import Path


class LLMInvoiceExtractor:
    """LLM-based invoice extractor with structured JSON output"""

    def __init__(self, llm_processor=None):
        """
        Initialize with an LLM processor

        Args:
            llm_processor: Instance of LLMDocumentProcessor
        """
        self.llm_processor = llm_processor
        self.extraction_prompt_template = """You are an expert invoice data extraction system. Extract structured data from the following OCR text.

REQUIRED FIELDS (extract if present):
- invoice_number: Invoice/bill number (e.g., "INV-2025-001", "NCY250924", "INVNO NCY250924")
- invoice_date: Date in YYYY-MM-DD format (convert formats like "2025/9/24", "24-Sep-25", "2025-09-24")
- tracking_number: Shipping/air waybill/tracking number (e.g., "820111868365", "506-538-938-065")
- total_amount: Total invoice amount as a decimal number only (e.g., 20.00, 135600, 4000)
- currency: Currency code (USD, JPY, CNY, EUR, GBP, etc.)

OPTIONAL FIELDS (extract if clearly present):
- shipper_name: Sender/shipper company name (clean company name only, no address)
- consignee_name: Receiver/consignee company name (clean company name only, no address)
- shipper_address: Sender's full address
- consignee_address: Receiver's full address
- phone: Phone/telephone number
- fax: Fax number

EXTRACTION RULES:
1. Return ONLY valid JSON format, no explanations or markdown
2. Set missing fields to null
3. Clean extracted values (remove excessive pipes |, extra spaces, region markers)
4. For dates: always convert to YYYY-MM-DD format
5. For amounts: extract only the number (remove currency symbols, commas OK)
6. For company names: extract only the company name, not the entire section with address/phone
7. Look for keywords in multiple languages:
   - Invoice: INVOICE NO, INVNO, 发票号, インボイス番号
   - Date: DATE, 日期, 出口日期
   - Tracking: Tracking No, Air Waybill No, AWB, 运单号码
   - Total: TOTAL, Total Invoice Value, 合计总价, 総額
   - Shipper: SHIPPER, 发货人, FROM
   - Consignee: CONSIGNEE, 收货人, TO, MESSRS

OCR TEXT:
{text}

JSON OUTPUT (respond with only the JSON, no other text):"""

    def extract_from_text(self, text: str) -> Optional[Dict]:
        """
        Extract invoice data from OCR text using LLM

        Args:
            text: OCR extracted text

        Returns:
            Dictionary with extracted fields or None if extraction fails
        """
        if not self.llm_processor:
            return None

        # Clean text before sending to LLM
        cleaned_text = self._clean_text(text)

        # Prepare prompt
        prompt = self.extraction_prompt_template.format(text=cleaned_text)

        # Call LLM
        try:
            response = self.llm_processor._call_ollama(prompt)
            if not response:
                return None

            # Parse JSON response
            result = self._parse_json_response(response)

            if result:
                # Post-process the extracted data
                result = self._post_process(result)

            return result

        except Exception as e:
            print(f"⚠ LLM extraction error: {e}")
            return None

    def _clean_text(self, text: str) -> str:
        """Clean OCR text before sending to LLM"""
        # Remove region markers
        text = re.sub(r'\[Region \d+ - \w+\]', '', text)
        # Normalize pipes
        text = re.sub(r'\s*\|\s*', ' | ', text)
        # Remove page markers
        text = re.sub(r'PAGE \d+\n=+\n', '', text)
        # Limit length to avoid token limits
        if len(text) > 4000:
            text = text[:4000]
        return text.strip()

    def _parse_json_response(self, response: str) -> Optional[Dict]:
        """Parse JSON from LLM response"""
        try:
            # Try direct JSON parse
            return json.loads(response)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(1))
                except:
                    pass

            # Try to find JSON object in text
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(0))
                except:
                    pass

            return None

    def _post_process(self, data: Dict) -> Dict:
        """Post-process extracted data"""
        # Clean string values
        for key, value in data.items():
            if isinstance(value, str):
                # Remove excessive pipes
                value = re.sub(r'\|+', '', value)
                # Remove region markers
                value = re.sub(r'\[Region \d+ - \w+\]', '', value)
                # Normalize whitespace
                value = re.sub(r'\s+', ' ', value).strip()
                data[key] = value if value else None

        # Convert amount to float if it's a string
        if data.get('total_amount'):
            if isinstance(data['total_amount'], str):
                try:
                    # Remove currency symbols and commas
                    amount_str = re.sub(r'[^\d.,]', '', data['total_amount'])
                    amount_str = amount_str.replace(',', '')
                    data['total_amount'] = float(amount_str)
                except:
                    data['total_amount'] = None

        # Validate and normalize date format
        if data.get('invoice_date'):
            normalized_date = self._normalize_date(data['invoice_date'])
            data['invoice_date'] = normalized_date

        return data

    def _normalize_date(self, date_str: str) -> Optional[str]:
        """Normalize date to YYYY-MM-DD format"""
        if not date_str:
            return None

        # Already in correct format
        if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
            return date_str

        # Convert 2025/9/24 to 2025-09-24
        match = re.match(r'^(\d{4})[/-](\d{1,2})[/-](\d{1,2})$', date_str)
        if match:
            year, month, day = match.groups()
            return f"{year}-{int(month):02d}-{int(day):02d}"

        # Convert 24-Sep-25 to 2025-09-24
        match = re.match(r'^(\d{1,2})-([A-Za-z]{3})-(\d{2,4})$', date_str)
        if match:
            day, month_name, year = match.groups()
            month_map = {
                'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04',
                'may': '05', 'jun': '06', 'jul': '07', 'aug': '08',
                'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12'
            }
            month = month_map.get(month_name.lower())
            if month:
                year = f"20{year}" if len(year) == 2 else year
                return f"{year}-{month}-{int(day):02d}"

        return date_str

    def format_for_database(self, data: Dict) -> Dict:
        """Format extracted data for database insertion"""
        return {
            'invoice_number': data.get('invoice_number'),
            'invoice_date': data.get('invoice_date'),
            'tracking_number': data.get('tracking_number'),
            'shipper_name': data.get('shipper_name'),
            'consignee_name': data.get('consignee_name'),
            'company_name': data.get('shipper_name') or data.get('consignee_name'),
            'total_amount': data.get('total_amount'),
            'currency': data.get('currency', 'USD'),
            'phone': data.get('phone'),
            'fax': data.get('fax'),
            'shipper_address': data.get('shipper_address'),
            'consignee_address': data.get('consignee_address'),
        }


def validate_extraction_result(data: Dict) -> tuple[bool, list[str]]:
    """
    Validate LLM extraction result

    Returns:
        (is_valid, list_of_issues)
    """
    issues = []

    if not data:
        return False, ["No data returned"]

    # Check required fields are present (at least one)
    required_fields = ['invoice_number', 'invoice_date', 'tracking_number', 'total_amount']
    has_required = any(data.get(field) for field in required_fields)

    if not has_required:
        issues.append("No required fields extracted")

    # Validate date format
    if data.get('invoice_date'):
        date_val = data['invoice_date']
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', str(date_val)):
            issues.append(f"Invalid date format: {date_val}")

    # Validate amount
    if data.get('total_amount'):
        amount = data['total_amount']
        if not isinstance(amount, (int, float)):
            try:
                float(amount)
            except:
                issues.append(f"Invalid amount: {amount}")

    # Validate currency
    if data.get('currency'):
        currency = data['currency']
        valid_currencies = ['USD', 'JPY', 'CNY', 'EUR', 'GBP', 'AUD', 'CAD', 'CHF', 'HKD', 'SGD']
        if currency not in valid_currencies:
            issues.append(f"Unknown currency: {currency}")

    is_valid = len(issues) == 0
    return is_valid, issues
