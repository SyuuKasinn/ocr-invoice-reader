#!/usr/bin/env python
"""测试报关数据提取功能"""
import sys
import json
sys.stdout.reconfigure(encoding='utf-8')

from ocr_invoice_reader.utils.customs_extractor import CustomsDataExtractor

# 示例发票文本（从你的 OCR 结果中提取）
sample_invoice = """
INVOICE

Tracking No: 506-538-938-065
INV No: KTB0911-X52-S01-24538
DATE: 24-Sep-25

Importer: SANEI SANSYOU CORPORATION
Address: 1-80 Komagabayashiminamicho, Nagata Ward, Kobe, Hyogo, 653-0045
Attn: MR. GAO PENGFEI
Tel: 0081-078-200-5562
FAX: 0081-078-200-5571

Shipper Address:
Dalian Xinghua Trading Co., LTD
1-3, NO.4, Yihuayuan Xinglin, Economic & Technical Development Zone, Dalian
CHINA
T: 116600

Item Details:
Item No. | PRODUCT NAME | QTY | Unit Price(JPY) | Total Amount(JPY)
1 | SEMICONDUCTOR PACKAGING EQUIPMENT PARTS (STEEL) | 4 | 1000 | 4000.00

FOB
Total: 4000.00
Total number of packages: 1

Signed by: LIU CAIYUN
Tel: 13304280988
"""

print("="*70)
print("报关数据提取测试")
print("="*70)

# 测试 qwen2.5:1.5b
print("\n[测试 1] 使用 qwen2.5:1.5b")
print("-"*70)

extractor = CustomsDataExtractor(model="qwen2.5:1.5b")
result = extractor.extract_customs_data(sample_invoice)

if result['success']:
    print("[OK] 提取成功！")
    print("\n提取的数据：")
    print(json.dumps(result['data'], indent=2, ensure_ascii=False))

    # 保存结果
    with open('customs_data_1.5b.json', 'w', encoding='utf-8') as f:
        json.dump(result['data'], f, indent=2, ensure_ascii=False)
    print("\n[OK] 已保存到 customs_data_1.5b.json")
else:
    print(f"[X] 提取失败: {result['error']}")
    if result.get('raw_response'):
        print(f"\n原始响应:\n{result['raw_response']}")

# 可选：测试 qwen2.5:3b（如果已安装）
print("\n" + "="*70)
response = input("是否测试 qwen2.5:3b（更准确但更慢）？(y/n): ").strip().lower()

if response == 'y':
    print("\n[测试 2] 使用 qwen2.5:3b")
    print("-"*70)

    extractor_3b = CustomsDataExtractor(model="qwen2.5:3b")
    result_3b = extractor_3b.extract_customs_data(sample_invoice)

    if result_3b['success']:
        print("[OK] 提取成功！")
        print("\n提取的数据：")
        print(json.dumps(result_3b['data'], indent=2, ensure_ascii=False))

        # 保存结果
        with open('customs_data_3b.json', 'w', encoding='utf-8') as f:
            json.dump(result_3b['data'], f, indent=2, ensure_ascii=False)
        print("\n[OK] 已保存到 customs_data_3b.json")
    else:
        print(f"[X] 提取失败: {result_3b['error']}")

print("\n" + "="*70)
print("测试完成")
print("="*70)
