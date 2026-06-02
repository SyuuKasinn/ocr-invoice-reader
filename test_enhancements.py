"""
测试增强功能的基础脚本

验证新模块的导入和基本功能
"""
import sys
from pathlib import Path

def test_imports():
    """测试模块导入"""
    print("="*60)
    print("Testing imports...")
    print("="*60)

    try:
        from ocr_invoice_reader.utils.stats_collector import (
            StatsCollector,
            PageStats,
            DocumentStats,
            format_stats_summary
        )
        print("[OK] stats_collector imported successfully")
    except Exception as e:
        print(f"[ERROR] Failed to import stats_collector: {e}")
        return False

    try:
        from ocr_invoice_reader.utils.html_report import generate_html_report
        print("[OK] html_report imported successfully")
    except Exception as e:
        print(f"[ERROR] Failed to import html_report: {e}")
        return False

    return True


def test_stats_collector():
    """测试统计收集器"""
    print("\n" + "="*60)
    print("Testing StatsCollector...")
    print("="*60)

    try:
        from ocr_invoice_reader.utils.stats_collector import StatsCollector

        collector = StatsCollector()
        collector.start_document("test_doc")

        # 模拟处理
        import time
        collector.start_page(0)
        time.sleep(0.1)
        collector.end_page(0)

        collector.end_document()

        # 创建测试数据 - 注意是 List[List[Dict]]
        test_regions = [
            {'type': 'text', 'confidence': 0.95, 'text': 'Sample text'},
            {'type': 'table', 'confidence': 0.85, 'text': 'Table data'},
        ]

        stats = collector.collect_document_stats(
            [test_regions],  # 单页，包含多个 regions
            document_name="test_doc"
        )

        print(f"[OK] Statistics collected:")
        print(f"   - Total pages: {stats.total_pages}")
        print(f"   - Total regions: {stats.total_regions}")
        print(f"   - Processing time: {stats.total_processing_time:.3f}s")
        print(f"   - Avg confidence: {stats.avg_confidence:.2%}")

        return True

    except Exception as e:
        print(f"[ERROR] StatsCollector test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_html_generation():
    """测试 HTML 生成"""
    print("\n" + "="*60)
    print("Testing HTML generation...")
    print("="*60)

    try:
        from ocr_invoice_reader.utils.html_report import generate_html_report
        from ocr_invoice_reader.utils.stats_collector import DocumentStats

        # 创建测试数据
        test_regions = [
            {'type': 'text', 'confidence': 0.95, 'text': 'Sample text', 'bbox': [0, 0, 100, 50]},
            {'type': 'table', 'confidence': 0.85, 'text': 'Table data', 'bbox': [0, 60, 200, 150]},
        ]

        # 创建虚拟图像文件
        import cv2
        import numpy as np
        test_img = np.ones((300, 400, 3), dtype=np.uint8) * 255
        cv2.putText(test_img, "Test Image", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        cv2.imwrite("test_page.jpg", test_img)

        # 生成 HTML - 修正数据结构
        html = generate_html_report(
            document_name="test_document",
            all_pages_regions=[test_regions],  # List[List[Dict]], 外层是页面列表
            image_paths=["test_page.jpg"],
            stats=None,  # 不传统计信息进行测试
            output_path="test_report.html",
        )

        print(f"[OK] HTML report generated:")
        print(f"   - File: test_report.html")
        print(f"   - Size: {len(html)} bytes")

        # 清理测试文件
        Path("test_page.jpg").unlink(missing_ok=True)
        Path("test_report.html").unlink(missing_ok=True)

        return True

    except Exception as e:
        print(f"[ERROR] HTML generation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("\n[TEST] Testing Enhanced OCR Features\n")

    tests = [
        ("Module Imports", test_imports),
        ("StatsCollector", test_stats_collector),
        ("HTML Generation", test_html_generation),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n[ERROR] Test '{name}' crashed: {e}")
            results.append((name, False))

    # 打印总结
    print("\n" + "="*60)
    print("[SUMMARY] Test Summary")
    print("="*60)

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status}: {name}")

    print("="*60)
    print(f"Result: {passed}/{total} tests passed")
    print("="*60)

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
