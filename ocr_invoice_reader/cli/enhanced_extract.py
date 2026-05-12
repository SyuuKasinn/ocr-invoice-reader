"""
Enhanced extraction CLI with better table detection
"""
import argparse
import sys
import io
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict

# Fix Windows encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from ocr_invoice_reader.processors.enhanced_structure_analyzer import EnhancedStructureAnalyzer
from ocr_invoice_reader.processors.file_handler import FileProcessor
from ocr_invoice_reader import __version__


def main():
    """Enhanced extraction CLI"""
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

        # Process all pages
        all_results = []
        for page_idx, image_path in enumerate(images, 1):
            print(f"\n{'='*60}")
            print(f"Processing page {page_idx}/{len(images)}: {Path(image_path).name}")
            print('='*60)

            # Analyze
            result = analyzer.analyze(image_path)
            result['page_number'] = page_idx
            all_results.append(result)

        # Create output directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path(args.output_dir) / timestamp
        output_dir.mkdir(parents=True, exist_ok=True)

        input_name = Path(args.image).stem

        # Display summary
        print("\n" + "="*60)
        print("EXTRACTION SUMMARY")
        print("="*60)
        print(f"Total pages: {len(all_results)}")

        total_regions = sum(len(r['regions']) for r in all_results)
        total_tables = sum(1 for r in all_results for region in r['regions'] if region.type == 'table')

        print(f"Total regions: {total_regions}")
        print(f"Total tables: {total_tables}")
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
                result_dict['regions'].append(region_dict)

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
                        # Use existing OCR boxes
                        if 'ocr_boxes' in result:
                            region_boxes = []
                            x1, y1, x2, y2 = region.bbox
                            for box in result['ocr_boxes']:
                                bx1, by1, bx2, by2 = box['bbox']
                                # Check if box center is inside region
                                cx, cy = (bx1 + bx2) / 2, (by1 + by2) / 2
                                if x1 <= cx <= x2 and y1 <= cy <= y2:
                                    region_boxes.append(box)
                            viz_region['ocr_boxes'] = region_boxes
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
