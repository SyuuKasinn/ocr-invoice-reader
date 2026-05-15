"""
LLM-based Invoice Data Extractor for GLOVIA Invoice突合
Based on specification: 機能概要_2-1-5_ Invoice突合.xlsx
"""
import json
import re
from typing import Dict, Optional
from pathlib import Path


class GLOVIAInvoiceExtractor:
    """
    LLM-based invoice extractor optimized for GLOVIA Invoice突合機能
    Extracts structured data for customs clearance (通関) processing
    """

    def __init__(self, llm_processor=None):
        """
        Initialize with an LLM processor

        Args:
            llm_processor: Instance of LLMDocumentProcessor
        """
        self.llm_processor = llm_processor

        # GLOVIA-optimized prompt based on Invoice突合 specification
        self.glovia_extraction_prompt = """You are an expert COMMERCIAL INVOICE analysis system for Japanese customs clearance (通関).
Extract structured data for GLOVIA Invoice突合機能.

Return JSON with this EXACT structure:
{{
  "document_type": "invoice",
  "confidence": "high",
  "invoice_data": {{
    "basic_info": {{
      "invoice_number": "...",
      "invoice_date": "YYYY-MM-DD",
      "hawb_number": "...",
      "mawb_number": "..."
    }},
    "shipper": {{
      "name": "...",
      "address": "..."
    }},
    "consignee": {{
      "name": "...",
      "tel": "...",
      "address_zip": "...",
      "address": "..."
    }},
    "importer": {{
      "company_number": "...",
      "name": "...",
      "tel": "...",
      "address_zip": "...",
      "address": "..."
    }},
    "delivery": {{
      "name": "...",
      "address": "..."
    }},
    "tax_info": {{
      "invoice_value": 0.00,
      "freight": 0.00,
      "insurance": 0.00,
      "customs_duty": 0.00,
      "consumption_tax": 0.00,
      "local_consumption_tax": 0.00,
      "taxable_value": 0.00,
      "currency": "USD"
    }},
    "cargo_info": {{
      "pieces": 0,
      "weight_kg": 0.0,
      "description": "..."
    }},
    "items": [
      {{
        "hs_code": "...",
        "description": "...",
        "quantity1": 0,
        "quantity2": 0
      }}
    ]
  }}
}}

CRITICAL EXTRACTION RULES (基于 Invoice突合 規格書):

1. **SHIPPER (発貨人・荷送人)**
   Keywords: SHIPPER, FROM, 発貨人, 荷送人, CORP NAME (in shipper section)
   - name: Company name ONLY (stop at ADDRESS/Tel/地址)
     Example: "DALIAN LONG SHENG WOOD INDUSTRY CO.LTD"
   - address: Full address (all lines after company name)
     Example: "AGENCY DALIAN CHINA ZHANG JIA YAOSTR.TAI PING"

2. **CONSIGNEE (収貨人・荷受人)**
   Keywords: CONSIGNEE, TO, MESSRS, 収貨人, 荷受人, 一株式会社
   - name: Company name ONLY (stop at TEL/ADDRESS/電話)
     Example: "MINORU SANGYO CORPORATION" or "株式会社 SHINJUKU"
   - tel: Phone number (CRITICAL for importer matching)
     Example: "03-3352-7152" or "0081-03-3661-1363"
   - address_zip: Postal code (e.g., "160-0022", "T566-00352")
   - address: Full address after ZIP
     Example: "2-10-12 TSURUNO.SETTSU,OSAKA,JAPAN"

3. **IMPORTER (輸入者)**
   Usually same as CONSIGNEE (copy consignee data if no separate importer)
   - company_number: 法人番号 (Corporate Number) if present
   - name: Company name
   - tel: CRITICAL field (used for duplicate importer detection in GLOVIA)
   - address_zip: Postal code
   - address: Full address

4. **DELIVERY (運送場所)**
   May be same as CONSIGNEE or different delivery location
   Keywords: DELIVERY, DESTINATION, 運送場所
   - name: Delivery location name
   - address: Delivery address

5. **TAX INFO (課税価格・税金)**
   - invoice_value (仕入書価格): TOTAL INVOICE VALUE, 合計総価, Total
     Example: Extract "20.00" from "USD20.00", "135600" from "Total | 135600"
   - freight (FREIGHT): Shipping/freight charges
   - insurance (保険): Insurance cost if shown
   - customs_duty (関税): Customs duty if calculated
   - consumption_tax (消費税): Consumption tax if calculated
   - local_consumption_tax (地方消費税): Local consumption tax if calculated
   - taxable_value (課税価格): Total taxable value if calculated
   - currency: USD, JPY, CNY, EUR, GBP

6. **CARGO INFO (貨物情報)**
   - pieces (PCS): Number of packages/pieces
     Example: Extract "1" from "1 | USD20.00", "10" from "PCS: 10"
   - weight_kg (重量): Weight in kilograms
     Example: "25.5" from "Weight: 25.5kg"
   - description (品名): Item description
     Example: "WOODEN FLOOR BOARD SAMPLE"

7. **ITEMS (品目リスト)**
   Extract each line item with:
   - hs_code (HSコード): Harmonized System code (e.g., "9403.60")
   - description (品名): Item name/description
   - quantity1 (数量1): Primary quantity
   - quantity2 (数量2): Secondary quantity (0 if not present)

8. **TRACKING NUMBERS**
   - hawb_number (HAWB番号): House Air Waybill
     Keywords: "Tracking No", "LDX:", after pipe "|"
     Example: Extract "506-538-938-065" from "Tracking No: | 506-538-938-065"
   - mawb_number (MAWB番号): Master Air Waybill
     Keywords: "AIR WAYBILL NO", "AWB", "運単号碼: |"
     Example: Extract "820111868365" from "運単号碼: | 820111868365"
     Example: Extract "324-04787403" from "AIR WAYBILLNO.2406460365245"

9. **DATE FORMAT**
   Convert ALL dates to YYYY-MM-DD:
   - "2025/9/24" → "2025-09-24"
   - "24-Sep-25" → "2025-09-24"
   - "DATE | 2025-9-24" → "2025-09-24"

10. **MULTI-LANGUAGE SUPPORT**
    - English: INVOICE, SHIPPER, CONSIGNEE, TOTAL, Tel, Address
    - Chinese: 発票, 発貨人, 収貨人, 合計総価, 電話, 地址
    - Japanese: インボイス, 荷送人, 荷受人, 総額, 電話番号, 住所

EXTRACTION PRIORITIES:
1. TEL field is MOST CRITICAL (複数輸入者検出のキー)
2. MAWB/HAWB numbers (PDF保存とリンクに使用)
3. Invoice value and freight (課税価格計算)
4. Shipper/Consignee names and addresses (通関書類作成)
5. Item details (品目申告)

CLEANING RULES:
- Remove [Region X - type] markers
- Remove excessive pipes (|||)
- Separate company name from address/tel
- Extract ZIP code from address
- Remove "ZIP:", "Tel:", "ADDRESS:" prefixes
- Clean phone numbers: keep format like "03-3352-7152"

IMPORTANT NOTES:
- If IMPORTER not explicitly shown, copy CONSIGNEE data to IMPORTER
- If DELIVERY not explicitly shown, copy CONSIGNEE data to DELIVERY
- Return null for truly missing fields, but 0 for numeric fields
- Return empty array [] for items if no item details found
- Return ONLY valid JSON, no explanations or markdown

OCR TEXT:
{text}

JSON OUTPUT:"""

    def extract_from_text(self, text: str) -> Optional[Dict]:
        """
        Extract GLOVIA-format invoice data from OCR text

        Args:
            text: OCR extracted text

        Returns:
            Dictionary with GLOVIA-structured invoice data
        """
        if not self.llm_processor:
            return None

        # Clean text
        cleaned_text = self._clean_text(text)

        # Prepare prompt
        prompt = self.glovia_extraction_prompt.format(text=cleaned_text)

        # Call LLM
        try:
            response = self.llm_processor._generate(prompt, temperature=0.3)
            if not response:
                return None

            # Parse JSON response
            result = self._parse_json_response(response)

            if result and result.get('invoice_data'):
                # Post-process the data
                result['invoice_data'] = self._post_process_glovia(result['invoice_data'])

            return result

        except Exception as e:
            print(f"⚠ GLOVIA LLM extraction error: {e}")
            return None

    def _clean_text(self, text: str) -> str:
        """Clean OCR text before sending to LLM"""
        # Remove region markers
        text = re.sub(r'\[Region \d+ - \w+\]', '', text)
        # Normalize pipes
        text = re.sub(r'\s*\|\s*', ' | ', text)
        # Remove page markers
        text = re.sub(r'PAGE \d+\n=+\n', '', text)
        # Limit length
        if len(text) > 4000:
            text = text[:4000]
        return text.strip()

    def _parse_json_response(self, response: str) -> Optional[Dict]:
        """Parse JSON from LLM response"""
        try:
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

    def _post_process_glovia(self, data: Dict) -> Dict:
        """Post-process GLOVIA invoice data"""
        # Normalize date in basic_info
        if data.get('basic_info', {}).get('invoice_date'):
            data['basic_info']['invoice_date'] = self._normalize_date(
                data['basic_info']['invoice_date']
            )

        # Ensure importer has data (copy from consignee if empty)
        if not data.get('importer', {}).get('name'):
            if data.get('consignee', {}).get('name'):
                data['importer'] = data['consignee'].copy()

        # Ensure delivery has data (copy from consignee if empty)
        if not data.get('delivery', {}).get('name'):
            if data.get('consignee', {}).get('name'):
                data['delivery'] = {
                    'name': data['consignee'].get('name'),
                    'address': data['consignee'].get('address')
                }

        # Clean string values
        for section in ['shipper', 'consignee', 'importer', 'delivery']:
            if section in data:
                for key, value in data[section].items():
                    if isinstance(value, str):
                        data[section][key] = self._clean_value(value)

        # Ensure numeric fields in tax_info
        if 'tax_info' in data:
            for key in ['invoice_value', 'freight', 'insurance', 'customs_duty',
                       'consumption_tax', 'local_consumption_tax', 'taxable_value']:
                if key in data['tax_info']:
                    value = data['tax_info'][key]
                    if isinstance(value, str):
                        try:
                            cleaned = re.sub(r'[^\d.]', '', value)
                            data['tax_info'][key] = float(cleaned) if cleaned else 0.0
                        except:
                            data['tax_info'][key] = 0.0
                    elif value is None:
                        data['tax_info'][key] = 0.0

        # Ensure numeric fields in cargo_info
        if 'cargo_info' in data:
            if isinstance(data['cargo_info'].get('pieces'), str):
                try:
                    data['cargo_info']['pieces'] = int(data['cargo_info']['pieces'])
                except:
                    data['cargo_info']['pieces'] = 0

            if isinstance(data['cargo_info'].get('weight_kg'), str):
                try:
                    cleaned = re.sub(r'[^\d.]', '', data['cargo_info']['weight_kg'])
                    data['cargo_info']['weight_kg'] = float(cleaned) if cleaned else 0.0
                except:
                    data['cargo_info']['weight_kg'] = 0.0

        return data

    def _clean_value(self, value: str) -> str:
        """Clean extracted string value"""
        # Remove excessive pipes
        value = re.sub(r'\|+', '', value)
        # Remove region markers
        value = re.sub(r'\[Region \d+ - \w+\]', '', value)
        # Normalize whitespace
        value = re.sub(r'\s+', ' ', value).strip()
        return value if value else None

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

    def format_for_glovia_db(self, data: Dict) -> Dict:
        """Format extracted data for GLOVIA database insertion"""
        invoice_data = data.get('invoice_data', {})

        return {
            # Basic info
            'invoice_number': invoice_data.get('basic_info', {}).get('invoice_number'),
            'invoice_date': invoice_data.get('basic_info', {}).get('invoice_date'),
            'hawb_number': invoice_data.get('basic_info', {}).get('hawb_number'),
            'mawb_number': invoice_data.get('basic_info', {}).get('mawb_number'),

            # Shipper
            'shipper_name': invoice_data.get('shipper', {}).get('name'),
            'shipper_address': invoice_data.get('shipper', {}).get('address'),

            # Consignee
            'consignee_name': invoice_data.get('consignee', {}).get('name'),
            'consignee_tel': invoice_data.get('consignee', {}).get('tel'),
            'consignee_zip': invoice_data.get('consignee', {}).get('address_zip'),
            'consignee_address': invoice_data.get('consignee', {}).get('address'),

            # Importer
            'importer_company_number': invoice_data.get('importer', {}).get('company_number'),
            'importer_name': invoice_data.get('importer', {}).get('name'),
            'importer_tel': invoice_data.get('importer', {}).get('tel'),
            'importer_zip': invoice_data.get('importer', {}).get('address_zip'),
            'importer_address': invoice_data.get('importer', {}).get('address'),

            # Delivery
            'delivery_name': invoice_data.get('delivery', {}).get('name'),
            'delivery_address': invoice_data.get('delivery', {}).get('address'),

            # Tax info
            'invoice_value': invoice_data.get('tax_info', {}).get('invoice_value'),
            'freight': invoice_data.get('tax_info', {}).get('freight'),
            'insurance': invoice_data.get('tax_info', {}).get('insurance'),
            'customs_duty': invoice_data.get('tax_info', {}).get('customs_duty'),
            'consumption_tax': invoice_data.get('tax_info', {}).get('consumption_tax'),
            'local_consumption_tax': invoice_data.get('tax_info', {}).get('local_consumption_tax'),
            'taxable_value': invoice_data.get('tax_info', {}).get('taxable_value'),
            'currency': invoice_data.get('tax_info', {}).get('currency', 'USD'),

            # Cargo info
            'pieces': invoice_data.get('cargo_info', {}).get('pieces'),
            'weight_kg': invoice_data.get('cargo_info', {}).get('weight_kg'),
            'description': invoice_data.get('cargo_info', {}).get('description'),

            # Items
            'items': invoice_data.get('items', []),
            'items_count': len(invoice_data.get('items', [])),
        }


def validate_glovia_extraction(data: Dict) -> tuple[bool, list[str]]:
    """
    Validate GLOVIA invoice extraction result

    Returns:
        (is_valid, list_of_issues)
    """
    issues = []

    if not data:
        return False, ["No data returned"]

    invoice_data = data.get('invoice_data', {})
    if not invoice_data:
        return False, ["No invoice_data field"]

    # Check critical fields for GLOVIA
    basic_info = invoice_data.get('basic_info', {})
    if not basic_info.get('invoice_date'):
        issues.append("Missing invoice_date")
    if not basic_info.get('mawb_number') and not basic_info.get('hawb_number'):
        issues.append("Missing both MAWB and HAWB numbers")

    # Check importer TEL (critical for matching)
    importer = invoice_data.get('importer', {})
    if not importer.get('tel'):
        issues.append("Missing importer TEL (required for matching)")

    # Check tax info
    tax_info = invoice_data.get('tax_info', {})
    if not tax_info.get('invoice_value'):
        issues.append("Missing invoice_value")
    if not tax_info.get('currency'):
        issues.append("Missing currency")

    is_valid = len(issues) == 0
    return is_valid, issues
