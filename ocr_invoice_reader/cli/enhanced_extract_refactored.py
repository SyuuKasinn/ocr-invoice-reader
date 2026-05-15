"""
Enhanced extraction CLI - Refactored to use Qwen Direct by default
"""
import argparse
import sys
import io
import json
import csv
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict

from ocr_invoice_reader.processors.enhanced_structure_analyzer import EnhancedStructureAnalyzer
from ocr_invoice_reader.processors.file_handler import FileProcessor
from ocr_invoice_reader.utils.invoice_extractor_v2 import InvoiceExtractorV2
from ocr_invoice_reader.utils.llm_invoice_extractor import LLMInvoiceExtractor, validate_extraction_result
from ocr_invoice_reader.utils.llm_factory import create_llm_processor, LLMFactory
from ocr_invoice_reader import __version__


def main():
    """Enhanced extraction CLI"""
    # Fix Windows encoding
    if sys.platform == 'win32':
        try:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        except (AttributeError, ValueError):
            pass

    parser = argparse.ArgumentParser(
        prog="ocr-enhanced",
        description="Enhanced OCR with Qwen Direct LLM (GPU accelerated)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic OCR + LLM (auto-selects best backend)
  ocr-enhanced --image invoice.pdf --use-llm

  # Force Qwen Direct (recommended for GPU)
  ocr-enhanced --image invoice.pdf --use-llm --llm-backend qwen_direct

  # Force Ollama (if you prefer)
  ocr-enhanced --image invoice.pdf --use-llm --llm-backend ollama

  # Use specific model size
  ocr-enhanced --image invoice.pdf --use-llm --llm-model 7b

  # High accuracy with 14B model
  ocr-enhanced --image invoice.pdf --use-llm --llm-model 14b

  # Check available backends
  ocr-enhanced --check-llm
        """
    )

    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')
    parser.add_argument('--image', type=str, help='Image or PDF file')
    parser.add_argument('--output-dir', type=str, default='results', help='Output directory')
    parser.add_argument('--visualize', action='store_true', help='Generate visualization')
    parser.add_argument('--use-cpu', action='store_true', help='Force CPU mode (for OCR)')
    parser.add_argument('--lang', type=str, default='ch',
                       choices=['ch', 'en', 'japan', 'korean', 'latin'],
                       help='OCR language (default: ch)')

    # LLM options
    parser.add_argument('--use-llm', action='store_true',
                       help='Enable LLM post-processing (GPU accelerated)')
    parser.add_argument('--llm-model', type=str, default='7b',
                       help='LLM model size: 3b, 7b, 14b (default: 7b)')
    parser.add_argument('--llm-backend', type=str, default='auto',
                       choices=['auto', 'qwen_direct', 'ollama'],
                       help='LLM backend: auto (default), qwen_direct, ollama')
    parser.add_argument('--llm-quantization', type=str, default='int4',
                       choices=['none', 'int4', 'int8'],
                       help='Quantization for Qwen Direct (default: int4)')
    parser.add_argument('--llm-gpu', action='store_true', default=True,
                       help='Use GPU for LLM (default: True)')
    parser.add_argument('--check-llm', action='store_true',
                       help='Check available LLM backends and exit')

    # Legacy compatibility
    parser.add_argument('--auto-setup-ollama', action='store_true',
                       help='[Deprecated] Use --llm-backend ollama instead')

    args = parser.parse_args()

    # Check LLM status and exit
    if args.check_llm:
        LLMFactory.print_status()
        return 0

    # Validate required arguments
    if not args.image:
        parser.error("--image is required (unless using --check-llm)")

    try:
        overall_start = time.time()

        print("="*60)
        print("Enhanced Document Extraction")
        print(f"Version: {__version__}")
        print(f"⏱ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)

        # Convert PDF if needed
        file_processor = FileProcessor()
        images = file_processor.process_file(args.image)

        if not images:
            print(f"Error: Cannot process file {args.image}")
            return 1

        print(f"\nTotal pages: {len(images)}")

        # Initialize analyzer
        analyzer = EnhancedStructureAnalyzer(
            use_gpu=not args.use_cpu,
            lang=args.lang
        )

        # Initialize LLM processor if requested
        llm_processor = None
        if args.use_llm:
            print("\nInitializing LLM processor...")

            # Handle quantization
            quantization = None if args.llm_quantization == 'none' else args.llm_quantization

            try:
                llm_processor = create_llm_processor(
                    model=args.llm_model,
                    backend=args.llm_backend,
                    use_gpu=args.llm_gpu,
                    quantization=quantization
                )

                if llm_processor:
                    backend = "Qwen Direct" if hasattr(llm_processor, 'tokenizer') else "Ollama"
                    print(f"✓ LLM ready: {args.llm_model} ({backend})")
                else:
                    print("✗ LLM initialization failed")
                    print("Continuing with OCR only mode")

            except Exception as e:
                print(f"✗ LLM error: {e}")
                print("Continuing with OCR only mode")

                # Fallback to Ollama if explicitly requested
                if args.auto_setup_ollama:
                    print("\n⚠ --auto-setup-ollama is deprecated")
                    print("For Ollama support, use: --llm-backend ollama")

        # Create extractor
        llm_extractor = None
        if llm_processor:
            llm_extractor = LLMInvoiceExtractor(llm_processor)

        # Process each page
        all_results = []
        all_invoices = []

        for idx, image_path in enumerate(images, 1):
            print("\n" + "="*60)
            print(f"⏱ [Page {idx}/{len(images)}] Starting: {Path(image_path).name}")
            print("="*60)

            page_start = time.time()

            # Analyze structure
            result = analyzer.analyze_single_page(args.image, page_idx=idx-1)

            # Extract text for LLM
            if llm_extractor:
                all_text = ""
                for region in result.get('regions', []):
                    if hasattr(region, 'text') and region.text:
                        all_text += region.text + "\n"

                if all_text.strip():
                    print("  Running LLM post-processing...")
                    llm_start = time.time()

                    try:
                        llm_result = llm_extractor.extract_from_text(all_text)

                        if llm_result and validate_extraction_result(llm_result):
                            result['llm_extraction'] = llm_result
                            all_invoices.append(llm_result.get('invoice_data', {}))
                            print(f"  ✓ LLM processing successful ({time.time()-llm_start:.2f}s)")
                        else:
                            print(f"  ⚠ LLM extraction incomplete")

                    except Exception as e:
                        print(f"  ✗ LLM processing failed: {e}")

            all_results.append(result)

            page_time = time.time() - page_start
            print("="*60)
            print(f"⏱ [Page {idx}] Completed in {page_time:.2f}s")
            print("="*60)

        # Save results
        print("\n" + "="*60)
        print("Saving results...")
        print("="*60)

        # Create output directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path(args.output_dir) / timestamp
        output_dir.mkdir(parents=True, exist_ok=True)

        base_name = Path(args.image).stem

        # Save individual pages
        for idx, result in enumerate(all_results, 1):
            page_base = f"{base_name}_page_{idx:04d}"

            # JSON
            json_path = output_dir / f"{page_base}.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2, default=str)
            print(f"  Page {idx} JSON: {json_path.name}")

            # TXT
            txt_path = output_dir / f"{page_base}.txt"
            with open(txt_path, 'w', encoding='utf-8') as f:
                for region in result.get('regions', []):
                    if hasattr(region, 'text') and region.text:
                        f.write(f"{region.text}\n\n")
            print(f"  Page {idx} TXT: {txt_path.name}")

            # LLM JSON (if available)
            if 'llm_extraction' in result:
                llm_json_path = output_dir / f"{page_base}_llm.json"
                with open(llm_json_path, 'w', encoding='utf-8') as f:
                    json.dump(result['llm_extraction'], f, ensure_ascii=False, indent=2)
                print(f"  Page {idx} LLM JSON: {llm_json_path.name}")

        # Combined results
        combined_path = output_dir / f"{base_name}_all_pages.json"
        with open(combined_path, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2, default=str)
        print(f"\n  Combined JSON: {combined_path.name}")

        # All invoices
        if all_invoices:
            invoices_path = output_dir / f"{base_name}_invoices.json"
            with open(invoices_path, 'w', encoding='utf-8') as f:
                json.dump(all_invoices, f, ensure_ascii=False, indent=2)
            print(f"  All invoices: {invoices_path.name}")

        # Summary
        total_time = time.time() - overall_start
        print("\n" + "="*60)
        print("EXTRACTION SUMMARY")
        print("="*60)
        print(f"Total pages: {len(images)}")
        print(f"Total processing time: {total_time:.2f}s")
        print(f"Average per page: {total_time/len(images):.2f}s")
        print(f"Output directory: {output_dir}")

        if llm_processor:
            print(f"LLM extractions: {len(all_invoices)}/{len(images)}")

        print("="*60)

        return 0

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        return 130
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
