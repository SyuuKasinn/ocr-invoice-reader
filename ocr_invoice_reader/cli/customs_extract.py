"""
报关数据提取命令行工具
"""
import argparse
import sys
import json
from pathlib import Path

from ocr_invoice_reader.utils.customs_extractor import CustomsDataExtractor
from ocr_invoice_reader import __version__


def main():
    """报关数据提取 CLI"""
    parser = argparse.ArgumentParser(
        prog="ocr-customs",
        description="Extract customs clearance data from OCR text files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # 从单个文本文件提取
  ocr-customs --input invoice.txt

  # 指定输出文件
  ocr-customs --input invoice.txt --output customs_data.json

  # 使用更准确的模型
  ocr-customs --input invoice.txt --model qwen2.5:3b

  # 批量处理多个文件
  ocr-customs --input invoice1.txt invoice2.txt --output-dir customs_data/

  # 直接从 OCR 结果目录处理
  ocr-customs --input results/20260514_171526/*.txt --output-dir customs_data/
        """
    )

    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')
    parser.add_argument('--input', '-i', type=str, nargs='+', required=True,
                        help='Input text file(s) from OCR')
    parser.add_argument('--output', '-o', type=str,
                        help='Output JSON file (for single file mode)')
    parser.add_argument('--output-dir', type=str,
                        help='Output directory (for batch mode)')
    parser.add_argument('--model', type=str, default='qwen2.5:3b',
                        choices=['qwen2.5:0.5b', 'qwen2.5:1.5b', 'qwen2.5:3b'],
                        help='LLM model (default: qwen2.5:3b)')
    parser.add_argument('--pretty', action='store_true',
                        help='Pretty print JSON output')
    parser.add_argument('--split-pages', action='store_true',
                        help='Split multi-page document and process each page separately (for large files)')
    parser.add_argument('--save-all-pages', action='store_true',
                        help='Save all page results separately (use with --split-pages)')

    args = parser.parse_args()

    try:
        print("="*70)
        print("Customs Data Extraction")
        print(f"Version: {__version__}")
        print(f"Model: {args.model}")
        print("="*70)

        # 创建提取器
        extractor = CustomsDataExtractor(model=args.model)

        # 单文件模式
        if len(args.input) == 1:
            input_file = args.input[0]
            print(f"\nProcessing: {input_file}")

            # 读取文本
            with open(input_file, 'r', encoding='utf-8') as f:
                text = f.read()

            # 检查是否需要分页处理
            if args.split_pages and '============================================================\nPAGE' in text:
                print("[INFO] Multi-page document detected, processing each page separately...")

                # 分割页面
                pages = text.split('============================================================\nPAGE')
                pages = [page for page in pages if page.strip()]

                print(f"[INFO] Found {len(pages)} pages")

                # 处理每页并收集结果
                page_results = []
                for i, page_text in enumerate(pages, 1):
                    print(f"\n  Processing page {i}/{len(pages)}...", end=' ')
                    try:
                        page_result = extractor.extract_customs_data(page_text)
                        if page_result['success']:
                            print("[OK]")
                            page_results.append(page_result['data'])
                        else:
                            print(f"[X] {page_result['error']}")
                    except Exception as e:
                        print(f"[X] {str(e)}")

                # 保存所有页面结果或选择最佳页面
                if page_results:
                    if args.save_all_pages:
                        # 保存所有页面结果
                        output_file = args.output if args.output else (Path(input_file).stem + '_customs_all.json')
                        all_pages_data = {
                            'total_pages': len(page_results),
                            'pages': page_results
                        }
                        with open(output_file, 'w', encoding='utf-8') as f:
                            if args.pretty:
                                json.dump(all_pages_data, f, indent=2, ensure_ascii=False)
                            else:
                                json.dump(all_pages_data, f, ensure_ascii=False)

                        print(f"\n[OK] Saved all {len(page_results)} pages to: {output_file}")
                        result = {'success': True, 'data': all_pages_data}
                    else:
                        # 计算每页的完整度得分
                        def completeness_score(data):
                            score = 0
                            # 关键字段权重
                            if data.get('tracking_number'): score += 20
                            if data.get('invoice_number'): score += 10
                            if data.get('invoice_date'): score += 5

                            # Shipper信息
                            shipper = data.get('shipper', {})
                            if shipper.get('company_name'): score += 15
                            if shipper.get('address'): score += 10
                            if shipper.get('country'): score += 5

                            # Receiver信息
                            receiver = data.get('receiver', {})
                            if receiver.get('company_name'): score += 15
                            if receiver.get('address'): score += 10
                            if receiver.get('country'): score += 5

                            # Items信息（有效的items）
                            items = data.get('items', [])
                            valid_items = [i for i in items if i.get('description') and i.get('quantity')]
                            score += min(len(valid_items) * 5, 20)  # 最多20分

                            # Payment信息
                            payment = data.get('payment', {})
                            if payment.get('total_amount'): score += 10

                            return score

                        # 选择得分最高的页面
                        result_data = max(page_results, key=completeness_score)
                        best_score = completeness_score(result_data)

                        result = {'success': True, 'data': result_data}
                        print(f"\n[OK] Combined results from {len(page_results)} pages (best score: {best_score})")
                else:
                    result = {'success': False, 'error': 'No pages processed successfully'}
            else:
                # 正常处理整个文件
                result = extractor.extract_customs_data(text)

            if result['success']:
                print("[OK] Extraction successful")

                # 确定输出文件
                if args.output:
                    output_file = args.output
                else:
                    output_file = Path(input_file).stem + '_customs.json'

                # 保存结果
                with open(output_file, 'w', encoding='utf-8') as f:
                    if args.pretty:
                        json.dump(result['data'], f, indent=2, ensure_ascii=False)
                    else:
                        json.dump(result['data'], f, ensure_ascii=False)

                print(f"[OK] Saved to: {output_file}")

                # 显示部分数据
                if result['data'].get('tracking_number'):
                    print(f"\nTracking Number: {result['data']['tracking_number']}")
                if result['data'].get('invoice_number'):
                    print(f"Invoice Number: {result['data']['invoice_number']}")
                if result['data'].get('shipper'):
                    print(f"Shipper: {result['data']['shipper'].get('company_name', 'N/A')}")
                if result['data'].get('receiver'):
                    print(f"Receiver: {result['data']['receiver'].get('company_name', 'N/A')}")

            else:
                print(f"[X] Extraction failed: {result['error']}")
                return 1

        # 批量模式
        else:
            print(f"\nBatch mode: {len(args.input)} files")

            # 确定输出目录
            if args.output_dir:
                output_dir = Path(args.output_dir)
            else:
                output_dir = Path('customs_data')

            output_dir.mkdir(parents=True, exist_ok=True)
            print(f"Output directory: {output_dir}")

            # 处理每个文件
            success_count = 0
            fail_count = 0

            for i, input_file in enumerate(args.input, 1):
                print(f"\n[{i}/{len(args.input)}] Processing: {input_file}")

                try:
                    # 读取文本
                    with open(input_file, 'r', encoding='utf-8') as f:
                        text = f.read()

                    # 提取数据
                    result = extractor.extract_customs_data(text)

                    if result['success']:
                        # 保存结果
                        output_file = output_dir / (Path(input_file).stem + '_customs.json')
                        with open(output_file, 'w', encoding='utf-8') as f:
                            if args.pretty:
                                json.dump(result['data'], f, indent=2, ensure_ascii=False)
                            else:
                                json.dump(result['data'], f, ensure_ascii=False)

                        print(f"  [OK] Saved to: {output_file}")
                        success_count += 1
                    else:
                        print(f"  [X] Failed: {result['error']}")
                        fail_count += 1

                except Exception as e:
                    print(f"  [X] Error: {e}")
                    fail_count += 1

            # 统计
            print("\n" + "="*70)
            print(f"Batch processing complete")
            print(f"  Success: {success_count}/{len(args.input)}")
            print(f"  Failed: {fail_count}/{len(args.input)}")
            print("="*70)

            if fail_count > 0:
                return 1

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
