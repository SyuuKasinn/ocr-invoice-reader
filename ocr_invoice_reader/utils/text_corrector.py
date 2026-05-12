# -*- coding: utf-8 -*-
"""
文本纠错模块 - 修正OCR识别错误
支持中文、英文的常见OCR错误修正
"""
import re
import sys

# 设置UTF-8编码
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

# 尝试导入纠错库
try:
    from autocorrect import Speller
    AUTOCORRECT_AVAILABLE = True
except ImportError:
    AUTOCORRECT_AVAILABLE = False
    print("提示: autocorrect未安装，英文纠错功能不可用")
    print("      安装: pip install autocorrect")

try:
    import pycorrector
    PYCORRECTOR_AVAILABLE = True
except ImportError:
    PYCORRECTOR_AVAILABLE = False
    print("提示: pycorrector未安装，中文纠错功能不可用")
    print("      安装: pip install pycorrector")


class TextCorrector:
    """文本纠错器"""

    def __init__(self, enable_english=True, enable_chinese=True, enable_rules=True):
        """
        初始化纠错器

        Args:
            enable_english: 是否启用英文纠错
            enable_chinese: 是否启用中文纠错
            enable_rules: 是否启用规则纠错
        """
        self.enable_english = enable_english and AUTOCORRECT_AVAILABLE
        self.enable_chinese = enable_chinese and PYCORRECTOR_AVAILABLE
        self.enable_rules = enable_rules

        # 初始化英文拼写检查器
        if self.enable_english:
            try:
                self.english_speller = Speller(lang='en')
            except:
                self.enable_english = False
                print("警告: 英文纠错初始化失败")

        # OCR常见字符混淆规则（优先级从高到低）
        self.ocr_confusion_rules = [
            # 数字与字母混淆
            (r'\b([A-Z]+)0([A-Z]+)\b', r'\1O\2'),  # 单词中的0->O
            (r'\b0([A-Z]{2,})', r'O\1'),  # 单词开头的0->O
            (r'\b1([A-Z]{2,})', r'I\1'),  # 单词开头的1->I
            (r'\bl([A-Z]{2,})', r'I\1'),  # 单词开头的l->I (修正了\2错误)

            # 常见OCR错误
            (r'\bO(\d+)', r'0\1'),  # O后接数字 -> 0
            (r'(\d+)O(\d+)', r'\g<1>0\g<2>'),  # 数字中的O->0
            (r'(\d+)l(\d+)', r'\g<1>1\g<2>'),  # 数字中的l->1
            (r'(\d+)I(\d+)', r'\g<1>1\g<2>'),  # 数字中的I->1

            # 标点符号
            (r'（', '('),  # 全角括号
            (r'）', ')'),
            (r'，', ','),  # 全角逗号
            (r'：', ':'),  # 全角冒号
            (r'；', ';'),  # 全角分号

            # 空格清理
            (r'\s+([,;:.])', r'\1'),  # 标点前的空格
            (r'([,;:])\s*([a-zA-Z])', r'\1 \2'),  # 标点后添加空格
        ]

        # 常见词汇映射（OCR经常识别错误的词）
        self.common_word_fixes = {
            # 英文常见错误
            'lnvoice': 'Invoice',
            'Dafe': 'Date',
            'Amounf': 'Amount',
            'Tofa1': 'Total',
            'Narne': 'Name',
            'Addre5s': 'Address',
            'Cornpany': 'Company',
            'Cusforner': 'Customer',
            'Te1': 'Tel',
            'Fax': 'Fax',
            'Ernail': 'Email',
            'Delively': 'Delivery',
            'Cornact': 'Contact',

            # 数字相关
            '0O': '00',
            'O0': '00',
            'l1': '11',
            '1l': '11',
        }

    def correct_text(self, text: str, preserve_case=True) -> str:
        """
        纠正文本

        Args:
            text: 待纠正的文本
            preserve_case: 是否保持大小写

        Returns:
            纠正后的文本
        """
        if not text or not text.strip():
            return text

        original_text = text
        corrected_text = text

        # 1. 规则纠错
        if self.enable_rules:
            corrected_text = self._apply_rules(corrected_text)
            corrected_text = self._apply_common_fixes(corrected_text)

        # 2. 判断文本类型
        has_chinese = self._has_chinese(corrected_text)
        has_english = self._has_english(corrected_text)

        # 3. 中文纠错
        if has_chinese and self.enable_chinese:
            corrected_text = self._correct_chinese(corrected_text)

        # 4. 英文纠错
        if has_english and self.enable_english:
            corrected_text = self._correct_english(corrected_text, preserve_case)

        return corrected_text

    def _apply_rules(self, text: str) -> str:
        """应用规则纠错"""
        for pattern, replacement in self.ocr_confusion_rules:
            text = re.sub(pattern, replacement, text)
        return text

    def _apply_common_fixes(self, text: str) -> str:
        """应用常见词汇修正"""
        for wrong, correct in self.common_word_fixes.items():
            # 大小写不敏感替换
            text = re.sub(r'\b' + re.escape(wrong) + r'\b', correct, text, flags=re.IGNORECASE)
        return text

    def _correct_chinese(self, text: str) -> str:
        """中文纠错"""
        if not self.enable_chinese:
            return text

        try:
            # pycorrector会返回(corrected_text, detail)
            corrected, detail = pycorrector.correct(text)
            return corrected
        except Exception as e:
            print(f"中文纠错失败: {e}")
            return text

    def _correct_english(self, text: str, preserve_case=True) -> str:
        """英文纠错"""
        if not self.enable_english:
            return text

        try:
            # 分词处理
            words = text.split()
            corrected_words = []

            for word in words:
                # 保留标点符号
                match = re.match(r'^([^\w]*)(\w+)([^\w]*)$', word)
                if match:
                    prefix, core, suffix = match.groups()

                    # 跳过纯数字和特殊格式
                    if core.isdigit() or self._is_special_format(core):
                        corrected_words.append(word)
                        continue

                    # 只纠正全英文单词
                    if core.isalpha() and core.isascii():
                        original_case = self._get_case_pattern(core)
                        corrected = self.english_speller(core)

                        # 保持原始大小写格式
                        if preserve_case:
                            corrected = self._apply_case_pattern(corrected, original_case)

                        corrected_words.append(prefix + corrected + suffix)
                    else:
                        corrected_words.append(word)
                else:
                    corrected_words.append(word)

            return ' '.join(corrected_words)
        except Exception as e:
            print(f"英文纠错失败: {e}")
            return text

    def _has_chinese(self, text: str) -> bool:
        """检查是否包含中文字符"""
        return bool(re.search(r'[一-鿿]', text))

    def _has_english(self, text: str) -> bool:
        """检查是否包含英文字符"""
        return bool(re.search(r'[a-zA-Z]', text))

    def _is_special_format(self, word: str) -> bool:
        """检查是否为特殊格式（如编号、代码等）"""
        # 包含数字和字母混合，或特殊字符
        has_digit = bool(re.search(r'\d', word))
        has_alpha = bool(re.search(r'[a-zA-Z]', word))
        has_special = bool(re.search(r'[_\-#@]', word))

        # 电话号码、邮编、编号等
        if (has_digit and has_alpha) or has_special:
            return True

        # 全大写且较短（可能是缩写）
        if word.isupper() and len(word) <= 5:
            return True

        return False

    def _get_case_pattern(self, word: str) -> str:
        """获取单词的大小写模式"""
        if word.isupper():
            return 'upper'
        elif word.islower():
            return 'lower'
        elif word[0].isupper() and word[1:].islower():
            return 'title'
        else:
            return 'mixed'

    def _apply_case_pattern(self, word: str, pattern: str) -> str:
        """应用大小写模式"""
        if pattern == 'upper':
            return word.upper()
        elif pattern == 'lower':
            return word.lower()
        elif pattern == 'title':
            return word.capitalize()
        else:
            return word


# 创建全局纠错器实例（延迟初始化）
_global_corrector = None

def get_corrector(enable_english=True, enable_chinese=True, enable_rules=True):
    """获取全局纠错器实例"""
    global _global_corrector
    if _global_corrector is None:
        _global_corrector = TextCorrector(
            enable_english=enable_english,
            enable_chinese=enable_chinese,
            enable_rules=enable_rules
        )
    return _global_corrector


def correct_text(text: str, enable_english=True, enable_chinese=True, enable_rules=True) -> str:
    """
    快捷函数：纠正文本

    Args:
        text: 待纠正的文本
        enable_english: 是否启用英文纠错
        enable_chinese: 是否启用中文纠错
        enable_rules: 是否启用规则纠错

    Returns:
        纠正后的文本
    """
    corrector = get_corrector(enable_english, enable_chinese, enable_rules)
    return corrector.correct_text(text)


if __name__ == '__main__':
    # 测试代码
    test_cases = [
        "lnvoice #12345",  # lnvoice -> Invoice
        "Dafe: 2024-01-15",  # Dafe -> Date
        "Amounf: $1234.56",  # Amounf -> Amount
        "Tel: 123-456-789O",  # 最后的O->0
        "HTL 5O6539397733",  # 数字中的O->0
        "Company Narne: ABC Corp",  # Narne -> Name
        "这是一个测试文本",  # 中文
        "Mixed text 测试 123",  # 混合
    ]

    corrector = TextCorrector()
    print("文本纠错测试:\n" + "=" * 50)
    for text in test_cases:
        corrected = corrector.correct_text(text)
        if text != corrected:
            print(f"原文: {text}")
            print(f"纠正: {corrected}")
            print("-" * 50)
