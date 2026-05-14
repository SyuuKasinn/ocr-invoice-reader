"""
Quick test for new CSV export features
"""
import sys
import io

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from ocr_invoice_reader.models.base import BaseDocument, DocumentItem, Address


def test_csv_export():
    """Test CSV export functionality"""
    print("Testing CSV Export Features...")
    print("=" * 60)

    # Create a test document
    doc = BaseDocument(
        document_type="invoice",
        document_number="TEST-001",
        date="2024-05-14",
        sender=Address(
            company="Test Company Inc",
            address="123 Test Street",
            phone="555-1234"
        ),
        receiver=Address(
            company="Customer Corp",
            address="456 Customer Ave",
            phone="555-5678"
        ),
        items=[
            DocumentItem(
                description="Product A",
                quantity=10,
                unit="pcs",
                unit_price=100.0,
                amount=1000.0
            ),
            DocumentItem(
                description="Product B",
                quantity=5,
                unit="pcs",
                unit_price=200.0,
                amount=1000.0
            )
        ],
        total_amount=2000.0,
        currency="JPY",
        confidence=0.95,
        extraction_method="test"
    )

    # Test CSV row conversion
    print("\n1. Testing to_csv_row()...")
    row = doc.to_csv_row()
    print(f"   ✓ Converted to CSV row with {len(row)} fields")
    print(f"   ✓ Document number: {row['document_number']}")
    print(f"   ✓ Total amount: {row['total_amount']}")

    # Test CSV items conversion
    print("\n2. Testing to_csv_items()...")
    items = doc.to_csv_items()
    print(f"   ✓ Converted to {len(items)} item rows")
    for idx, item in enumerate(items, 1):
        print(f"   ✓ Item {idx}: {item['description']} - {item['amount']}")

    # Test saving to CSV
    print("\n3. Testing save_to_csv()...")
    try:
        doc.save_to_csv('test_output/summary.csv', mode='summary')
        print(f"   ✓ Summary CSV saved successfully")

        doc.save_to_csv('test_output/items.csv', mode='items')
        print(f"   ✓ Items CSV saved successfully")
    except Exception as e:
        print(f"   ✗ Error: {e}")

    # Test multiple documents
    print("\n4. Testing save_multiple_to_csv()...")
    doc2 = BaseDocument(
        document_number="TEST-002",
        total_amount=3000.0,
        confidence=0.90
    )

    try:
        BaseDocument.save_multiple_to_csv(
            [doc, doc2],
            'test_output/batch.csv',
            mode='summary'
        )
        print(f"   ✓ Batch CSV saved successfully")
    except Exception as e:
        print(f"   ✗ Error: {e}")

    print("\n" + "=" * 60)
    print("CSV Export Test Complete!")
    print("\nCheck test_output/ directory for generated CSV files")


if __name__ == "__main__":
    test_csv_export()
