"""
Text cleaner for OCR results - removes excessive spaces
"""
import re


def clean_ocr_spaces(text: str) -> str:
    """
    Clean excessive spaces from OCR text
    
    Fixes patterns like:
    - "T E L : 0 0 4 4" -> "TEL: 0044"
    - "M I N O R U" -> "MINORU"
    - "R M 1 0 1" -> "RM101"
    
    Args:
        text: OCR text with excessive spaces
        
    Returns:
        Cleaned text
    """
    if not text:
        return text
    
    def merge_chars(match):
        """Remove all spaces from matched group"""
        return match.group(0).replace(' ', '')
    
    # 1. Merge single uppercase letters: "T E L" -> "TEL"
    text = re.sub(r'\b([A-Z])\s+(?:[A-Z]\s+)*[A-Z]\b', merge_chars, text)
    
    # 2. Merge single digits: "5 0 6 5 3 8" -> "506538"
    text = re.sub(r'\b(\d)\s+(?:\d\s+)*\d\b', merge_chars, text)
    
    # 3. Merge letter-number combinations: "RM 1 0 1" -> "RM101"
    text = re.sub(r'\b([A-Z]+)\s+(\d)(?:\s+\d)*\b', merge_chars, text)
    
    # 4. Merge number-letter combinations: "25 T1676" -> "25T1676"
    text = re.sub(r'\b(\d+)\s+([A-Z]\d+)\b', r'\1\2', text)
    
    # 5. Clean punctuation spacing
    text = re.sub(r'\s*:\s*', ': ', text)  # " : " -> ": "
    text = re.sub(r'\s*,\s*', ', ', text)  # " , " -> ", "
    text = re.sub(r'\s*\.\s*', '. ', text)  # " . " -> ". "
    
    # 6. Remove multiple spaces
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()


def clean_ocr_text_line_by_line(text: str) -> str:
    """
    Clean OCR text line by line
    
    Preserves line breaks while cleaning each line
    """
    if not text:
        return text
    
    lines = text.split('\n')
    cleaned_lines = [clean_ocr_spaces(line) for line in lines]
    return '\n'.join(cleaned_lines)


def process_ocr_text(text: str) -> str:
    """Main entry point for OCR text cleaning"""
    return clean_ocr_text_line_by_line(text)
