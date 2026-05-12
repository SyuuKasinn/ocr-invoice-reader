"""
Raw PP-Structure output CLI (original format)
"""
import argparse
import sys
import io
import json
from pathlib import Path

# Fix Windows encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from ocr_invoice_reader.processors.structure_analyzer import StructureAnalyzer
from ocr_invoice_reader import __version__


def main():
    """CLI for raw PP-Structure output"""
    parser = argparse.ArgumentParser(
        prog="ocr-raw",
        description="PP-Structure Raw Output (Original Format)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze document structure
  ocr-raw --image invoice.pdf --visualize

  # Use CPU mode
  ocr-raw --image invoice.jpg --use-cpu

  # Save to JSON
  ocr-raw --image doc.pdf --output result.json
        """
    )

    # Version
    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {__version__}'
    )

    # Input
    parser.add_argument(
        '--image',
        type=str,
        required=True,
        help='Image or PDF file'
    )

    # Output
    parser.add_argument(
        '--output-dir',
        type=str,
        default='results',
        help='Output directory (default: results/)'
    )

    # Processing options
    parser.add_argument(
        '--visualize',
        action='store_true',
        help='Generate visualization image'
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
        print("="*60)
        print("PP-Structure Raw Output")
        print(f"Version: {__version__}")
        print("="*60)

        # Check if file needs conversion
        from ocr_invoice_reader.processors.file_handler import FileProcessor

        file_processor = FileProcessor()
        images = file_processor.process_file(args.image)

        if not images:
            print(f"Error: Cannot process file {args.image}")
            return 1

        print(f"\nTotal pages: {len(images)}")

        # Initialize analyzer
        analyzer = StructureAnalyzer(
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
            result = analyzer.analyze(image_path, visualize=False)  # We'll visualize later
            result['page_number'] = page_idx
            all_results.append(result)

        # Display summary
        print("\n" + "="*60)
        print("PP-STRUCTURE RESULTS SUMMARY")
        print("="*60)
        print(f"Total pages: {len(all_results)}")

        total_regions = sum(len(r['regions']) for r in all_results)
        print(f"Total regions: {total_regions}")
        print("="*60)

        # Display results for each page
        for result in all_results:
            page_num = result['page_number']
            print(f"\n[Page {page_num}]")
            print(f"  Method: {result['method']}")
            print(f"  Regions: {len(result['regions'])}")

            for i, region in enumerate(result['regions'], 1):
                print(f"    Region {i}: {region.type}")

        # Create timestamped subfolder
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path(args.output_dir) / timestamp
        output_dir.mkdir(parents=True, exist_ok=True)

        input_name = Path(args.image).stem

        # Save results
        print("\n" + "="*60)
        print("Saving results...")
        print("="*60)

        # Save individual page files
        print("\nIndividual page files:")
        for result in all_results:
            page_num = result['page_number']
            page_name = Path(result['image_path']).stem

            # Prepare page data
            page_data = {
                'page_number': page_num,
                'method': result['method'],
                'image_path': result['image_path'],
                'regions': []
            }

            for region in result['regions']:
                page_data['regions'].append({
                    'type': region.type,
                    'bbox': region.bbox,
                    'confidence': region.confidence,
                    'text': region.text,
                    'table_html': region.table_html if region.table_html else None,
                    'ocr_count': len(region.ocr_results)
                })

            # Individual JSON
            page_json = output_dir / f"{page_name}.json"
            with open(page_json, 'w', encoding='utf-8') as f:
                json.dump(page_data, f, indent=2, ensure_ascii=False)
            print(f"  Page {page_num} JSON: {page_json.name}")

            # Individual TXT
            page_txt = output_dir / f"{page_name}.txt"
            page_text = analyzer.extract_all_text(result)
            with open(page_txt, 'w', encoding='utf-8') as f:
                f.write(f"PAGE {page_num}\n")
                f.write(f"{'='*60}\n\n")
                f.write(page_text)
            print(f"  Page {page_num} TXT: {page_txt.name}")

        # Save combined JSON
        print("\nCombined files:")
        json_output = output_dir / f"{input_name}_all_pages.json"
        output_data = {
            'document': input_name,
            'total_pages': len(all_results),
            'pages': []
        }

        for result in all_results:
            page_data = {
                'page_number': result['page_number'],
                'method': result['method'],
                'regions': []
            }

            for region in result['regions']:
                page_data['regions'].append({
                    'type': region.type,
                    'bbox': region.bbox,
                    'confidence': region.confidence,
                    'text': region.text,
                    'table_html': region.table_html if region.table_html else None,
                    'ocr_count': len(region.ocr_results)
                })

            output_data['pages'].append(page_data)

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

                page_text = analyzer.extract_all_text(result)
                f.write(page_text)
                f.write('\n\n')

        print(f"  All pages TXT: {text_output.name}")

        # Visualize if requested
        if args.visualize:
            from ocr_invoice_reader.utils.visualizer import OCRVisualizer
            import cv2
            import numpy as np

            print("\nGenerating visualizations...")

            visualizer = OCRVisualizer()

            for result in all_results:
                page_num = result['page_number']
                image_path = result['image_path']

                page_name = Path(image_path).stem
                viz_output = output_dir / f"{page_name}_viz.jpg"

                # Read image
                img = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), cv2.IMREAD_COLOR)

                # Prepare regions for visualization
                viz_regions = []
                for region in result['regions']:
                    viz_region = {
                        'type': region.type,
                        'bbox': region.bbox,
                        'confidence': region.confidence,
                        'text': region.text,
                        'ocr_boxes': []
                    }

                    # Add OCR boxes if available
                    if hasattr(region, 'ocr_results') and region.ocr_results:
                        for ocr_item in region.ocr_results:
                            viz_region['ocr_boxes'].append({
                                'box': ocr_item.get('box', []),
                                'text': ocr_item.get('text', ''),
                                'confidence': ocr_item.get('confidence', 0.0)
                            })

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
