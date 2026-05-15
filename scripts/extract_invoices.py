"""
Batch extract invoice data from OCR results
Processes all TXT files in a results directory and generates CSV for database import
"""
import sys
import io
import csv
import json
from pathlib import Path
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except (AttributeError, ValueError):
        pass

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ocr_invoice_reader.utils.invoice_extractor import InvoiceExtractor


def process_results_directory(results_dir: str, output_csv: str = None):
    """Process all TXT files in results directory"""

    results_path = Path(results_dir)

    if not results_path.exists():
        print(f"Error: Directory not found: {results_dir}")
        return

    # Find all page TXT files (not _llm.txt or _analysis.txt)
    txt_files = []
    for txt_file in results_path.rglob("*.txt"):
        # Skip LLM analysis files
        if '_llm' not in txt_file.stem and '_analysis' not in txt_file.stem:
            # Only process page files
            if '_page_' in txt_file.stem or '_all_pages' in txt_file.stem:
                txt_files.append(txt_file)

    if not txt_files:
        print(f"No TXT files found in {results_dir}")
        return

    print("="*60)
    print("BATCH INVOICE EXTRACTION")
    print("="*60)
    print(f"Found {len(txt_files)} TXT files")
    print()

    extractor = InvoiceExtractor()
    all_results = []

    for txt_file in txt_files:
        print(f"Processing: {txt_file.name}")

        try:
            data = extractor.extract_from_file(str(txt_file))
            db_data = extractor.format_for_database(data)

            # Add source info
            db_data['source_file'] = txt_file.name
            db_data['source_path'] = str(txt_file)

            all_results.append(db_data)

            # Show extracted info
            if db_data.get('invoice_number'):
                print(f"  ✓ Invoice: {db_data['invoice_number']}")
            if db_data.get('company_name'):
                print(f"  ✓ Company: {db_data['company_name']}")
            if db_data.get('total_amount'):
                print(f"  ✓ Amount: {db_data['currency']} {db_data['total_amount']}")
            print()

        except Exception as e:
            print(f"  ✗ Error: {e}")
            print()

    # Generate output CSV
    if not output_csv:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_csv = f"invoices_extracted_{timestamp}.csv"

    output_path = Path(output_csv)

    print("="*60)
    print("SAVING RESULTS")
    print("="*60)

    # Get all unique field names
    all_fields = set()
    for result in all_results:
        all_fields.update(result.keys())

    # Order fields: important ones first, then alphabetical
    priority_fields = ['invoice_number', 'invoice_date', 'company_name', 'total_amount', 'currency']
    other_fields = sorted([f for f in all_fields if f not in priority_fields])
    ordered_fields = [f for f in priority_fields if f in all_fields] + other_fields

    # Write CSV
    with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=ordered_fields)
        writer.writeheader()
        writer.writerows(all_results)

    print(f"✓ CSV saved: {output_path}")
    print(f"  Records: {len(all_results)}")

    # Also save as JSON
    json_path = output_path.with_suffix('.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    print(f"✓ JSON saved: {json_path}")

    # Generate SQL INSERT statements
    sql_path = output_path.with_suffix('.sql')
    with open(sql_path, 'w', encoding='utf-8') as f:
        f.write("-- Generated SQL INSERT statements for invoices\n")
        f.write(f"-- Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"-- Total records: {len(all_results)}\n\n")

        # Create table statement
        f.write("CREATE TABLE IF NOT EXISTS invoices (\n")
        f.write("    id INT AUTO_INCREMENT PRIMARY KEY,\n")
        f.write("    invoice_number VARCHAR(100),\n")
        f.write("    invoice_date VARCHAR(50),\n")
        f.write("    tracking_number VARCHAR(100),\n")
        f.write("    company_name VARCHAR(255),\n")
        f.write("    total_amount DECIMAL(15,2),\n")
        f.write("    currency VARCHAR(10),\n")
        f.write("    phone VARCHAR(50),\n")
        f.write("    fax VARCHAR(50),\n")
        f.write("    item_count INT,\n")
        f.write("    source_file VARCHAR(255),\n")
        f.write("    source_path TEXT,\n")
        f.write("    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP\n")
        f.write(");\n\n")

        # Generate INSERT statements
        for result in all_results:
            # Create temporary data dict with only non-None values
            insert_data = {k: v for k, v in result.items() if v is not None}

            if insert_data:
                fields = list(insert_data.keys())
                values = []

                for key in fields:
                    value = insert_data[key]
                    if isinstance(value, str):
                        # Escape single quotes
                        value = value.replace("'", "''")
                        values.append(f"'{value}'")
                    elif value is None:
                        values.append('NULL')
                    else:
                        values.append(str(value))

                fields_str = ', '.join(fields)
                values_str = ', '.join(values)

                f.write(f"INSERT INTO invoices ({fields_str})\n")
                f.write(f"VALUES ({values_str});\n\n")

    print(f"✓ SQL saved: {sql_path}")

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    # Statistics
    with_invoice_no = sum(1 for r in all_results if r.get('invoice_number'))
    with_company = sum(1 for r in all_results if r.get('company_name'))
    with_amount = sum(1 for r in all_results if r.get('total_amount'))

    print(f"Total records:      {len(all_results)}")
    print(f"With invoice no:    {with_invoice_no}")
    print(f"With company name:  {with_company}")
    print(f"With total amount:  {with_amount}")

    print("\nOutput files:")
    print(f"  - {output_path.name} (CSV for Excel/database import)")
    print(f"  - {json_path.name} (JSON for APIs)")
    print(f"  - {sql_path.name} (SQL statements)")


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Extract invoice data from OCR results for database import",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process specific results directory
  python extract_invoices.py --dir results/20260515_104903

  # Process and specify output file
  python extract_invoices.py --dir results/20260515_104903 --output my_invoices.csv

  # Process all results
  python extract_invoices.py --dir results
        """
    )

    parser.add_argument(
        '--dir',
        type=str,
        required=True,
        help='Results directory to process'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Output CSV file (default: invoices_extracted_TIMESTAMP.csv)'
    )

    args = parser.parse_args()

    process_results_directory(args.dir, args.output)


if __name__ == '__main__':
    main()
