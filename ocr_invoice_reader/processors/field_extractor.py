"""
Field extractor: Extract structured fields from OCR text using rules
"""
import re
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from ocr_invoice_reader.models.base import BaseDocument, Address, DocumentItem


class FieldExtractor:
    """Rule-based field extractor"""

    def __init__(self):
        """Initialize field extractor with patterns"""

        # Document type patterns
        self.doc_type_patterns = {
            'invoice': r'(?i)\b(invoice|請求書|发票|インボイス)\b',
            'waybill': r'(?i)\b(waybill|运单|送り状|express|配送|delivery)\b',
            'contract': r'(?i)\b(contract|契約|合同)\b',
            'receipt': r'(?i)\b(receipt|領収書|收據)\b',
            'order': r'(?i)\b(order|注文|订单|purchase)\b',
        }

        # Document number patterns
        self.doc_number_patterns = [
            r'(?:invoice|waybill|tracking|order)[:\s#]*([A-Z0-9\-]+)',
            r'(?:No\.|NO\.|番号|编号)[:\s]*([A-Z0-9\-]+)',
            r'\b([A-Z]{2,4}\s*\d{6,})\b',  # HTL 506539397733
            r'\b([A-Z]+\d{8,})\b',  # HTL506539397733
        ]

        # Date patterns
        self.date_patterns = [
            r'(\d{4})[-/年](\d{1,2})[-/月](\d{1,2})',  # 2026-05-12, 2026年5月12日
            r'(\d{1,2})[-/](\d{1,2})[-/](\d{4})',      # 12-05-2026
            r'(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{4})',  # 12 May 2026
        ]

        # Amount patterns
        self.amount_patterns = [
            r'(?:total|合計|total amount|金額|总额)[:\s¥$€£]*([0-9,]+\.?\d*)',
            r'(?:amount|金额)[:\s¥$€£]*([0-9,]+\.?\d*)',
            r'¥\s*([0-9,]+\.?\d*)',
            r'\$\s*([0-9,]+\.?\d*)',
        ]

        # Currency patterns
        self.currency_patterns = {
            'JPY': r'(?:¥|JPY|円|日元)',
            'USD': r'(?:\$|USD|美元|dollar)',
            'CNY': r'(?:CNY|RMB|元|人民币)',
            'EUR': r'(?:€|EUR|欧元|euro)',
        }

        # Phone patterns
        self.phone_patterns = [
            r'(?:tel|phone|電話|电话)[:\s]*([0-9\-\(\)\+\s]{8,})',
            r'\b(\+?\d{1,3}[-\.\s]?\(?\d{2,4}\)?[-\.\s]?\d{3,4}[-\.\s]?\d{3,4})\b',
        ]

        # Email patterns
        self.email_pattern = r'\b([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b'

        # Company name indicators
        self.company_indicators = [
            r'CO\.,?\s*LTD',
            r'COMPANY',
            r'CORP',
            r'INC',
            r'株式会社',
            r'有限会社',
            r'公司',
            r'企业',
        ]

    def extract(self, text: str, regions: List[Any] = None, source_file: str = None) -> BaseDocument:
        """
        Extract structured fields from text

        Args:
            text: Full text content
            regions: Layout regions (optional)
            source_file: Source file path

        Returns:
            BaseDocument with extracted fields
        """
        doc = BaseDocument(source_file=source_file)

        # Extract document type
        doc.document_type = self._extract_document_type(text)

        # Extract document number
        doc.document_number = self._extract_document_number(text)

        # Extract date
        doc.date = self._extract_date(text)

        # Extract addresses
        sender, receiver = self._extract_addresses(text, regions)
        doc.sender = sender
        doc.receiver = receiver

        # Extract amounts
        doc.total_amount = self._extract_total_amount(text)
        doc.currency = self._extract_currency(text)

        # Extract items (if table regions available)
        if regions:
            doc.items = self._extract_items_from_regions(regions)

        # Calculate confidence
        doc.confidence = self._calculate_confidence(doc)
        doc.extraction_method = "rule_based"
        doc.extraction_timestamp = datetime.now().isoformat()

        return doc

    def _extract_document_type(self, text: str) -> str:
        """Extract document type"""
        text_lower = text.lower()

        for doc_type, pattern in self.doc_type_patterns.items():
            if re.search(pattern, text_lower):
                return doc_type

        return "unknown"

    def _extract_document_number(self, text: str) -> Optional[str]:
        """Extract document number"""
        text_clean = text.replace('\n', ' ')

        for pattern in self.doc_number_patterns:
            match = re.search(pattern, text_clean, re.IGNORECASE)
            if match:
                number = match.group(1)
                # Clean up
                number = number.strip().replace(' ', '')
                # Validate (at least 5 chars)
                if len(number) >= 5:
                    return number

        return None

    def _extract_date(self, text: str) -> Optional[str]:
        """Extract date in YYYY-MM-DD format"""
        for pattern in self.date_patterns:
            match = re.search(pattern, text)
            if match:
                groups = match.groups()

                try:
                    # Different formats
                    if len(groups) == 3:
                        if len(groups[0]) == 4:  # YYYY-MM-DD
                            year, month, day = groups
                        elif len(groups[2]) == 4:  # DD-MM-YYYY
                            day, month, year = groups
                        else:  # Month name format
                            day = groups[0]
                            month_name = groups[1]
                            year = groups[2]
                            month_map = {
                                'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
                                'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
                                'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
                            }
                            month = month_map.get(month_name[:3], '01')

                        # Format as YYYY-MM-DD
                        return f"{year}-{int(month):02d}-{int(day):02d}"

                except (ValueError, IndexError):
                    continue

        return None

    def _extract_total_amount(self, text: str) -> Optional[float]:
        """Extract total amount"""
        for pattern in self.amount_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_str = match.group(1)
                # Clean up
                amount_str = amount_str.replace(',', '').strip()
                try:
                    return float(amount_str)
                except ValueError:
                    continue

        return None

    def _extract_currency(self, text: str) -> str:
        """Extract currency"""
        for currency, pattern in self.currency_patterns.items():
            if re.search(pattern, text):
                return currency

        # Default
        return "JPY"

    def _extract_addresses(self, text: str, regions: List[Any] = None) -> Tuple[Optional[Address], Optional[Address]]:
        """Extract sender and receiver addresses"""

        # Keywords for sender/receiver
        sender_keywords = [
            r'(?i)\b(from|sender|shipper|差出人|发件人|送り主)',
            r'(?i)\b(consignor)',
        ]

        receiver_keywords = [
            r'(?i)\b(to|receiver|consignee|宛先|收件人|届け先)',
            r'(?i)\b(delivery\s+to|ship\s+to)',
        ]

        # Split text into lines
        lines = text.split('\n')

        sender = Address()
        receiver = Address()

        # Try to find sender/receiver sections
        sender_section = []
        receiver_section = []
        current_section = None

        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                continue

            # Check for section markers
            is_sender = any(re.search(kw, line_stripped) for kw in sender_keywords)
            is_receiver = any(re.search(kw, line_stripped) for kw in receiver_keywords)

            if is_sender:
                current_section = 'sender'
                continue
            elif is_receiver:
                current_section = 'receiver'
                continue

            # Add to current section
            if current_section == 'sender':
                sender_section.append(line_stripped)
            elif current_section == 'receiver':
                receiver_section.append(line_stripped)

        # Extract from sections
        if sender_section:
            sender = self._parse_address_section(sender_section)

        if receiver_section:
            receiver = self._parse_address_section(receiver_section)

        return sender, receiver

    def _parse_address_section(self, lines: List[str]) -> Address:
        """Parse address from lines"""
        address = Address()

        # Extract company (lines with company indicators)
        for line in lines:
            if any(ind in line.upper() for ind in ['CO.', 'LTD', 'COMPANY', 'CORP', 'INC', '株式会社', '有限会社', '公司']):
                if not address.company:
                    address.company = line
                    break

        # Extract phone
        for line in lines:
            for pattern in self.phone_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    address.phone = match.group(1).strip()
                    break
            if address.phone:
                break

        # Extract email
        email_text = ' '.join(lines)
        match = re.search(self.email_pattern, email_text)
        if match:
            address.email = match.group(1)

        # Combine remaining lines as address
        address_lines = [
            line for line in lines
            if line != address.company and (not address.phone or address.phone not in line)
        ]

        if address_lines:
            address.address = ', '.join(address_lines[:3])  # Max 3 lines

        return address

    def _extract_items_from_regions(self, regions: List[Any]) -> List[DocumentItem]:
        """Extract items from table regions"""
        items = []

        # Find table regions
        table_regions = [r for r in regions if hasattr(r, 'type') and r.type == 'table']

        for region in table_regions:
            # Try to parse table_html or text
            if hasattr(region, 'table_html') and region.table_html:
                items.extend(self._parse_table_html(region.table_html))
            elif hasattr(region, 'text') and region.text:
                items.extend(self._parse_table_text(region.text))

        return items

    def _parse_table_html(self, html: str) -> List[DocumentItem]:
        """Parse items from HTML table"""
        items = []

        # Simple HTML parsing (could use BeautifulSoup for better results)
        rows = re.findall(r'<tr>(.*?)</tr>', html, re.DOTALL)

        for row in rows[1:]:  # Skip header
            cells = re.findall(r'<td>(.*?)</td>', row)
            cells = [re.sub(r'<[^>]+>', '', cell).strip() for cell in cells]

            if len(cells) >= 2:
                item = DocumentItem(description=cells[0])

                # Try to parse quantity, price, amount
                if len(cells) >= 3:
                    try:
                        item.quantity = float(cells[1].replace(',', ''))
                    except:
                        pass

                if len(cells) >= 4:
                    try:
                        item.unit_price = float(cells[2].replace(',', ''))
                    except:
                        pass

                if len(cells) >= 5:
                    try:
                        item.amount = float(cells[3].replace(',', ''))
                    except:
                        pass

                items.append(item)

        return items

    def _parse_table_text(self, text: str) -> List[DocumentItem]:
        """Parse items from table text"""
        items = []

        lines = text.split('\n')
        for line in lines:
            # Simple heuristic: line with numbers might be an item
            if re.search(r'\d+', line):
                item = DocumentItem(description=line[:50])  # First 50 chars
                items.append(item)

        return items

    def _calculate_confidence(self, doc: BaseDocument) -> float:
        """Calculate extraction confidence"""
        score = 0.0
        total = 0.0

        # Document number (20%)
        total += 0.2
        if doc.document_number:
            score += 0.2

        # Date (15%)
        total += 0.15
        if doc.date:
            score += 0.15

        # Sender (20%)
        total += 0.2
        if doc.sender and not doc.sender.is_empty():
            score += 0.1
            if doc.sender.company:
                score += 0.1

        # Receiver (20%)
        total += 0.2
        if doc.receiver and not doc.receiver.is_empty():
            score += 0.1
            if doc.receiver.company:
                score += 0.1

        # Amount (15%)
        total += 0.15
        if doc.total_amount:
            score += 0.15

        # Items (10%)
        total += 0.1
        if doc.items:
            score += 0.1

        return score / total if total > 0 else 0.0
