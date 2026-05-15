"""
报关数据提取器 - 从发票中提取报关系统所需的结构化数据
"""
import json
from typing import Dict, Any, Optional
from ocr_invoice_reader.utils.llm_processor import LLMProcessor


class CustomsDataExtractor:
    """报关数据提取器"""

    def __init__(self, model: str = "qwen2.5:3b"):
        self.llm = LLMProcessor(model=model)

    def extract_customs_data(self, invoice_text: str) -> Dict[str, Any]:
        """
        从发票文本中提取报关所需的结构化数据

        Args:
            invoice_text: OCR识别的发票文本

        Returns:
            报关数据字典
        """
        system_prompt = """你是一个专业的报关数据提取专家。
你的任务是从发票/运单文本中提取关键信息，并转换为标准的JSON格式。

请严格按照以下JSON结构返回数据：
{
  "tracking_number": "运单号/追踪号",
  "invoice_number": "发票号",
  "invoice_date": "发票日期（YYYY-MM-DD格式）",
  "logistics_provider": "物流公司名称",
  "shipper": {
    "company_name": "发货人公司名称",
    "account_number": "账号/客户号",
    "address": "发货人地址",
    "city": "城市",
    "country": "国家"
  },
  "receiver": {
    "company_name": "收货人公司名称",
    "contact_person": "联系人姓名",
    "phone": "电话号码",
    "address": "收货人地址",
    "zip_code": "邮编",
    "city": "城市",
    "country": "国家"
  },
  "shipment_info": {
    "category": "货物类别（Parcel/Document等）",
    "total_packages": "总包裹数（数字）",
    "total_weight": "总重量（数字）",
    "weight_unit": "重量单位（kg/lb等）",
    "dimensions": {
      "length": "长度（数字）",
      "width": "宽度（数字）",
      "height": "高度（数字）",
      "unit": "单位（cm/inch等）"
    }
  },
  "items": [
    {
      "description": "货物描述",
      "quantity": "数量",
      "unit_price": "单价",
      "total_amount": "总金额",
      "currency": "币种"
    }
  ],
  "payment": {
    "terms": "付款条款（FOB/CIF等）",
    "currency": "币种",
    "total_amount": "总金额"
  }
}

注意事项：
1. 如果某个字段在文本中找不到，使用 null 而不是空字符串
2. 数字字段必须是数字类型，不要包含单位
3. 日期格式统一为 YYYY-MM-DD
4. 地址要完整，包含所有可用信息
5. 电话号码保留原格式（包括国家代码）
6. 只返回JSON，不要添加任何解释
"""

        user_prompt = f"""请从以下发票/运单文本中提取报关所需的数据：

{invoice_text}

返回标准JSON格式的数据："""

        try:
            # 使用较长的超时时间（8页文档需要更长时间）
            response = self.llm._generate(user_prompt, system_prompt, temperature=0.1, timeout=180)

            # 解析 JSON
            result = self._parse_json_response(response)

            # 验证和清理数据
            result = self._validate_and_clean(result)

            return {
                "success": True,
                "data": result,
                "raw_response": response
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "raw_response": response if 'response' in locals() else None
            }

    def _parse_json_response(self, response: str) -> Dict:
        """解析 LLM 返回的 JSON"""
        # 尝试提取 JSON 部分
        if '```json' in response:
            json_str = response.split('```json')[1].split('```')[0].strip()
        elif '```' in response:
            json_str = response.split('```')[1].split('```')[0].strip()
        else:
            json_str = response.strip()

        # 移除可能的注释
        lines = json_str.split('\n')
        cleaned_lines = [line for line in lines if not line.strip().startswith('//')]
        json_str = '\n'.join(cleaned_lines)

        return json.loads(json_str)

    def _validate_and_clean(self, data: Dict) -> Dict:
        """验证和清理数据"""
        # 确保数字字段是数字类型
        if 'shipment_info' in data and data['shipment_info']:
            shipment = data['shipment_info']

            # 转换总包裹数
            if 'total_packages' in shipment:
                try:
                    shipment['total_packages'] = int(shipment['total_packages']) if shipment['total_packages'] else None
                except (ValueError, TypeError):
                    shipment['total_packages'] = None

            # 转换重量
            if 'total_weight' in shipment:
                try:
                    shipment['total_weight'] = float(shipment['total_weight']) if shipment['total_weight'] else None
                except (ValueError, TypeError):
                    shipment['total_weight'] = None

            # 转换尺寸
            if 'dimensions' in shipment and shipment['dimensions']:
                dims = shipment['dimensions']
                for key in ['length', 'width', 'height']:
                    if key in dims:
                        try:
                            dims[key] = float(dims[key]) if dims[key] else None
                        except (ValueError, TypeError):
                            dims[key] = None

        # 转换商品数量和金额
        if 'items' in data and isinstance(data['items'], list):
            for item in data['items']:
                if 'quantity' in item:
                    try:
                        item['quantity'] = int(item['quantity']) if item['quantity'] else None
                    except (ValueError, TypeError):
                        item['quantity'] = None

                for field in ['unit_price', 'total_amount']:
                    if field in item:
                        try:
                            item[field] = float(item[field]) if item[field] else None
                        except (ValueError, TypeError):
                            item[field] = None

        # 转换总金额
        if 'payment' in data and data['payment'] and 'total_amount' in data['payment']:
            try:
                data['payment']['total_amount'] = float(data['payment']['total_amount']) if data['payment']['total_amount'] else None
            except (ValueError, TypeError):
                data['payment']['total_amount'] = None

        return data

    def extract_from_file(self, txt_file: str) -> Dict[str, Any]:
        """
        从文本文件提取报关数据

        Args:
            txt_file: OCR生成的文本文件路径

        Returns:
            报关数据字典
        """
        with open(txt_file, 'r', encoding='utf-8') as f:
            text = f.read()

        return self.extract_customs_data(text)

    def batch_extract(self, txt_files: list) -> list:
        """
        批量提取多个文件的报关数据

        Args:
            txt_files: 文本文件路径列表

        Returns:
            报关数据列表
        """
        results = []
        for i, txt_file in enumerate(txt_files, 1):
            print(f"Processing {i}/{len(txt_files)}: {txt_file}")
            result = self.extract_from_file(txt_file)
            results.append({
                "file": txt_file,
                "result": result
            })

        return results


def extract_customs_data(invoice_text: str, model: str = "qwen2.5:3b") -> Dict[str, Any]:
    """
    便捷函数：提取报关数据

    Args:
        invoice_text: 发票文本
        model: LLM 模型名称

    Returns:
        报关数据字典
    """
    extractor = CustomsDataExtractor(model=model)
    return extractor.extract_customs_data(invoice_text)
