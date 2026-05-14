"""
Test improved OCR processing
"""
import sys
import io

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from ocr_invoice_reader.utils.text_processor import TextProcessor


def test_text_processing():
    """Test text processing improvements"""
    print("Testing Text Processing Improvements")
    print("=" * 60)

    processor = TextProcessor()

    # Test 1: Split concatenated words
    print("\n1. Splitting concatenated English words:")
    test_cases = [
        "INTERNATIONALEXPRESSWAYBILL",
        "COMPANYNAME",
        "PHONENUMBER",
        "DELIVERYADDRESS",
    ]

    for text in test_cases:
        result = processor.split_concatenated_words(text)
        print(f"   {text}")
        print(f"   → {result}")

    # Test 2: CamelCase spacing
    print("\n2. Adding spaces to CamelCase:")
    test_cases = [
        "CompanyName",
        "PhoneNumber",
        "TrackingNumber123",
    ]

    for text in test_cases:
        result = processor.add_spaces_to_camelcase(text)
        print(f"   {text} → {result}")

    # Test 3: Clean OCR text
    print("\n3. Cleaning OCR text:")
    test_cases = [
        "国 | INTERNATIONALEXPRESSWAYBILL",
        "From Shipper/  发件人",
        "Company  name，address",
    ]

    for text in test_cases:
        result = processor.clean_ocr_text(text)
        print(f"   Before: {text}")
        print(f"   After:  {result}")

    # Test 4: Full processing
    print("\n4. Full OCR result processing:")
    test_cases = [
        "INTERNATIONALEXPRESSWAYBILL",
        "FromShipper/发件人",
        "Customername发件人名Phonenumber发件人电话",
    ]

    for text in test_cases:
        result = processor.process_ocr_result(text, split_words=True)
        print(f"   {text}")
        print(f"   → {result}")

    print("\n" + "=" * 60)
    print("Text Processing Test Complete!")


if __name__ == "__main__":
    test_text_processing()
