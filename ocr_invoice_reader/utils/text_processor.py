"""
Text post-processing utilities
"""
import re
from typing import List


class TextProcessor:
    """Text post-processing for OCR results"""

    # Common English words that help identify word boundaries
    COMMON_WORDS = {
        'express', 'waybill', 'international', 'shipper', 'consignee',
        'from', 'delivery', 'account', 'number', 'customer', 'name',
        'phone', 'company', 'address', 'contact', 'person', 'code',
        'weight', 'height', 'width', 'length', 'package', 'cargo',
        'declared', 'value', 'description', 'content', 'invoice',
        'date', 'total', 'amount', 'freight', 'payment', 'term',
        'port', 'loading', 'discharge', 'vessel', 'shipping'
    }

    @staticmethod
    def split_concatenated_words(text: str) -> str:
        """
        Split concatenated English words using pattern matching

        Example: "INTERNATIONALEXPRESSWAYBILL" -> "INTERNATIONAL EXPRESS WAYBILL"
        """
        if not text:
            return text

        # Only process if text is all uppercase and no spaces
        if not (text.isupper() and ' ' not in text and len(text) > 10):
            return text

        # Try to find word boundaries
        words_found = []
        remaining = text.lower()
        position = 0

        while remaining:
            # Try to match longest common word first
            matched = False
            for length in range(min(len(remaining), 15), 2, -1):
                candidate = remaining[:length]
                if candidate in TextProcessor.COMMON_WORDS:
                    words_found.append(text[position:position + length])
                    remaining = remaining[length:]
                    position += length
                    matched = True
                    break

            if not matched:
                # Check for pattern: capital letter followed by lowercase
                # e.g., "WayBill" -> "Way Bill"
                if len(remaining) > 1:
                    # Add single character and continue
                    words_found.append(text[position])
                    remaining = remaining[1:]
                    position += 1
                else:
                    words_found.append(text[position:])
                    break

        if len(words_found) > 1:
            return ' '.join(words_found)
        return text

    @staticmethod
    def add_spaces_to_camelcase(text: str) -> str:
        """
        Add spaces to CamelCase text

        Example: "CompanyName" -> "Company Name"
        """
        # Insert space before capital letters that follow lowercase
        text = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', text)
        # Insert space before capital letters that follow numbers
        text = re.sub(r'(?<=[0-9])(?=[A-Z])', ' ', text)
        return text

    @staticmethod
    def clean_ocr_text(text: str) -> str:
        """
        Clean up common OCR errors

        - Remove extra spaces
        - Fix common character substitutions
        - Normalize punctuation
        """
        if not text:
            return text

        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)

        # Fix common OCR mistakes
        replacements = {
            '|': ' | ',  # Ensure pipe has spaces
            '  |  ': ' | ',  # Normalize pipe spacing
            '，': ',',  # Chinese comma to English
            '。': '.',  # Chinese period to English
            '：': ':',  # Chinese colon to English
        }

        for old, new in replacements.items():
            text = text.replace(old, new)

        # Remove leading/trailing spaces
        text = text.strip()

        return text

    @staticmethod
    def process_ocr_result(text: str, split_words: bool = True) -> str:
        """
        Main processing pipeline for OCR text

        Args:
            text: Raw OCR text
            split_words: Whether to attempt word splitting

        Returns:
            Processed text
        """
        if not text:
            return text

        # Clean basic issues
        text = TextProcessor.clean_ocr_text(text)

        # Split concatenated words if enabled
        if split_words:
            # Process each word separately
            words = text.split()
            processed_words = []
            for word in words:
                if word.isupper() and len(word) > 10:
                    processed = TextProcessor.split_concatenated_words(word)
                    processed_words.append(processed)
                else:
                    # Add spaces to CamelCase
                    processed = TextProcessor.add_spaces_to_camelcase(word)
                    processed_words.append(processed)
            text = ' '.join(processed_words)

        return text

    @staticmethod
    def normalize_table_text(text: str) -> str:
        """
        Normalize text for table cells

        - Ensure consistent spacing around separators
        - Remove extra whitespace
        """
        if not text:
            return text

        # Normalize pipe separators
        text = re.sub(r'\s*\|\s*', ' | ', text)

        # Remove extra spaces
        text = re.sub(r'\s+', ' ', text)

        return text.strip()


def process_region_text(text: str, region_type: str = 'text') -> str:
    """
    Process text based on region type

    Args:
        text: Raw text
        region_type: Type of region (title, text, table, etc.)

    Returns:
        Processed text
    """
    processor = TextProcessor()

    if region_type == 'table':
        return processor.normalize_table_text(text)
    else:
        return processor.process_ocr_result(text, split_words=True)
