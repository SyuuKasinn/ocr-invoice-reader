"""
完整集成测试 - 测试增强功能的实际效果

使用真实的发票 PDF 进行测试
"""
import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from ocr_invoice_reader.extractors.document_extractor import DocumentExtractor
from ocr_invoice_reader.utils.stats_collector import StatsCollector, format_stats_summary
from ocr_invoice_reader.utils.html_report import generate_html_report


def test_invoice_extraction(pdf_path: str, output_dir: str = "test_results"):
    """
    完整测试：提取发票信息并生成增强报告

    Args:
        pdf_path: PDF 文件路径
        output_dir: 输出目录
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        print(f"[ERROR] File not found: {pdf_path}")
        return False

    print("="*70)
    print(f"[TEST] Testing Invoice Extraction")
    print("="*70)
    print(f"Input: {pdf_path.name}")
    print(f"Size: {pdf_path.stat().st_size / 1024 / 1024:.2f} MB")
    print()

    # 创建输出目录
    output_path = Path(output_dir) / pdf_path.stem
    output_path.mkdir(parents=True, exist_ok=True)

    try:
        # 初始化
        print("[1/5] Initializing extractor...")
        extractor = DocumentExtractor(use_gpu=True, lang='japan')
        collector = StatsCollector()

        # 开始处理
        print("[2/5] Processing document...")
        collector.start_document(pdf_path.stem)
        start_time = time.time()

        # 转换 PDF
        temp_images = extractor.file_processor.process_file(str(pdf_path))
        print(f"      Converted to {len(temp_images)} page(s)")

        all_pages_regions = []
        all_vis_paths = []

        # 逐页处理
        for i, img_path in enumerate(temp_images):
            print(f"[3/5] Processing page {i + 1}/{len(temp_images)}...", end=" ")
            page_start = time.time()

            collector.start_page(i)

            # 结构分析
            structure_result = extractor.structure_analyzer.analyze(
                img_path,
                visualize=True
            )

            regions = structure_result['regions']
            all_pages_regions.append(regions)

            # 保存可视化
            vis_path = output_path / f"page_{i+1}_visualization.jpg"
            if structure_result.get('visualization'):
                import shutil
                shutil.copy(structure_result['visualization'], vis_path)
            all_vis_paths.append(str(vis_path))

            collector.end_page(i)

            page_time = time.time() - page_start
            print(f"{len(regions)} regions ({page_time:.2f}s)")

        collector.end_document()

        # 收集统计
        print("[4/5] Collecting statistics...")
        stats = collector.collect_document_stats(
            all_pages_regions,
            document_name=pdf_path.stem
        )

        # 打印统计
        print()
        print("-"*70)
        print(format_stats_summary(stats))
        print("-"*70)
        print()

        # 生成 HTML 报告
        print("[5/5] Generating HTML report...")
        html_path = output_path / f"{pdf_path.stem}_report.html"
        generate_html_report(
            document_name=pdf_path.stem,
            all_pages_regions=all_pages_regions,
            image_paths=all_vis_paths,
            stats=stats,
            output_path=str(html_path),
        )

        total_time = time.time() - start_time

        print()
        print("="*70)
        print("[SUCCESS] Test completed!")
        print("="*70)
        print(f"Total time: {total_time:.2f}s")
        print(f"Output directory: {output_path}")
        print(f"HTML report: {html_path}")
        print(f"Visualizations: {len(all_vis_paths)} images")
        print("="*70)

        return True

    except Exception as e:
        print()
        print("="*70)
        print(f"[FAILED] Test failed: {e}")
        print("="*70)
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="Full integration test")
    parser.add_argument("pdf_path", help="Path to PDF file")
    parser.add_argument("-o", "--output", default="test_results", help="Output directory")

    args = parser.parse_args()

    success = test_invoice_extraction(args.pdf_path, args.output)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    # 如果没有命令行参数，使用默认测试文件
    if len(sys.argv) == 1:
        test_files = [
            r"C:\Work\SVN\trunk\SBS_GLOVIA\00.資料\INVOICE関連\インボイス見本.pdf",
            r"C:\Work\SVN\trunk\SBS_GLOVIA\00.資料\INVOICE関連\INVOICE.pdf",
        ]

        print("\n" + "="*70)
        print("[AUTO TEST] Running tests on default files")
        print("="*70 + "\n")

        results = []
        for test_file in test_files:
            if Path(test_file).exists():
                print(f"\n[TEST FILE] {Path(test_file).name}\n")
                success = test_invoice_extraction(test_file)
                results.append((Path(test_file).name, success))
                print("\n")
            else:
                print(f"[SKIP] File not found: {test_file}\n")
                results.append((Path(test_file).name, False))

        # 总结
        print("\n" + "="*70)
        print("[SUMMARY] Test Results")
        print("="*70)
        for name, success in results:
            status = "[PASS]" if success else "[FAIL]"
            print(f"{status} {name}")
        print("="*70)

        passed = sum(1 for _, s in results if s)
        print(f"Result: {passed}/{len(results)} tests passed")
        print("="*70 + "\n")

        sys.exit(0 if passed == len(results) else 1)
    else:
        main()
