"""
Simple PDF test - Test both invoice PDFs with basic OCR
"""
import sys
from pathlib import Path
from datetime import datetime
from ocr_invoice_reader.core.pipeline import Pipeline
from ocr_invoice_reader.core.config import PipelineConfig, VLConfig, IOConfig

def simple_test(pdf_path: str, output_name: str):
    """Simple test with basic OCR only"""
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        print(f"ERROR: File not found: {pdf_path}")
        return False

    print("\n" + "="*80)
    print(f"Testing: {pdf_path.name}")
    print("="*80)

    # Simple configuration
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f'test_results/{output_name}_{timestamp}'

    config = PipelineConfig(
        vl=VLConfig(use_gpu=False),  # CPU only for faster initialization
        io=IOConfig(
            output_dir=output_dir,
            save_markdown=True,
            save_visualization=True,
            save_per_page_json=True,
        )
    )

    try:
        print(f"[INFO] Processing with PaddleOCR-VL...")
        print(f"[INFO] Output directory: {output_dir}")

        pipeline = Pipeline(config)
        document = pipeline.run(str(pdf_path))

        print(f"\n[SUCCESS] Processing complete!")
        print(f"  Document: {document.document}")
        print(f"  Total Pages: {document.total_pages}")

        # Summary
        for page in document.pages:
            print(f"\n  Page {page.page_index + 1}: {len(page.blocks)} regions detected")

            # Count region types
            region_counts = {}
            for block in page.blocks:
                region_counts[block.label] = region_counts.get(block.label, 0) + 1

            for label, count in sorted(region_counts.items()):
                print(f"    - {label}: {count}")

        # List generated files
        output_path = Path(output_dir)
        if output_path.exists():
            files = list(output_path.rglob('*'))
            file_list = [f for f in files if f.is_file()]
            print(f"\n  Generated {len(file_list)} files in: {output_dir}")
            for f in sorted(file_list)[:5]:  # Show first 5 files
                print(f"    - {f.name}")
            if len(file_list) > 5:
                print(f"    ... and {len(file_list) - 5} more files")

        print(f"\n[SUCCESS] {pdf_path.name} test passed")
        return True

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("\n" + "="*80)
    print("OCR Invoice Reader - Simple PDF Test")
    print("="*80)

    # Test files
    tests = [
        (r"C:\Work\SVN\trunk\SBS_GLOVIA\00.資料\INVOICE関連\インボイス見本.pdf", "invoice_sample"),
        (r"C:\Work\SVN\trunk\SBS_GLOVIA\00.資料\INVOICE関連\INVOICE.pdf", "invoice_main"),
    ]

    results = {}
    for pdf_path, name in tests:
        results[Path(pdf_path).name] = simple_test(pdf_path, name)

    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    for filename, success in results.items():
        status = "[PASSED]" if success else "[FAILED]"
        print(f"  {status} {filename}")

    total = len(results)
    passed = sum(1 for s in results.values() if s)
    print(f"\n  Total: {passed}/{total} tests passed")
    print("="*80)

    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
