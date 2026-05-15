"""
Parallel Enhanced extraction CLI with pipeline processing
OCR and LLM run in parallel pipeline for maximum performance
"""
import argparse
import sys
import io
import json
import csv
import time
import threading
from queue import Queue
from pathlib import Path
from datetime import datetime
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed

from ocr_invoice_reader.processors.enhanced_structure_analyzer import EnhancedStructureAnalyzer
from ocr_invoice_reader.processors.file_handler import FileProcessor
from ocr_invoice_reader.utils.invoice_extractor_v2 import InvoiceExtractorV2
from ocr_invoice_reader.utils.llm_invoice_extractor import LLMInvoiceExtractor, validate_extraction_result
from ocr_invoice_reader import __version__


class ParallelPipeline:
    """Pipeline processor for parallel OCR and LLM processing"""

    def __init__(self, analyzer, llm_processor=None, max_workers=3):
        self.analyzer = analyzer
        self.llm_processor = llm_processor
        self.max_workers = max_workers
        self.results = {}
        self.timings = {}

    def process_page_ocr(self, page_idx, image_path):
        """Stage 1: OCR processing"""
        start = time.time()

        print(f"  [Page {page_idx}] 🔍 OCR started...")

        result = self.analyzer.analyze(image_path)
        result['page_number'] = page_idx
        result['image_path'] = image_path

        ocr_time = time.time() - start

        print(f"  [Page {page_idx}] ✓ OCR completed in {ocr_time:.2f}s")

        return page_idx, result, ocr_time

    def process_page_llm(self, page_idx, result):
        """Stage 2: LLM processing (classification + extraction)"""
        if not self.llm_processor:
            return page_idx, result, 0

        start = time.time()

        print(f"  [Page {page_idx}] 🤖 LLM extraction started...")

        try:
            # Extract all text from regions
            all_text = '\n'.join([
                r.text for r in result['regions']
                if hasattr(r, 'text') and r.text
            ])

            if all_text.strip():
                # Combined extraction (classification + invoice data in ONE call)
                llm_extractor = LLMInvoiceExtractor(self.llm_processor)
                combined_result = llm_extractor.extract_with_classification(all_text)

                if combined_result:
                    # Add classification result
                    result['llm_document_type'] = {
                        'type': combined_result.get('document_type'),
                        'confidence': combined_result.get('confidence')
                    }

                    # Process invoice data if available
                    invoice_data = combined_result.get('invoice_data')
                    if invoice_data:
                        # Validate LLM result
                        is_valid, issues = validate_extraction_result(invoice_data)

                        if is_valid:
                            result['llm_invoice_data'] = invoice_data
                            result['llm_extraction_method'] = 'llm'
                            print(f"  [Page {page_idx}] ✓ LLM extraction successful")
                        else:
                            result['llm_validation_issues'] = issues
                            print(f"  [Page {page_idx}] ⚠ LLM validation failed: {', '.join(issues)}")
                            print(f"  [Page {page_idx}] → Will use regex fallback")

                    print(f"  [Page {page_idx}] ✓ Document type: {combined_result.get('document_type')}")
                else:
                    print(f"  [Page {page_idx}] ⚠ LLM returned no data")

        except Exception as e:
            print(f"  [Page {page_idx}] ✗ LLM error: {str(e)}")
            result['llm_error'] = str(e)

        llm_time = time.time() - start
        print(f"  [Page {page_idx}] ✓ LLM completed in {llm_time:.2f}s")

        return page_idx, result, llm_time

    def process_page_invoice_extraction(self, page_idx, result):
        """Stage 3: Invoice extraction (LLM or regex fallback)"""
        start = time.time()

        try:
            # Extract text from regions
            page_text = '\n\n'.join([
                f"[Region {i} - {region.type}]\n{region.text}"
                for i, region in enumerate(result['regions'], 1)
            ])

            # Check if LLM already extracted invoice data
            if result.get('llm_invoice_data'):
                llm_extractor = LLMInvoiceExtractor(self.llm_processor)
                db_data = llm_extractor.format_for_database(result['llm_invoice_data'])
                extraction_method = 'llm'
                print(f"  [Page {page_idx}] ✓ Using LLM extracted data")
            else:
                # Fallback to regex extraction
                print(f"  [Page {page_idx}] → Using regex extraction")
                invoice_extractor = InvoiceExtractorV2()
                invoice_data = invoice_extractor.extract_from_text(page_text)
                db_data = invoice_extractor.format_for_database(invoice_data)
                extraction_method = 'regex_fallback'

                # Add raw item data
                result['invoice_items'] = invoice_data.get('items', [])
                result['invoice_items_count'] = invoice_data.get('items_count', 0)

            result['invoice_extracted_fields'] = db_data
            result['invoice_extraction_method'] = extraction_method

        except Exception as e:
            print(f"  [Page {page_idx}] ✗ Invoice extraction error: {str(e)}")
            result['invoice_extraction_error'] = str(e)

        extraction_time = time.time() - start

        return page_idx, result, extraction_time

    def process_all_pages_parallel(self, images):
        """
        Process all pages with parallel pipeline:
        - OCR runs in parallel for all pages
        - LLM runs in parallel as OCR completes
        - Invoice extraction runs after LLM
        """
        all_results = [None] * len(images)
        all_timings = {}

        print("\n" + "="*60)
        print("🚀 PARALLEL PIPELINE PROCESSING")
        print("="*60)

        # Stage 1: Parallel OCR for all pages
        print("\n📊 Stage 1: OCR Processing (Parallel)")
        print("-"*60)

        ocr_start = time.time()

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            ocr_futures = {
                executor.submit(self.process_page_ocr, idx, img): idx
                for idx, img in enumerate(images, 1)
            }

            for future in as_completed(ocr_futures):
                page_idx, result, ocr_time = future.result()
                all_results[page_idx - 1] = result
                all_timings[page_idx] = {'ocr': ocr_time, 'llm': 0, 'extraction': 0}

        ocr_total_time = time.time() - ocr_start
        print(f"\n✓ All OCR completed in {ocr_total_time:.2f}s")

        # Stage 2: Parallel LLM processing (if enabled)
        if self.llm_processor:
            print("\n🤖 Stage 2: LLM Processing (Parallel)")
            print("-"*60)

            llm_start = time.time()

            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                llm_futures = {
                    executor.submit(self.process_page_llm, idx, result): idx
                    for idx, result in enumerate(all_results, 1)
                }

                for future in as_completed(llm_futures):
                    page_idx, result, llm_time = future.result()
                    all_results[page_idx - 1] = result
                    all_timings[page_idx]['llm'] = llm_time

            llm_total_time = time.time() - llm_start
            print(f"\n✓ All LLM processing completed in {llm_total_time:.2f}s")

        # Stage 3: Invoice extraction (sequential, fast)
        if self.llm_processor:
            print("\n📄 Stage 3: Invoice Data Formatting")
            print("-"*60)

            extraction_start = time.time()

            for idx, result in enumerate(all_results, 1):
                page_idx, result, extraction_time = self.process_page_invoice_extraction(idx, result)
                all_results[page_idx - 1] = result
                all_timings[page_idx]['extraction'] = extraction_time

            extraction_total_time = time.time() - extraction_start
            print(f"\n✓ All invoice extraction completed in {extraction_total_time:.2f}s")

        # Calculate total processing time per page
        for page_idx, result in enumerate(all_results, 1):
            timing = all_timings[page_idx]
            total_page_time = timing['ocr'] + timing['llm'] + timing['extraction']
            result['processing_time'] = total_page_time
            result['timing_breakdown'] = timing

        return all_results, all_timings


def main():
    """Parallel enhanced extraction CLI"""
    # Fix Windows encoding
    if sys.platform == 'win32':
        try:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        except (AttributeError, ValueError):
            pass

    parser = argparse.ArgumentParser(
        prog="ocr-enhanced-parallel",
        description="Parallel Enhanced OCR with Pipeline Processing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Parallel processing (faster)
  ocr-enhanced-parallel --image invoice.pdf --use-llm

  # Control parallelism
  ocr-enhanced-parallel --image invoice.pdf --use-llm --workers 4
        """
    )

    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')
    parser.add_argument('--image', type=str, required=True, help='Image or PDF file')
    parser.add_argument('--output-dir', type=str, default='results', help='Output directory')
    parser.add_argument('--visualize', action='store_true', help='Generate visualization')
    parser.add_argument('--use-cpu', action='store_true', help='Force CPU mode')
    parser.add_argument('--lang', type=str, default='ch', choices=['ch', 'en', 'japan', 'korean', 'latin'], help='OCR language')
    parser.add_argument('--use-llm', action='store_true', help='Enable LLM post-processing')
    parser.add_argument('--llm-model', type=str, default='7b', choices=['3b', '7b', '14b'], help='LLM model size (3b/7b/14b)')
    parser.add_argument('--llm-quantization', type=str, default='int4', choices=['int4', 'int8', 'none'], help='Quantization method (GPU only)')
    parser.add_argument('--workers', type=int, default=3, help='Max parallel workers (default: 3)')

    args = parser.parse_args()

    try:
        overall_start = time.time()

        print("="*60)
        print("🚀 Parallel Enhanced Document Extraction")
        print(f"Version: {__version__}")
        print(f"⏱ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Workers: {args.workers}")
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
            from ocr_invoice_reader.utils.qwen_direct_processor import create_qwen_processor
            from ocr_invoice_reader.utils.environment import EnvironmentConfig

            env = EnvironmentConfig()
            use_gpu = not args.use_cpu and env.gpu_available
            quantization = None if args.llm_quantization == 'none' else args.llm_quantization

            print(f"\nInitializing Qwen LLM ({args.llm_model.upper()})...")
            print(f"  Device: {'GPU' if use_gpu else 'CPU'}")
            if use_gpu and quantization:
                print(f"  Quantization: {quantization}")

            llm_processor = create_qwen_processor(
                model_size=args.llm_model,
                use_gpu=use_gpu,
                quantization=quantization if use_gpu else None
            )

            if llm_processor:
                print(f"✓ LLM ready: Qwen2.5-{args.llm_model.upper()}")
            else:
                print("✗ LLM initialization failed")

        # Create parallel pipeline
        pipeline = ParallelPipeline(analyzer, llm_processor, max_workers=args.workers)

        # Process all pages in parallel
        processing_start = time.time()
        all_results, all_timings = pipeline.process_all_pages_parallel(images)
        processing_time = time.time() - processing_start

        # Create output directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path(args.output_dir) / timestamp
        output_dir.mkdir(parents=True, exist_ok=True)

        input_name = Path(args.image).stem

        # Save results (same format as serial version)
        print("\n" + "="*60)
        print("💾 Saving results...")
        print("="*60)

        # Save individual page files
        for result in all_results:
            page_num = result['page_number']
            page_name = Path(result['image_path']).stem

            # JSON
            result_dict = {
                'page_number': result['page_number'],
                'method': result['method'],
                'image_path': result['image_path'],
                'processing_time': result.get('processing_time', 0),
                'timing_breakdown': result.get('timing_breakdown', {}),
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
                result_dict['regions'].append(region_dict)

            # Add LLM results
            if 'llm_document_type' in result:
                result_dict['llm_document_type'] = result['llm_document_type']
            if 'llm_error' in result:
                result_dict['llm_error'] = result['llm_error']

            page_json = output_dir / f"{page_name}.json"
            with open(page_json, 'w', encoding='utf-8') as f:
                json.dump(result_dict, f, indent=2, ensure_ascii=False)

            # TXT
            page_txt = output_dir / f"{page_name}.txt"
            with open(page_txt, 'w', encoding='utf-8') as f:
                f.write(f"PAGE {page_num}\n{'='*60}\n\n")
                for i, region in enumerate(result['regions'], 1):
                    f.write(f"[Region {i} - {region.type}]\n{region.text}\n\n")

            # Invoice extraction JSON
            if llm_processor and result.get('invoice_extracted_fields'):
                page_llm_json = output_dir / f"{page_name}_llm.json"

                extraction_result = {
                    'page': result['page_number'],
                    'source_file': page_name,
                    'extraction_method': result.get('invoice_extraction_method'),
                    'extracted_fields': result['invoice_extracted_fields'],
                    'processing_time': result.get('processing_time', 0),
                    'timing_breakdown': result.get('timing_breakdown', {})
                }

                if result.get('llm_validation_issues'):
                    extraction_result['llm_validation_issues'] = result['llm_validation_issues']
                if result.get('invoice_items'):
                    extraction_result['raw_data'] = {
                        'items': result['invoice_items'],
                        'items_count': result['invoice_items_count']
                    }
                if 'llm_document_type' in result:
                    extraction_result['llm_document_type'] = result['llm_document_type']

                with open(page_llm_json, 'w', encoding='utf-8') as f:
                    json.dump(extraction_result, f, indent=2, ensure_ascii=False)

                print(f"  Page {page_num}: {page_llm_json.name}")

                # Show key fields
                fields = result['invoice_extracted_fields']
                if fields.get('invoice_number'):
                    print(f"    ✓ Invoice: {fields['invoice_number']}")
                if fields.get('total_amount'):
                    print(f"    ✓ Amount: {fields['currency']} {fields['total_amount']}")

        # Performance summary
        print("\n" + "="*60)
        print("⚡ PERFORMANCE SUMMARY")
        print("="*60)

        # Calculate statistics
        ocr_times = [t['ocr'] for t in all_timings.values()]
        llm_times = [t['llm'] for t in all_timings.values()]
        extraction_times = [t['extraction'] for t in all_timings.values()]

        print(f"Total processing time:    {processing_time:.2f}s ({processing_time/60:.1f} min)")
        print(f"Average per page:         {processing_time/len(all_results):.2f}s")
        print(f"\nStage breakdown:")
        print(f"  OCR (parallel):         {sum(ocr_times):.2f}s total, avg {sum(ocr_times)/len(ocr_times):.2f}s/page")
        if llm_times and sum(llm_times) > 0:
            print(f"  LLM (parallel):         {sum(llm_times):.2f}s total, avg {sum(llm_times)/len(llm_times):.2f}s/page")
            print(f"  Extraction:             {sum(extraction_times):.2f}s total")

        # Estimate serial time for comparison
        if llm_processor:
            estimated_serial = sum(ocr_times) + sum(llm_times) + sum(extraction_times)
            speedup = estimated_serial / processing_time
            print(f"\nEstimated serial time:    {estimated_serial:.2f}s")
            print(f"Speedup factor:           {speedup:.1f}x faster")

        # Invoice extraction summary
        if llm_processor:
            llm_count = sum(1 for r in all_results if r.get('invoice_extraction_method') == 'llm')
            regex_count = sum(1 for r in all_results if r.get('invoice_extraction_method') == 'regex_fallback')
            print(f"\nInvoice extraction:")
            print(f"  LLM extracted:          {llm_count} pages")
            print(f"  Regex fallback:         {regex_count} pages")

        # Final summary
        overall_elapsed = time.time() - overall_start
        print("\n" + "="*60)
        print("✓ PROCESSING COMPLETE")
        print("="*60)
        print(f"Total elapsed time:       {overall_elapsed:.2f}s ({overall_elapsed/60:.1f} min)")
        print(f"Output directory:         {output_dir}")
        print(f"Finished at:              {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
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
