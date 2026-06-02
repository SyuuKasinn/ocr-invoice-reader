"""
测试增强功能 - 使用 PaddleOCR-VL Pipeline

测试统计收集和 HTML 报告生成功能
"""
import sys
import time
from pathlib import Path

from ocr_invoice_reader.core.pipeline import Pipeline
from ocr_invoice_reader.core.config import PipelineConfig, VLConfig, IOConfig
from ocr_invoice_reader.utils.stats_collector import StatsCollector, format_stats_summary
from ocr_invoice_reader.utils.html_report import generate_html_report


def test_with_enhanced_features(pdf_path: str, output_dir: str = "test_results_enhanced"):
    """
    使用增强功能测试文档处理

    Args:
        pdf_path: PDF 文件路径
        output_dir: 输出目录
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        print(f"[ERROR] File not found: {pdf_path}")
        return False

    print("="*70)
    print(f"[TEST] Enhanced OCR Invoice Reader")
    print("="*70)
    print(f"Input: {pdf_path.name}")
    print(f"Size: {pdf_path.stat().st_size / 1024 / 1024:.2f} MB")
    print()

    try:
        # 配置 pipeline
        print("[1/4] Initializing pipeline...")
        config = PipelineConfig(
            vl=VLConfig(
                use_gpu=True,
                lang='japan',  # 日语发票
                use_doc_orientation_classify=False,
                use_doc_unwarping=False,
            ),
            io=IOConfig(
                output_dir=output_dir,
                save_markdown=True,
                save_visualization=True,
                save_per_page_json=False,  # 不保存单页 JSON（节省时间）
                inline_images_in_html=False,  # 不内嵌图像（HTML 文件更小）
            )
        )

        pipeline = Pipeline(config)
        collector = StatsCollector()

        # 开始处理
        print("[2/4] Processing document with PaddleOCR-VL...")
        collector.start_document(pdf_path.stem)
        start_time = time.time()

        # 运行 pipeline
        document = pipeline.run(str(pdf_path), max_pages=None)

        collector.end_document()
        process_time = time.time() - start_time

        print(f"      Processed {document.total_pages} page(s) in {process_time:.2f}s")
        print()

        # 收集统计
        print("[3/4] Collecting statistics...")

        # 从 DocumentResult 提取 regions 数据
        all_pages_regions = []
        for page in document.pages:
            regions = []
            for block in page.blocks:
                region = {
                    'type': block.label,
                    'bbox': block.bbox if block.bbox else [0, 0, 0, 0],
                    'confidence': block.score if block.score else 0.0,
                    'text': block.text,
                }
                regions.append(region)
            all_pages_regions.append(regions)

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

        # 生成增强的 HTML 报告
        print("[4/4] Generating enhanced HTML report...")

        # 创建输出目录
        output_path = Path(output_dir) / pdf_path.stem
        output_path.mkdir(parents=True, exist_ok=True)

        # 创建可视化图像（使用 pipeline 的可视化结果）
        vis_paths = []
        for i, page in enumerate(document.pages):
            # 如果有可视化图像，使用它；否则创建占位符
            vis_path = output_path / f"page_{i+1}_vis.png"
            if page.image_path and Path(page.image_path).exists():
                import shutil
                try:
                    shutil.copy(page.image_path, vis_path)
                except:
                    # 如果复制失败，创建占位符图像
                    import cv2
                    import numpy as np
                    placeholder = np.ones((800, 600, 3), dtype=np.uint8) * 240
                    cv2.putText(placeholder, f"Page {i+1}", (200, 400),
                               cv2.FONT_HERSHEY_SIMPLEX, 2, (100, 100, 100), 3)
                    cv2.imwrite(str(vis_path), placeholder)
            else:
                # 创建占位符
                import cv2
                import numpy as np
                placeholder = np.ones((800, 600, 3), dtype=np.uint8) * 240
                cv2.putText(placeholder, f"Page {i+1}", (200, 400),
                           cv2.FONT_HERSHEY_SIMPLEX, 2, (100, 100, 100), 3)
                cv2.imwrite(str(vis_path), placeholder)

            vis_paths.append(str(vis_path))

        # 生成 HTML
        html_path = output_path / f"{pdf_path.stem}_enhanced_report.html"
        generate_html_report(
            document_name=pdf_path.stem,
            all_pages_regions=all_pages_regions,
            image_paths=vis_paths,
            stats=stats,
            output_path=str(html_path),
        )

        print()
        print("="*70)
        print("[SUCCESS] Test completed!")
        print("="*70)
        print(f"Output directory: {output_path}")
        print(f"Enhanced HTML: {html_path}")
        print(f"Visualizations: {len(vis_paths)} images")
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
    if len(sys.argv) < 2:
        # 使用默认测试文件
        test_files = [
            r"C:\Work\SVN\trunk\SBS_GLOVIA\00.資料\INVOICE関連\インボイス見本.pdf",
            r"C:\Work\SVN\trunk\SBS_GLOVIA\00.資料\INVOICE関連\INVOICE.pdf",
        ]

        print("\n" + "="*70)
        print("[AUTO TEST] Running enhanced features test")
        print("="*70 + "\n")

        results = []
        for test_file in test_files:
            if Path(test_file).exists():
                success = test_with_enhanced_features(test_file)
                results.append((Path(test_file).name, success))
                print("\n")
            else:
                print(f"[SKIP] File not found: {test_file}\n")

        # 总结
        print("="*70)
        print("[SUMMARY] Test Results")
        print("="*70)
        for name, success in results:
            status = "[PASS]" if success else "[FAIL]"
            print(f"{status} {name}")
        print("="*70)

        passed = sum(1 for _, s in results if s)
        print(f"Result: {passed}/{len(results)} tests passed")
        print("="*70)

        sys.exit(0 if passed == len(results) else 1)
    else:
        # 使用命令行参数
        pdf_path = sys.argv[1]
        output_dir = sys.argv[2] if len(sys.argv) > 2 else "test_results_enhanced"
        success = test_with_enhanced_features(pdf_path, output_dir)
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
