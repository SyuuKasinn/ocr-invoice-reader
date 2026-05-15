"""
Enhanced extraction CLI with better table detection
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
from ocr_invoice_reader.utils.invoice_extractor import InvoiceExtractor
from ocr_invoice_reader import __version__


def main():
    """Enhanced extraction CLI"""
    # Fix Windows encoding (do it inside main, after argparse)
    if sys.platform == 'win32':
        try:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        except (AttributeError, ValueError):
            pass  # Already wrapped or not needed
    parser = argparse.ArgumentParser(
        prog="ocr-enhanced",
        description="Enhanced OCR with Better Table Detection",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Enhanced extraction
  ocr-enhanced --image invoice.pdf --visualize

  # Use CPU mode
  ocr-enhanced --image invoice.jpg --use-cpu
        """
    )

    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')
    parser.add_argument('--image', type=str, required=True, help='Image or PDF file')
    parser.add_argument('--output-dir', type=str, default='results', help='Output directory')
    parser.add_argument('--visualize', action='store_true', help='Generate visualization')
    parser.add_argument('--use-cpu', action='store_true', help='Force CPU mode')
    parser.add_argument('--lang', type=str, default='ch', choices=['ch', 'en', 'japan', 'korean', 'latin'], help='OCR language (default: ch, recommended for mixed documents)')
    parser.add_argument('--use-llm', action='store_true', help='Enable LLM post-processing (requires Ollama)')
    parser.add_argument('--llm-model', type=str, default='qwen2.5:3b', help='LLM model for post-processing (default: qwen2.5:3b)')
    parser.add_argument('--auto-setup-ollama', action='store_true', help='Automatically setup Ollama without prompts (installs if needed)')

    args = parser.parse_args()

    try:
        print("="*60)
        print("Enhanced Document Extraction")
        print(f"Version: {__version__}")
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
            from ocr_invoice_reader.utils.llm_processor import create_llm_processor
            from ocr_invoice_reader.utils.ollama_manager import OllamaManager

            print("\nInitializing LLM processor...")

            # Try to create directly first
            llm_processor = create_llm_processor(args.llm_model)

            if llm_processor:
                print(f"✓ LLM ready: {args.llm_model}")
            else:
                # LLM not available, try auto setup
                print("✗ LLM not available")

                if args.auto_setup_ollama:
                    # Fully automatic mode
                    print("\nAutomatic setup mode (--auto-setup-ollama)")
                    manager = OllamaManager()
                    success, message = manager.setup(args.llm_model, auto_confirm=True)

                    if success:
                        llm_processor = create_llm_processor(args.llm_model)
                        if llm_processor:
                            print(f"✓ LLM setup successful")
                        else:
                            print(f"✗ LLM still unavailable, continuing with OCR only")
                    else:
                        print(f"{message}")
                        print("Continuing with OCR only mode")
                else:
                    # Interactive mode
                    print("\nOllama service is not running or not installed")
                    print("Options:")
                    print("  1. Automatic setup of Ollama (recommended)")
                    print("  2. View manual setup instructions")
                    print("  3. Skip LLM features, continue with OCR only")

                    choice = input("\nPlease choose (1/2/3): ").strip()

                    if choice == '1':
                        # Interactive automatic setup
                        print("\nStarting automatic setup...")
                        manager = OllamaManager()
                        success, message = manager.setup(args.llm_model, auto_confirm=False)

                        if success:
                            llm_processor = create_llm_processor(args.llm_model)
                            if llm_processor:
                                print(f"\n✓ LLM setup successful, starting processing")
                            else:
                                print(f"\n✗ LLM still unavailable, continuing with OCR only")
                        else:
                            print(f"\n{message}")
                            print("Continuing with OCR only mode")

                    elif choice == '2':
                        print("\n" + "=" * 60)
                        print("Manual Ollama Setup")
                        print("=" * 60)
                        print("1. Visit: https://ollama.ai/download")
                        print("2. Download and install Ollama (Windows version)")
                        print("3. After installation, run in command line:")
                        print(f"   ollama pull {args.llm_model}")
                        print("4. Re-run this command:")
                        print(f"   ocr-enhanced --image <file> --use-llm")
                        print("\nOr use automatic installation mode:")
                        print(f"   ocr-enhanced --image <file> --use-llm --auto-setup-ollama")
                        print("=" * 60)
                        return 0

                    else:
                        print("\nContinuing with OCR only mode (without LLM)")

        # Process all pages
        all_results = []
        start_time = time.time()

        for page_idx, image_path in enumerate(images, 1):
            print(f"\n{'='*60}")
            print(f"Processing page {page_idx}/{len(images)}: {Path(image_path).name}")
            print('='*60)

            page_start = time.time()

            # Analyze
            result = analyzer.analyze(image_path)
            result['page_number'] = page_idx

            # LLM post-processing
            if llm_processor and result.get('regions'):
                print("  Running LLM post-processing...")
                try:
                    # Extract all text from regions
                    all_text = '\n'.join([
                        r.text for r in result['regions']
                        if hasattr(r, 'text') and r.text
                    ])

                    if all_text.strip():
                        # Classify document
                        doc_type = llm_processor.classify_document(all_text[:500])
                        result['llm_document_type'] = doc_type

                        # Extract fields if it's an invoice
                        if doc_type.get('type') == 'invoice':
                            fields = llm_processor.extract_invoice_fields(all_text[:1500])
                            result['llm_extracted_fields'] = fields
                            print(f"  ✓ Detected: {doc_type.get('type')} (confidence: {doc_type.get('confidence')})")
                        else:
                            print(f"  ✓ Detected: {doc_type.get('type')}")

                except Exception as e:
                    print(f"  ✗ LLM processing failed: {str(e)}")
                    result['llm_error'] = str(e)

            page_time = time.time() - page_start
            result['processing_time'] = page_time
            print(f"  ⏱ Page processed in {page_time:.2f}s")

            all_results.append(result)

        # Create output directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path(args.output_dir) / timestamp
        output_dir.mkdir(parents=True, exist_ok=True)

        input_name = Path(args.image).stem

        # Calculate timing statistics
        total_time = time.time() - start_time

        # Display summary
        print("\n" + "="*60)
        print("EXTRACTION SUMMARY")
        print("="*60)
        print(f"Total pages: {len(all_results)}")

        total_regions = sum(len(r['regions']) for r in all_results)
        total_tables = sum(1 for r in all_results for region in r['regions'] if region.type == 'table')

        print(f"Total regions: {total_regions}")
        print(f"Total tables: {total_tables}")
        print(f"\n⏱ Processing time: {total_time:.2f}s")
        print(f"  Average per page: {total_time/len(all_results):.2f}s")
        print(f"  Pages per minute: {len(all_results)/(total_time/60):.1f}")
        print("="*60)

        # Display detailed results for each page
        for result in all_results:
            page_num = result['page_number']
            print(f"\n[Page {page_num}]")
            print(f"  Method: {result['method']}")
            print(f"  Regions: {len(result['regions'])}")

            for i, region in enumerate(result['regions'], 1):
                if region.type == 'table':
                    rows = getattr(region, 'rows', '?')
                    columns = getattr(region, 'columns', '?')
                    print(f"    Region {i}: {region.type} ({rows}x{columns})")
                else:
                    print(f"    Region {i}: {region.type}")

        # Save results for all pages
        print("\n" + "="*60)
        print("Saving results...")
        print("="*60)

        # Save individual page files
        print("\nIndividual page files:")
        for result in all_results:
            page_num = result['page_number']
            page_name = Path(result['image_path']).stem

            # Convert regions to dict for JSON serialization
            result_dict = {
                'page_number': result['page_number'],
                'method': result['method'],
                'image_path': result['image_path'],
                'regions': []
            }
            for region in result['regions']:
                region_dict = {
                    'type': region.type,
                    'bbox': region.bbox,
                    'confidence': region.confidence,
                    'text': region.text,
                    'table_html': region.table_html if region.table_html else None
                }
                if hasattr(region, 'rows'):
                    region_dict['rows'] = region.rows
                if hasattr(region, 'columns'):
                    region_dict['columns'] = region.columns
                if hasattr(region, 'ocr_boxes'):
                    region_dict['ocr_boxes'] = region.ocr_boxes
                result_dict['regions'].append(region_dict)

            # Add LLM results to result_dict if present
            if 'llm_document_type' in result:
                result_dict['llm_document_type'] = result['llm_document_type']
            if 'llm_extracted_fields' in result:
                result_dict['llm_extracted_fields'] = result['llm_extracted_fields']
            if 'llm_error' in result:
                result_dict['llm_error'] = result['llm_error']

            # Individual JSON
            page_json = output_dir / f"{page_name}.json"
            with open(page_json, 'w', encoding='utf-8') as f:
                json.dump(result_dict, f, indent=2, ensure_ascii=False)
            print(f"  Page {page_num} JSON: {page_json.name}")

            # Individual TXT
            page_txt = output_dir / f"{page_name}.txt"
            with open(page_txt, 'w', encoding='utf-8') as f:
                f.write(f"PAGE {page_num}\n")
                f.write(f"{'='*60}\n\n")

                for i, region in enumerate(result['regions'], 1):
                    f.write(f"[Region {i} - {region.type}]\n")
                    f.write(region.text + '\n\n')
            print(f"  Page {page_num} TXT: {page_txt.name}")

            # Individual invoice extraction JSON (only if --use-llm is enabled)
            if llm_processor:
                page_llm_json = output_dir / f"{page_name}_llm.json"
                try:
                    # Initialize invoice extractor
                    invoice_extractor = InvoiceExtractor()

                    # Extract text from regions
                    page_text = '\n\n'.join([
                        f"[Region {i} - {region.type}]\n{region.text}"
                        for i, region in enumerate(result['regions'], 1)
                    ])

                    # Extract invoice data
                    invoice_data = invoice_extractor.extract_from_text(page_text)
                    db_data = invoice_extractor.format_for_database(invoice_data)

                    # Add metadata
                    extraction_result = {
                        'page': result['page_number'],
                        'source_file': page_name,
                        'extraction_method': 'invoice_extractor',
                        'extracted_fields': db_data,
                        'raw_data': {
                            'items': invoice_data.get('items', []),
                            'items_count': invoice_data.get('items_count', 0),
                        }
                    }

                    # Add LLM results if available
                    if 'llm_document_type' in result:
                        extraction_result['llm_document_type'] = result['llm_document_type']
                    if 'llm_extracted_fields' in result:
                        extraction_result['llm_extracted_fields'] = result['llm_extracted_fields']
                    if 'llm_error' in result:
                        extraction_result['llm_error'] = result['llm_error']

                    # Save as JSON
                    with open(page_llm_json, 'w', encoding='utf-8') as f:
                        json.dump(extraction_result, f, indent=2, ensure_ascii=False)

                    print(f"  Page {page_num} Invoice JSON: {page_llm_json.name}")

                    # Show extracted key fields
                    if db_data.get('invoice_number'):
                        print(f"    ✓ Invoice: {db_data['invoice_number']}")
                    if db_data.get('company_name'):
                        print(f"    ✓ Company: {db_data['company_name']}")
                    if db_data.get('total_amount'):
                        print(f"    ✓ Amount: {db_data['currency']} {db_data['total_amount']}")

                except Exception as e:
                    print(f"  ✗ Invoice extraction failed: {str(e)}")

        # Save combined JSON
        print("\nCombined files:")
        json_output = output_dir / f"{input_name}_all_pages.json"

        # Convert all results to dict format
        pages_dict = []
        for result in all_results:
            result_dict = {
                'page_number': result['page_number'],
                'method': result['method'],
                'image_path': result['image_path'],
                'regions': []
            }
            for region in result['regions']:
                region_dict = {
                    'type': region.type,
                    'bbox': region.bbox,
                    'confidence': region.confidence,
                    'text': region.text,
                    'table_html': region.table_html if region.table_html else None
                }
                if hasattr(region, 'rows'):
                    region_dict['rows'] = region.rows
                if hasattr(region, 'columns'):
                    region_dict['columns'] = region.columns
                result_dict['regions'].append(region_dict)
            pages_dict.append(result_dict)

        output_data = {
            'document': input_name,
            'total_pages': len(all_results),
            'pages': pages_dict
        }

        with open(json_output, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        print(f"  All pages JSON: {json_output.name}")

        # Save extracted text for all pages
        text_output = output_dir / f"{input_name}_all_pages.txt"
        with open(text_output, 'w', encoding='utf-8') as f:
            for result in all_results:
                page_num = result['page_number']
                f.write(f"{'='*60}\n")
                f.write(f"PAGE {page_num}\n")
                f.write(f"{'='*60}\n\n")

                for i, region in enumerate(result['regions'], 1):
                    f.write(f"[Region {i} - {region.type}]\n")
                    f.write(region.text + '\n\n')

                f.write('\n\n')

        print(f"  All pages TXT: {text_output.name}")

        # Save tables from all pages
        tables_output = output_dir / f"{input_name}_all_tables.html"
        table_count = 0
        with open(tables_output, 'w', encoding='utf-8') as f:
            f.write('<html><head><meta charset="utf-8"><style>')
            f.write('table {border-collapse: collapse; margin: 20px 0;} ')
            f.write('td {border: 1px solid #ccc; padding: 5px;}')
            f.write('h2 {color: #333; margin-top: 40px;}')
            f.write('</style></head><body>')

            for result in all_results:
                page_num = result['page_number']
                page_tables = [r for r in result['regions'] if r.type == 'table' and r.table_html]

                if page_tables:
                    f.write(f'<h2>Page {page_num}</h2>')

                    for region in page_tables:
                        table_count += 1
                        f.write(f'<h3>Table {table_count}</h3>')
                        f.write(region.table_html)

            f.write('</body></html>')

        print(f"  Tables: {tables_output} ({table_count} tables)")

        # Save basic CSV summary (all pages)
        csv_summary = output_dir / f"{input_name}_summary.csv"
        with open(csv_summary, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(['Page', 'Method', 'Regions', 'Tables', 'Text_Length'])

            for result in all_results:
                page_num = result['page_number']
                method = result['method']
                region_count = len(result['regions'])
                table_count_page = sum(1 for r in result['regions'] if r.type == 'table')
                text_length = sum(len(r.text or '') for r in result['regions'])

                writer.writerow([page_num, method, region_count, table_count_page, text_length])

        print(f"  Summary CSV: {csv_summary.name}")

        # Save combined invoice extraction JSON (only if --use-llm is enabled)
        if llm_processor:
            invoice_json = output_dir / f"{input_name}_invoices.json"
            try:
                invoice_extractor = InvoiceExtractor()
                all_invoices = []

                for result in all_results:
                    page_num = result['page_number']

                    # Extract text from regions
                    page_text = '\n\n'.join([
                        f"[Region {i} - {region.type}]\n{region.text}"
                        for i, region in enumerate(result['regions'], 1)
                    ])

                    # Extract invoice data
                    invoice_data = invoice_extractor.extract_from_text(page_text)
                    db_data = invoice_extractor.format_for_database(invoice_data)

                    # Create invoice record
                    invoice_record = {
                        'page': page_num,
                        'source_file': Path(result['image_path']).stem,
                        'extracted_fields': db_data,
                        'items_count': invoice_data.get('items_count', 0),
                    }

                    # Add LLM results if available
                    if 'llm_document_type' in result:
                        invoice_record['llm_document_type'] = result['llm_document_type']

                    all_invoices.append(invoice_record)

                # Save combined JSON
                combined_data = {
                    'document': input_name,
                    'total_pages': len(all_results),
                    'invoices': all_invoices,
                    'summary': {
                        'with_invoice_number': sum(1 for inv in all_invoices if inv['extracted_fields'].get('invoice_number')),
                        'with_company': sum(1 for inv in all_invoices if inv['extracted_fields'].get('company_name')),
                        'with_amount': sum(1 for inv in all_invoices if inv['extracted_fields'].get('total_amount')),
                    }
                }

                with open(invoice_json, 'w', encoding='utf-8') as f:
                    json.dump(combined_data, f, indent=2, ensure_ascii=False)

                print(f"  Invoices JSON: {invoice_json.name}")
                print(f"    Pages with invoice no: {combined_data['summary']['with_invoice_number']}")
                print(f"    Pages with company: {combined_data['summary']['with_company']}")
                print(f"    Pages with amount: {combined_data['summary']['with_amount']}")

            except Exception as e:
                print(f"  ✗ Combined invoice extraction failed: {str(e)}")

        # Visualize if requested
        if args.visualize:
            from ocr_invoice_reader.utils.visualizer import OCRVisualizer
            import cv2
            import numpy as np

            print("\nGenerating visualizations...")

            visualizer = OCRVisualizer()

            # Initialize OCR engine for extracting detailed boxes when needed
            from paddleocr import PaddleOCR
            ocr_engine = PaddleOCR(
                use_angle_cls=False,
                lang=args.lang,
                device='cpu' if args.use_cpu else 'gpu',
                show_log=False
            )

            for result in all_results:
                page_num = result['page_number']
                image_path = result['image_path']

                # Generate output filename
                page_name = Path(image_path).stem
                viz_output = output_dir / f"{page_name}_viz.jpg"

                # Read image
                img = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), cv2.IMREAD_COLOR)

                # Prepare regions with OCR boxes
                viz_regions = []
                for region in result['regions']:
                    viz_region = {
                        'type': region.type,
                        'bbox': region.bbox,
                        'confidence': region.confidence,
                        'text': region.text,
                    }

                    # Add OCR boxes for all regions (including tables)
                    if result.get('method') == 'coordinate_based':
                        # Use existing OCR boxes from region
                        if hasattr(region, 'ocr_boxes') and region.ocr_boxes:
                            viz_region['ocr_boxes'] = region.ocr_boxes
                        else:
                            viz_region['ocr_boxes'] = []
                    else:
                        # For ppstructure_enhanced method, run OCR on this region to get detailed boxes
                        if region.text:  # Only if region has text
                            x1, y1, x2, y2 = region.bbox
                            roi = img[y1:y2, x1:x2]

                            try:
                                ocr_result = ocr_engine.ocr(roi, cls=False)
                                if ocr_result and ocr_result[0]:
                                    region_boxes = []
                                    for line in ocr_result[0]:
                                        if line:
                                            box, (text, conf) = line
                                            # Adjust box coordinates to full image
                                            adjusted_box = [[p[0] + x1, p[1] + y1] for p in box]
                                            region_boxes.append({
                                                'box': adjusted_box,
                                                'text': text,
                                                'confidence': conf
                                            })
                                    viz_region['ocr_boxes'] = region_boxes
                                else:
                                    viz_region['ocr_boxes'] = []
                            except:
                                viz_region['ocr_boxes'] = []
                        else:
                            viz_region['ocr_boxes'] = []

                    viz_regions.append(viz_region)

                # Visualize
                visualizer.save_visualization(
                    img,
                    viz_regions,
                    str(viz_output),
                    show_text=True,
                    show_boxes=True
                )
                print(f"  Page {page_num}: {viz_output.name}")

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
