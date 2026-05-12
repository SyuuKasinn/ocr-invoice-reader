"""
Simple CLI for basic OCR (legacy functionality)
"""
import argparse
import sys
import io
from pathlib import Path

# Fix Windows encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from ocr_invoice_reader.extractors.simple_ocr import SimpleOCR
from ocr_invoice_reader import __version__


def main():
    """Main entry point for simple OCR CLI"""
    parser = argparse.ArgumentParser(
        prog="ocr-simple",
        description="Simple OCR Text Recognition",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Simple OCR on single image
  ocr-simple --image invoice.jpg

  # Batch OCR on directory
  ocr-simple --input-dir images/

  # Enable handwriting mode
  ocr-simple --image handwritten.jpg --handwriting

  # Disable text correction
  ocr-simple --image invoice.jpg --no-correction
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
        help='Single image file'
    )
    input_group.add_argument(
        '--input-dir',
        type=str,
        help='Directory containing images'
    )

    # Output options
    parser.add_argument(
        '--output-dir',
        type=str,
        help='Output directory'
    )

    # Processing options
    parser.add_argument(
        '--handwriting',
        action='store_true',
        help='Enable handwriting recognition mode'
    )
    parser.add_argument(
        '--no-correction',
        action='store_true',
        help='Disable text correction'
    )
    parser.add_argument(
        '--use-cpu',
        action='store_true',
        help='Force CPU mode'
    )
    parser.add_argument(
        '--lang',
        type=str,
        default='ch',
        choices=['ch', 'en', 'japan', 'korean', 'latin'],
        help='OCR language (default: ch, recommended for mixed documents)'
    )
    parser.add_argument(
        '--confidence',
        type=float,
        default=0.5,
        help='Confidence threshold (default: 0.5)'
    )

    args = parser.parse_args()

    try:
        # Initialize OCR
        print("Simple OCR Text Recognition")
        print(f"Version: {__version__}")
        print("="*60)

        ocr = SimpleOCR(
            lang=args.lang,
            use_gpu=not args.use_cpu,
            confidence_threshold=args.confidence,
            handwriting_mode=args.handwriting,
            enable_correction=not args.no_correction
        )

        # Process
        if args.image:
            # Single file
            print(f"\nRecognizing: {args.image}")
            result = ocr.recognize(args.image)

            print(f"\nRecognized {result['total_lines']} lines")
            print("\nText:")
            print("-"*60)
            print(result['full_text'])
            print("-"*60)

            # Save result
            if args.output_dir:
                import os
                import json
                os.makedirs(args.output_dir, exist_ok=True)
                output_file = Path(args.output_dir) / f"{Path(args.image).stem}_ocr.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                print(f"\nResult saved to: {output_file}")

        else:
            # Batch processing
            print(f"\nBatch processing: {args.input_dir}")
            results = ocr.batch_recognize(
                input_dir=args.input_dir,
                output_dir=args.output_dir
            )

            print(f"\nProcessed {len(results)} files")
            total_lines = sum(r['total_lines'] for r in results)
            print(f"Total lines recognized: {total_lines}")

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
