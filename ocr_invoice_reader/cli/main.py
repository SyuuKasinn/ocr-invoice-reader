"""
Main CLI entry point for document extraction
"""
import argparse
import sys
import io
from pathlib import Path

# Fix Windows encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from ocr_invoice_reader.extractors.document_extractor import DocumentExtractor
from ocr_invoice_reader import __version__


def main():
    """Main entry point for CLI"""
    parser = argparse.ArgumentParser(
        prog="ocr-extract",
        description="Document Information Extraction System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract from single file
  ocr-extract --image invoice.pdf --visualize

  # Batch extract from directory
  ocr-extract --input-dir invoices/ --visualize

  # Use CPU mode
  ocr-extract --image invoice.jpg --use-cpu

  # Custom output directory
  ocr-extract --input-dir docs/ --output-dir results/
        """
    )

    # Version
    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {__version__}'
    )

    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        '--image',
        type=str,
        help='Single image or PDF file'
    )
    input_group.add_argument(
        '--input-dir',
        type=str,
        help='Directory containing images/PDFs'
    )

    # Output options
    parser.add_argument(
        '--output-dir',
        type=str,
        help='Output directory (default: auto-generated timestamp folder)'
    )

    # Processing options
    parser.add_argument(
        '--visualize',
        action='store_true',
        help='Generate visualization images'
    )
    parser.add_argument(
        '--use-cpu',
        action='store_true',
        help='Force CPU mode (disable GPU)'
    )
    parser.add_argument(
        '--lang',
        type=str,
        default='ch',
        choices=['ch', 'en', 'japan', 'korean', 'latin'],
        help='OCR language (default: ch, recommended for mixed documents)'
    )

    args = parser.parse_args()

    try:
        # Initialize extractor
        print("="*60)
        print("Document Information Extraction System")
        print(f"Version: {__version__}")
        print("="*60)

        extractor = DocumentExtractor(
            use_gpu=not args.use_cpu,
            lang=args.lang
        )

        # Process
        if args.image:
            # Single file
            print(f"\nProcessing: {args.image}")
            document = extractor.extract(args.image, visualize=args.visualize)

            # Save result
            import os
            output_dir = args.output_dir or "extracted_data"
            os.makedirs(output_dir, exist_ok=True)

            output_file = Path(output_dir) / f"{Path(args.image).stem}_extracted.json"
            document.save_to_file(str(output_file))

            print("\n" + "="*60)
            print("EXTRACTION RESULTS")
            print("="*60)
            print(document)
            print("="*60)
            print(f"\nResult saved to: {output_file}")

        else:
            # Batch processing
            print(f"\nBatch processing: {args.input_dir}")
            documents = extractor.batch_extract(
                input_path=args.input_dir,
                output_dir=args.output_dir,
                visualize=args.visualize
            )

            print("\n" + "="*60)
            print(f"BATCH PROCESSING COMPLETE")
            print("="*60)
            print(f"Total processed: {len(documents)}")
            print(f"Average confidence: {sum(d.confidence for d in documents)/len(documents):.1%}" if documents else "N/A")
            print("="*60)

        return 0

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        return 1
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
