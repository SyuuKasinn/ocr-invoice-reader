"""
Tests for CSV export functionality
"""
import pytest
from pathlib import Path
import tempfile
import csv
from ocr_invoice_reader.models.base import BaseDocument, DocumentItem, Address


@pytest.fixture
def sample_document():
    """Create a sample document for testing"""
    return BaseDocument(
        document_type="invoice",
        document_number="TEST-001",
        date="2024-05-14",
        sender=Address(
            company="Test Sender Inc",
            address="123 Sender St",
            phone="555-1234"
        ),
        receiver=Address(
            company="Test Receiver Corp",
            address="456 Receiver Ave",
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
        subtotal=2000.0,
        tax=200.0,
        total_amount=2200.0,
        currency="JPY",
        confidence=0.95,
        extraction_method="test_method",
        source_file="test_invoice.pdf"
    )


def test_to_csv_row(sample_document):
    """Test converting document to CSV row"""
    row = sample_document.to_csv_row()

    assert row['document_type'] == 'invoice'
    assert row['document_number'] == 'TEST-001'
    assert row['date'] == '2024-05-14'
    assert row['sender_company'] == 'Test Sender Inc'
    assert row['receiver_company'] == 'Test Receiver Corp'
    assert row['total_amount'] == 2200.0
    assert row['currency'] == 'JPY'
    assert row['item_count'] == 2
    assert '95' in row['confidence']  # Check percentage format


def test_to_csv_items(sample_document):
    """Test converting document items to CSV rows"""
    rows = sample_document.to_csv_items()

    assert len(rows) == 2

    # Check first item
    assert rows[0]['document_number'] == 'TEST-001'
    assert rows[0]['item_index'] == 1
    assert rows[0]['description'] == 'Product A'
    assert rows[0]['quantity'] == 10
    assert rows[0]['unit_price'] == 100.0
    assert rows[0]['amount'] == 1000.0

    # Check second item
    assert rows[1]['item_index'] == 2
    assert rows[1]['description'] == 'Product B'


def test_save_to_csv_summary(sample_document):
    """Test saving document to summary CSV"""
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = Path(tmpdir) / "test_summary.csv"
        sample_document.save_to_csv(str(csv_path), mode='summary')

        assert csv_path.exists()

        # Read and verify
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

            assert len(rows) == 1
            assert rows[0]['document_number'] == 'TEST-001'
            assert rows[0]['total_amount'] == '2200.0'


def test_save_to_csv_items(sample_document):
    """Test saving document items to CSV"""
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = Path(tmpdir) / "test_items.csv"
        sample_document.save_to_csv(str(csv_path), mode='items')

        assert csv_path.exists()

        # Read and verify
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

            assert len(rows) == 2
            assert rows[0]['description'] == 'Product A'
            assert rows[1]['description'] == 'Product B'


def test_save_multiple_to_csv_summary():
    """Test saving multiple documents to CSV"""
    doc1 = BaseDocument(
        document_type="invoice",
        document_number="DOC-001",
        date="2024-05-14",
        total_amount=1000.0,
        confidence=0.95
    )

    doc2 = BaseDocument(
        document_type="invoice",
        document_number="DOC-002",
        date="2024-05-15",
        total_amount=2000.0,
        confidence=0.92
    )

    documents = [doc1, doc2]

    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = Path(tmpdir) / "test_batch.csv"
        BaseDocument.save_multiple_to_csv(documents, str(csv_path), mode='summary')

        assert csv_path.exists()

        # Read and verify
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

            assert len(rows) == 2
            assert rows[0]['document_number'] == 'DOC-001'
            assert rows[1]['document_number'] == 'DOC-002'


def test_save_multiple_to_csv_items():
    """Test saving items from multiple documents to CSV"""
    doc1 = BaseDocument(
        document_number="DOC-001",
        items=[
            DocumentItem(description="Item A", quantity=1, amount=100.0)
        ]
    )

    doc2 = BaseDocument(
        document_number="DOC-002",
        items=[
            DocumentItem(description="Item B", quantity=2, amount=200.0),
            DocumentItem(description="Item C", quantity=3, amount=300.0)
        ]
    )

    documents = [doc1, doc2]

    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = Path(tmpdir) / "test_batch_items.csv"
        BaseDocument.save_multiple_to_csv(documents, str(csv_path), mode='items')

        assert csv_path.exists()

        # Read and verify
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

            # Should have 3 items total (1 from doc1, 2 from doc2)
            assert len(rows) == 3
            assert rows[0]['description'] == 'Item A'
            assert rows[1]['description'] == 'Item B'
            assert rows[2]['description'] == 'Item C'


def test_csv_mode_validation(sample_document):
    """Test invalid CSV mode raises error"""
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = Path(tmpdir) / "test.csv"

        with pytest.raises(ValueError, match="Invalid mode"):
            sample_document.save_to_csv(str(csv_path), mode='invalid')


def test_csv_empty_documents():
    """Test saving empty document list"""
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = Path(tmpdir) / "test_empty.csv"

        # Should not raise error, just not create file
        BaseDocument.save_multiple_to_csv([], str(csv_path), mode='summary')

        # File should not be created for empty list
        assert not csv_path.exists()


def test_csv_special_characters():
    """Test CSV export with special characters"""
    doc = BaseDocument(
        document_number="DOC-001",
        items=[
            DocumentItem(description='Item with "quotes"', quantity=1),
            DocumentItem(description='Item with, comma', quantity=2),
            DocumentItem(description='Item with\nnewline', quantity=3)
        ]
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = Path(tmpdir) / "test_special.csv"
        doc.save_to_csv(str(csv_path), mode='items')

        # Read and verify special characters are preserved
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

            assert 'quotes' in rows[0]['description']
            assert 'comma' in rows[1]['description']
