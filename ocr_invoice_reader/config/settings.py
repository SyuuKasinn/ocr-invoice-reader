"""
OCR配置文件
"""
import os

class Config:
    # PaddleOCR配置
    OCR_LANG = 'japan'  # 支持: ch, en, japan, korean, 或使用 'multi' 进行多语言
    USE_GPU = True  # 是否使用GPU加速（将转换为device参数）
    USE_ANGLE_CLS = True  # 是否进行文字方向分类（新版使用use_textline_orientation）

    # 识别参数
    DET_DB_THRESH = 0.3  # 文本检测阈值
    DET_DB_BOX_THRESH = 0.5  # 文本框检测阈值
    DET_DB_UNCLIP_RATIO = 1.5  # 文本框扩张比例
    REC_CONFIDENCE_THRESHOLD = 0.5  # 识别置信度阈值

    # 手写文字增强配置
    HANDWRITING_MODE = True  # 是否启用手写文字优化模式
    HANDWRITING_CONFIDENCE_THRESHOLD = 0.3  # 手写文字的置信度阈值（更宽松）
    ENABLE_IMAGE_ENHANCEMENT = True  # 是否启用图像增强
    ENABLE_MULTIPLE_PASSES = True  # 是否启用多次识别（提高准确率）

    # 输出配置
    DEFAULT_OUTPUT_DIR = 'results'
    DEFAULT_OUTPUT_FORMAT = 'json'  # json, txt, excel

    # 支持的图片格式
    SUPPORTED_IMAGE_FORMATS = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']

    # 可视化配置
    VIS_FONT_PATH = None  # 字体路径，None则使用默认
    VIS_TEXT_SCORE = True  # 是否显示识别分数
    VIS_TEXT_SIZE = 20
    VIS_THICKNESS = 2

    @staticmethod
    def ensure_dirs():
        """确保必要的目录存在"""
        os.makedirs(Config.DEFAULT_OUTPUT_DIR, exist_ok=True)
