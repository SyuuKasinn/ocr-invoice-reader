"""
Comprehensive Test for Invoice PDFs
Tests both インボイス見本.pdf and INVOICE.pdf
"""
import sys
from pathlib import Path
from datetime import datetime
from ocr_invoice_reader.core.pipeline import Pipeline
from ocr_invoice_reader.core.config import PipelineConfig, VLConfig, IOConfig

def test_invoice_pdf(pdf_path: str, output_prefix: str = "test"):
    """Test a single invoice PDF"""
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        print(f"[ERROR] File not found {pdf_path}")
        return False

    print("\n" + "="*80)
    print(f"Testing: {pdf_path.name}")
    print("="*80)

    # Configuration
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f'test_results/{output_prefix}_{timestamp}'

    config = PipelineConfig(
        vl=VLConfig(
            use_gpu=True,  # Try GPU first
            lang='japan',  # Japanese language support
        ),
        io=IOConfig(
            output_dir=output_dir,
            save_markdown=True,
            save_visualization=True,
            save_per_page_json=True,
        )
    )

    try:
        # Process all pages
        print(f"\n[INFO] Processing PDF with OCR + LLM...")
        pipeline = Pipeline(config)
        document = pipeline.run(str(pdf_path))

        # Display results
        print(f"\n[SUCCESS] Processing Complete!")
        print(f"Document: {document.document}")
        print(f"Total Pages: {document.total_pages}")
        print(f"Output Directory: {output_dir}")

        # Page-by-page summary
        for page in document.pages:
            print(f"\n{'-'*80}")
            print(f"Page {page.page_index + 1}/{document.total_pages}")
            print(f"{'-'*80}")
            print(f"  Detected Regions: {len(page.blocks)}")

            # Region breakdown
            region_types = {}
            for block in page.blocks:
                region_types[block.label] = region_types.get(block.label, 0) + 1

            for label, count in sorted(region_types.items()):
                print(f"    - {label}: {count}")

            # Text content preview
            total_text_length = sum(len(block.text or '') for block in page.blocks)
            print(f"  Total Text: {total_text_length} characters")

            # Show first few text blocks
            text_blocks = [b for b in page.blocks if b.text and len(b.text.strip()) > 10]
            if text_blocks:
                print(f"\n  Sample Text Blocks:")
                for i, block in enumerate(text_blocks[:3], 1):
                    text_preview = block.text.strip()[:80].replace('\n', ' ')
                    if len(block.text) > 80:
                        text_preview += "..."
                    print(f"    [{i}] {block.label}: {text_preview}")

            # Markdown summary
            if page.markdown:
                lines = [l for l in page.markdown.split('\n') if l.strip()]
                print(f"  Markdown: {len(lines)} lines")

        # List output files
        output_path = Path(output_dir)
        if output_path.exists():
            print(f"\nGenerated Files:")
            for file in sorted(output_path.rglob('*')):
                if file.is_file():
                    size_kb = file.stat().st_size / 1024
                    rel_path = file.relative_to(output_path)
                    print(f"  - {rel_path} ({size_kb:.1f} KB)")

        print(f"\n[SUCCESS] Test completed successfully for {pdf_path.name}")
        return True

    except Exception as e:
        print(f"\n[ERROR] During processing: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run tests on both invoice PDFs"""
    print("\n" + "="*80)
    print("OCR Invoice Reader - PDF Test Suite")
    print("="*80)

    # Test files
    test_files = [
        (r"C:\Work\SVN\trunk\SBS_GLOVIA\00.資料\INVOICE関連\インボイス見本.pdf", "invoice_sample"),
        (r"C:\Work\SVN\trunk\SBS_GLOVIA\00.資料\INVOICE関連\INVOICE.pdf", "invoice"),
    ]

    results = {}

    for pdf_path, prefix in test_files:
        success = test_invoice_pdf(pdf_path, prefix)
        results[Path(pdf_path).name] = success

    # Final summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    for filename, success in results.items():
        status = "[PASSED]" if success else "[FAILED]"
        print(f"  {status} - {filename}")

    total = len(results)
    passed = sum(1 for s in results.values() if s)
    print(f"\n  Total: {passed}/{total} tests passed")
    print("="*80)

    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
