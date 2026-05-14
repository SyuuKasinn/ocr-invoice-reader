"""
图像优化工具 - 提升OCR处理速度
"""
import cv2
import numpy as np
from typing import Tuple


class ImageOptimizer:
    """图像预处理优化器

    通过智能缩放和优化，在保持精度的前提下提升处理速度
    """

    def __init__(self, max_size: int = 2000, min_size: int = 800):
        """
        Args:
            max_size: 最大边长（像素），超过会缩小
            min_size: 最小边长（像素），低于会放大
        """
        self.max_size = max_size
        self.min_size = min_size

    def optimize(self, img: np.ndarray, verbose: bool = False) -> np.ndarray:
        """
        优化图像以提升OCR速度

        Args:
            img: 输入图像
            verbose: 是否打印详细信息

        Returns:
            优化后的图像
        """
        original_shape = img.shape[:2]

        # 1. 智能缩放
        img = self.resize_if_needed(img, verbose)

        # 2. 去噪（可选，轻微）
        # img = self.denoise(img)

        if verbose and img.shape[:2] != original_shape:
            scale = img.shape[1] / original_shape[1]
            print(f"  Image optimized: {original_shape[1]}x{original_shape[0]} → "
                  f"{img.shape[1]}x{img.shape[0]} ({scale:.2f}x)")

        return img

    def resize_if_needed(self, img: np.ndarray, verbose: bool = False) -> np.ndarray:
        """
        如果图像过大或过小，调整到合适尺寸

        对于OCR，2000px足够了，更大只会增加计算量
        对于太小的图像，放大可以提高识别率
        """
        h, w = img.shape[:2]
        max_dim = max(h, w)
        min_dim = min(h, w)

        scale = 1.0

        # 图像过大 - 缩小
        if max_dim > self.max_size:
            scale = self.max_size / max_dim
            interpolation = cv2.INTER_AREA  # 缩小用AREA最好

        # 图像过小 - 放大（提高识别率）
        elif min_dim < self.min_size:
            scale = self.min_size / min_dim
            interpolation = cv2.INTER_CUBIC  # 放大用CUBIC

        else:
            return img  # 尺寸合适，不需要调整

        new_w = int(w * scale)
        new_h = int(h * scale)

        img = cv2.resize(img, (new_w, new_h), interpolation=interpolation)

        return img

    def denoise(self, img: np.ndarray, strength: int = 3) -> np.ndarray:
        """
        轻微去噪（可选）

        Args:
            img: 输入图像
            strength: 去噪强度（1-10，推荐3）
        """
        # 使用fastNlMeansDenoisingColored进行彩色图像去噪
        # h=strength 控制去噪强度，值越大去噪越强但可能模糊细节
        return cv2.fastNlMeansDenoisingColored(img, None, strength, strength, 7, 21)

    def enhance_contrast(self, img: np.ndarray, clip_limit: float = 2.0) -> np.ndarray:
        """
        增强对比度（可选，用于低质量扫描件）

        Args:
            img: 输入图像
            clip_limit: 对比度限制（1.0-4.0）
        """
        # 转换到LAB色彩空间
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)

        # CLAHE (对比度限制自适应直方图均衡)
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(8, 8))
        l = clahe.apply(l)

        # 合并回BGR
        lab = cv2.merge([l, a, b])
        img = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

        return img

    def sharpen(self, img: np.ndarray, strength: float = 1.0) -> np.ndarray:
        """
        锐化图像（可选，用于模糊图像）

        Args:
            img: 输入图像
            strength: 锐化强度（0.5-2.0）
        """
        # 创建锐化核
        kernel = np.array([
            [0, -1, 0],
            [-1, 5, -1],
            [0, -1, 0]
        ], dtype=np.float32)

        # 调整强度
        kernel = kernel * strength
        kernel[1, 1] = 1 + 4 * strength

        # 应用卷积
        sharpened = cv2.filter2D(img, -1, kernel)

        return sharpened


def optimize_for_ocr(img: np.ndarray,
                     max_size: int = 2000,
                     enhance_quality: bool = False,
                     verbose: bool = False) -> np.ndarray:
    """
    便捷函数：优化图像用于OCR

    Args:
        img: 输入图像
        max_size: 最大边长
        enhance_quality: 是否增强图像质量（对比度、锐化）
        verbose: 是否打印信息

    Returns:
        优化后的图像

    Example:
        >>> import cv2
        >>> img = cv2.imread('invoice.jpg')
        >>> img_optimized = optimize_for_ocr(img, max_size=2000)
        >>> # 然后用于OCR处理
    """
    optimizer = ImageOptimizer(max_size=max_size)
    img = optimizer.optimize(img, verbose=verbose)

    if enhance_quality:
        # 仅在图像质量较差时使用
        img = optimizer.enhance_contrast(img, clip_limit=2.0)

    return img
