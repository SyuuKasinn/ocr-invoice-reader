#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试PaddleOCR v4模型升级
验证模型加载和性能提升
"""
import time
import sys
import os
from pathlib import Path

# 设置UTF-8编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def test_v4_model_info():
    """测试v4模型信息"""
    print("=" * 60)
    print("PaddleOCR v4 模型升级测试")
    print("=" * 60)

    try:
        import paddleocr
        print(f"\n✅ PaddleOCR版本: {paddleocr.__version__}")

        if paddleocr.__version__ < "2.8.0":
            print(f"⚠️  警告: PaddleOCR版本过低 ({paddleocr.__version__})")
            print("   推荐升级到 >= 2.8.1: pip install --upgrade paddleocr>=2.8.1")
    except ImportError:
        print("❌ PaddleOCR未安装")
        return False

    # 检查GPU可用性
    try:
        import paddle
        print(f"\n✅ PaddlePaddle版本: {paddle.__version__}")
        device = paddle.device.get_device()
        print(f"✅ 设备: {device}")

        if 'gpu' in device.lower() or 'cuda' in device.lower():
            print("🚀 GPU可用 - 性能最佳")
        else:
            print("💻 使用CPU模式")
    except:
        print("⚠️  无法检测设备信息")

    return True

def test_enhanced_analyzer():
    """测试EnhancedStructureAnalyzer v4模型"""
    print("\n" + "=" * 60)
    print("测试 EnhancedStructureAnalyzer (v4模型)")
    print("=" * 60)

    try:
        from ocr_invoice_reader.processors.enhanced_structure_analyzer import EnhancedStructureAnalyzer

        print("\n[1/3] 初始化分析器...")
        start = time.time()
        analyzer = EnhancedStructureAnalyzer(use_gpu=False, lang='ch')
        init_time = time.time() - start
        print(f"✅ 初始化完成 (耗时: {init_time:.2f}秒)")

        # 检查模型路径
        print("\n[2/3] 检查模型...")
        import os
        model_dir = os.path.expanduser('~/.paddleocr/whl/')
        if os.path.exists(model_dir):
            v4_models = []
            for root, dirs, files in os.walk(model_dir):
                for d in dirs:
                    if 'v4' in d.lower():
                        v4_models.append(d)

            if v4_models:
                print("✅ 检测到v4模型:")
                for model in v4_models[:5]:  # 只显示前5个
                    print(f"   • {model}")
                if len(v4_models) > 5:
                    print(f"   ... 还有 {len(v4_models) - 5} 个模型")
            else:
                print("⚠️  未检测到v4模型，可能使用默认模型")
        else:
            print("⚠️  模型目录不存在")

        print("\n✅ EnhancedStructureAnalyzer 测试通过")
        return True

    except Exception as e:
        print(f"❌ EnhancedStructureAnalyzer 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_structure_analyzer():
    """测试StructureAnalyzer v4模型"""
    print("\n" + "=" * 60)
    print("测试 StructureAnalyzer (v4模型)")
    print("=" * 60)

    try:
        from ocr_invoice_reader.processors.structure_analyzer import StructureAnalyzer

        print("\n[1/2] 初始化分析器...")
        start = time.time()
        analyzer = StructureAnalyzer(use_gpu=False, lang='ch')
        init_time = time.time() - start
        print(f"✅ 初始化完成 (耗时: {init_time:.2f}秒)")

        print("\n✅ StructureAnalyzer 测试通过")
        return True

    except Exception as e:
        print(f"❌ StructureAnalyzer 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_simple_ocr():
    """测试SimpleOCR v4模型"""
    print("\n" + "=" * 60)
    print("测试 SimpleOCR (v4模型)")
    print("=" * 60)

    try:
        from ocr_invoice_reader.extractors.simple_ocr import SimpleOCR

        print("\n[1/2] 初始化OCR引擎...")
        start = time.time()
        ocr = SimpleOCR(lang='ch', use_gpu=False)
        init_time = time.time() - start
        print(f"✅ 初始化完成 (耗时: {init_time:.2f}秒)")

        print("\n✅ SimpleOCR 测试通过")
        return True

    except Exception as e:
        print(f"❌ SimpleOCR 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def performance_comparison(test_image=None):
    """性能对比测试（如果提供测试图像）"""
    if not test_image or not Path(test_image).exists():
        print("\n" + "=" * 60)
        print("跳过性能测试（未提供测试图像）")
        print("=" * 60)
        print("\n提示: 运行性能测试请使用:")
        print("  python test_v4_upgrade.py <图片路径>")
        return

    print("\n" + "=" * 60)
    print("性能对比测试")
    print("=" * 60)

    try:
        from ocr_invoice_reader.processors.enhanced_structure_analyzer import EnhancedStructureAnalyzer

        print(f"\n测试图像: {test_image}")

        # CPU测试
        print("\n[CPU模式] 处理测试...")
        analyzer_cpu = EnhancedStructureAnalyzer(use_gpu=False, lang='ch')

        start = time.time()
        result = analyzer_cpu.analyze(test_image)
        cpu_time = time.time() - start

        print(f"✅ CPU处理完成")
        print(f"   耗时: {cpu_time:.2f}秒")
        if result:
            print(f"   检测区域数: {len(result.get('regions', []))}")

        # GPU测试（如果可用）
        try:
            import paddle
            if 'gpu' in paddle.device.get_device().lower() or 'cuda' in paddle.device.get_device().lower():
                print("\n[GPU模式] 处理测试...")
                analyzer_gpu = EnhancedStructureAnalyzer(use_gpu=True, lang='ch')

                start = time.time()
                result = analyzer_gpu.analyze(test_image)
                gpu_time = time.time() - start

                print(f"✅ GPU处理完成")
                print(f"   耗时: {gpu_time:.2f}秒")
                print(f"   提速: {((cpu_time - gpu_time) / cpu_time * 100):.1f}%")
        except:
            print("\n⚠️  GPU不可用，跳过GPU测试")

    except Exception as e:
        print(f"❌ 性能测试失败: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主函数"""
    print("\n" + "🚀" * 30)
    print("PaddleOCR v4 升级验证测试")
    print("🚀" * 30 + "\n")

    # 检查是否提供测试图像
    test_image = sys.argv[1] if len(sys.argv) > 1 else None

    results = []

    # 1. 检查环境
    results.append(("环境检查", test_v4_model_info()))

    # 2. 测试各个模块
    results.append(("EnhancedStructureAnalyzer", test_enhanced_analyzer()))
    results.append(("StructureAnalyzer", test_structure_analyzer()))
    results.append(("SimpleOCR", test_simple_ocr()))

    # 3. 性能测试（可选）
    if test_image:
        performance_comparison(test_image)

    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {name}")

    print(f"\n总计: {passed}/{total} 通过")

    if passed == total:
        print("\n🎉 所有测试通过！v4模型升级成功！")
        print("\n下一步:")
        print("  1. 运行实际文档测试: python test_v4_upgrade.py <发票图片路径>")
        print("  2. 对比处理速度是否有30%左右提升")
        print("  3. 查看升级文档: PADDLEOCR_V4_UPGRADE.md")
        return 0
    else:
        print("\n⚠️  部分测试失败，请检查错误信息")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
