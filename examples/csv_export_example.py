"""
Example: CSV Export Usage

This example demonstrates how to use the CSV export functionality.
"""
from pathlib import Path
from ocr_invoice_reader.extractors.document_extractor import DocumentExtractor
from ocr_invoice_reader.models.base import BaseDocument


def example_single_document():
    """Export single document to CSV"""
    print("=" * 60)
    print("Example 1: Single Document CSV Export")
    print("=" * 60)

    # Extract document
    extractor = DocumentExtractor(use_gpu=False, lang='ch')
    document = extractor.extract('invoice.pdf')

    # Save as summary CSV (one row with document info)
    document.save_to_csv('output/invoice_summary.csv', mode='summary')
    print("✓ Summary CSV saved: output/invoice_summary.csv")

    # Save as items CSV (one row per line item)
    document.save_to_csv('output/invoice_items.csv', mode='items')
    print("✓ Items CSV saved: output/invoice_items.csv")


def example_batch_documents():
    """Export batch documents to CSV"""
    print("\n" + "=" * 60)
    print("Example 2: Batch Documents CSV Export")
    print("=" * 60)

    # Process batch
    extractor = DocumentExtractor(use_gpu=False, lang='ch')
    documents = extractor.batch_extract(
        input_path='invoices/',
        output_dir='output/batch_results',
        visualize=False
    )

    # CSV files are automatically generated in output directory:
    # - extraction_summary.csv (one row per document)
    # - extraction_items.csv (one row per item)

    print(f"\n✓ Processed {len(documents)} documents")
    print("✓ CSV files saved in: output/batch_results/")


def example_custom_csv():
    """Custom CSV export with multiple documents"""
    print("\n" + "=" * 60)
    print("Example 3: Custom Multi-Document CSV")
    print("=" * 60)

    # Create or load multiple documents
    documents = []

    # Process multiple files
    extractor = DocumentExtractor(use_gpu=False, lang='ch')
    for pdf_file in Path('invoices/').glob('*.pdf'):
        doc = extractor.extract(str(pdf_file))
        documents.append(doc)

    # Export all documents to single CSV
    BaseDocument.save_multiple_to_csv(
        documents,
        'output/all_invoices_summary.csv',
        mode='summary'
    )
    print("✓ Summary CSV saved: output/all_invoices_summary.csv")

    BaseDocument.save_multiple_to_csv(
        documents,
        'output/all_invoices_items.csv',
        mode='items'
    )
    print("✓ Items CSV saved: output/all_invoices_items.csv")


def example_reading_csv():
    """Example of reading exported CSV with pandas"""
    print("\n" + "=" * 60)
    print("Example 4: Reading CSV with Pandas")
    print("=" * 60)

    try:
        import pandas as pd

        # Read summary CSV
        df_summary = pd.read_csv('output/invoice_summary.csv')
        print("\nSummary CSV columns:")
        print(df_summary.columns.tolist())
        print(f"\nTotal documents: {len(df_summary)}")

        # Read items CSV
        df_items = pd.read_csv('output/invoice_items.csv')
        print("\nItems CSV columns:")
        print(df_items.columns.tolist())
        print(f"\nTotal items: {len(df_items)}")

        # Analysis examples
        print("\n--- Analysis Examples ---")

        # Total amount by document
        print("\nTotal amounts by document:")
        print(df_summary[['document_number', 'total_amount', 'currency']])

        # Item statistics
        if not df_items.empty:
            print(f"\nAverage items per document: {len(df_items) / len(df_summary):.1f}")
            print(f"Total items value: {df_items['amount'].sum()}")

    except ImportError:
        print("\nNote: Install pandas to analyze CSV files:")
        print("  pip install pandas")


def example_csv_formats():
    """Show the difference between summary and items CSV formats"""
    print("\n" + "=" * 60)
    print("CSV Format Comparison")
    print("=" * 60)

    print("\n1. SUMMARY CSV (mode='summary')")
    print("-" * 40)
    print("One row per document with flattened structure:")
    print("""
    document_type | document_number | date       | sender_company | receiver_company | total_amount | currency
    invoice       | INV-2024-001    | 2024-05-14 | ABC Company    | XYZ Corp         | 10000       | JPY
    invoice       | INV-2024-002    | 2024-05-15 | ABC Company    | DEF Corp         | 15000       | JPY
    """)

    print("\n2. ITEMS CSV (mode='items')")
    print("-" * 40)
    print("One row per line item with references:")
    print("""
    document_number | document_type | item_index | description | quantity | unit_price | amount
    INV-2024-001    | invoice       | 1          | Product A   | 10       | 1000       | 10000
    INV-2024-001    | invoice       | 2          | Product B   | 5        | 2000       | 10000
    INV-2024-002    | invoice       | 1          | Product C   | 20       | 750        | 15000
    """)

    print("\nUse summary CSV for:")
    print("  - Document-level analysis")
    print("  - High-level reporting")
    print("  - Master data tables")

    print("\nUse items CSV for:")
    print("  - Line item analysis")
    print("  - Detailed reporting")
    print("  - Product/SKU tracking")


if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════╗
║           OCR Invoice Reader - CSV Export Examples        ║
╚════════════════════════════════════════════════════════════╝
    """)

    # Show format comparison
    example_csv_formats()

    # Uncomment to run live examples:
    # example_single_document()
    # example_batch_documents()
    # example_custom_csv()
    # example_reading_csv()

    print("\n" + "=" * 60)
    print("To run the live examples:")
    print("  1. Uncomment the example functions above")
    print("  2. Ensure you have invoice PDF files in the correct paths")
    print("  3. Run: python examples/csv_export_example.py")
    print("=" * 60)
