"""
增强的文档提取示例

演示如何使用统计收集和 HTML 报告生成功能
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ocr_invoice_reader.extractors.document_extractor import DocumentExtractor
from ocr_invoice_reader.utils.stats_collector import StatsCollector, format_stats_summary
from ocr_invoice_reader.utils.html_report import generate_html_report


def extract_with_stats(image_path: str, output_dir: str = "results"):
    """
    使用统计收集和 HTML 报告生成的文档提取

    Args:
        image_path: 输入图像或 PDF 路径
        output_dir: 输出目录
    """
    print(f"📄 Processing: {image_path}\n")

    # 创建输出目录
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # 初始化提取器和统计收集器
    extractor = DocumentExtractor(use_gpu=True, lang='japan')
    collector = StatsCollector()

    # 开始计时
    collector.start_document(Path(image_path).stem)

    # 如果是 PDF，需要处理多页
    if Path(image_path).suffix.lower() == '.pdf':
        temp_images = extractor.file_processor.process_file(image_path)
        image_paths = temp_images
    else:
        image_paths = [image_path]

    all_pages_regions = []
    all_vis_paths = []

    # 逐页处理
    for i, img_path in enumerate(image_paths):
        print(f"  Processing page {i + 1}/{len(image_paths)}...")

        # 开始页面计时
        collector.start_page(i)

        # 结构分析
        structure_result = extractor.structure_analyzer.analyze(
            img_path,
            visualize=True
        )

        regions = structure_result['regions']
        all_pages_regions.append(regions)

        # 保存可视化结果
        vis_path = output_path / f"page_{i+1}_vis.jpg"
        if structure_result.get('visualization'):
            import shutil
            shutil.copy(structure_result['visualization'], vis_path)
        all_vis_paths.append(str(vis_path))

        # 结束页面计时
        collector.end_page(i)

        print(f"    ✓ Page {i + 1}: {len(regions)} regions detected")

    # 结束文档计时
    collector.end_document()

    # 收集统计信息
    stats = collector.collect_document_stats(
        all_pages_regions,
        document_name=Path(image_path).stem
    )

    # 打印统计摘要
    print("\n" + "="*60)
    print("📊 Statistics Summary")
    print("="*60)
    print(format_stats_summary(stats))
    print("="*60 + "\n")

    # 生成 HTML 报告
    html_path = output_path / f"{Path(image_path).stem}_report.html"
    generate_html_report(
        document_name=Path(image_path).stem,
        all_pages_regions=all_pages_regions,
        image_paths=all_vis_paths,
        stats=stats,
        output_path=str(html_path),
    )

    print(f"✅ Processing complete!")
    print(f"   Output directory: {output_path}")
    print(f"   HTML report: {html_path}")

    return stats


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("Usage: python enhanced_extraction_example.py <input_file> [output_dir]")
        print("\nExample:")
        print("  python enhanced_extraction_example.py invoice.pdf")
        print("  python enhanced_extraction_example.py document.jpg results/")
        sys.exit(1)

    input_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "results"

    if not Path(input_file).exists():
        print(f"❌ Error: File not found: {input_file}")
        sys.exit(1)

    try:
        extract_with_stats(input_file, output_dir)
    except KeyboardInterrupt:
        print("\n\n❌ Interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
