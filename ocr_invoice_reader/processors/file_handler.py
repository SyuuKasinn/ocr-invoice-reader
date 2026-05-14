"""
文件处理模块：支持PDF、压缩包等多种文件类型
"""
import os
import shutil
import tempfile
import zipfile
import tarfile
from typing import List, Dict, Optional
from pathlib import Path

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

try:
    from pdf2image import convert_from_path
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False

try:
    import py7zr
    PY7ZR_AVAILABLE = True
except ImportError:
    PY7ZR_AVAILABLE = False

try:
    import rarfile
    RARFILE_AVAILABLE = True
except ImportError:
    RARFILE_AVAILABLE = False

from PIL import Image


class FileTypeHandler:
    """文件类型处理器"""

    # 支持的图片格式
    IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.gif', '.webp'}

    # 支持的PDF格式
    PDF_EXTENSIONS = {'.pdf'}

    # 支持的压缩包格式
    ARCHIVE_EXTENSIONS = {'.zip', '.rar', '.7z', '.tar', '.tar.gz', '.tgz'}

    @staticmethod
    def get_file_type(file_path: str) -> str:
        """
        判断文件类型

        Returns:
            'image', 'pdf', 'archive', 'unknown'
        """
        ext = Path(file_path).suffix.lower()

        if ext in FileTypeHandler.IMAGE_EXTENSIONS:
            return 'image'
        elif ext in FileTypeHandler.PDF_EXTENSIONS:
            return 'pdf'
        elif ext in FileTypeHandler.ARCHIVE_EXTENSIONS:
            return 'archive'
        else:
            return 'unknown'

    @staticmethod
    def is_supported(file_path: str) -> bool:
        """检查文件是否支持"""
        return FileTypeHandler.get_file_type(file_path) != 'unknown'


class PDFHandler:
    """PDF文件处理器"""

    def __init__(self, use_pymupdf: bool = True):
        """
        初始化PDF处理器

        Args:
            use_pymupdf: 优先使用PyMuPDF（更快），否则使用pdf2image
        """
        self.use_pymupdf = use_pymupdf and PYMUPDF_AVAILABLE

        if not self.use_pymupdf and not PDF2IMAGE_AVAILABLE:
            raise ImportError(
                "PDF处理需要安装 PyMuPDF 或 pdf2image\n"
                "运行: pip install PyMuPDF 或 pip install pdf2image"
            )

    def extract_pdf_text(self, pdf_path: str) -> Dict[int, List[Dict]]:
        """
        提取PDF中的内嵌文字（带位置信息）

        Args:
            pdf_path: PDF文件路径

        Returns:
            {页码: [{text: 文字, bbox: 边界框}]}
        """
        if not PYMUPDF_AVAILABLE:
            return {}

        pdf_text_data = {}

        try:
            pdf_document = fitz.open(pdf_path)

            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]

                # 提取文字块（包含位置信息）
                blocks = page.get_text("dict")["blocks"]

                page_texts = []
                for block in blocks:
                    if block.get("type") == 0:  # 文本块
                        for line in block.get("lines", []):
                            for span in line.get("spans", []):
                                text = span.get("text", "").strip()
                                bbox = span.get("bbox")  # (x0, y0, x1, y1)

                                if text and bbox:
                                    page_texts.append({
                                        "text": text,
                                        "bbox": bbox,  # PDF坐标
                                        "font_size": span.get("size", 0),
                                        "font": span.get("font", "")
                                    })

                pdf_text_data[page_num] = page_texts

            pdf_document.close()
            print(f"  Extracted PDF text: {sum(len(v) for v in pdf_text_data.values())} blocks")

        except Exception as e:
            print(f"  Warning: PDF text extraction failed - {e}")

        return pdf_text_data

    def pdf_to_images(self, pdf_path: str, output_dir: str = None,
                      dpi: int = 300) -> List[str]:
        """
        将PDF转换为图片

        Args:
            pdf_path: PDF文件路径
            output_dir: 输出目录（默认为临时目录）
            dpi: 图片分辨率（默认300 DPI）

        Returns:
            生成的图片路径列表
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF文件不存在: {pdf_path}")

        if output_dir is None:
            output_dir = tempfile.mkdtemp(prefix='pdf_')
        else:
            os.makedirs(output_dir, exist_ok=True)

        base_name = Path(pdf_path).stem
        image_paths = []

        if self.use_pymupdf:
            print(f"  Using PyMuPDF to convert PDF (DPI: {dpi})...")
            image_paths = self._convert_with_pymupdf(pdf_path, output_dir, base_name, dpi)
        else:
            print(f"  Using pdf2image to convert PDF (DPI: {dpi})...")
            image_paths = self._convert_with_pdf2image(pdf_path, output_dir, base_name, dpi)

        print(f"  PDF conversion complete: {len(image_paths)} pages")
        return image_paths

    def _convert_with_pymupdf(self, pdf_path: str, output_dir: str,
                              base_name: str, dpi: int) -> List[str]:
        """使用PyMuPDF转换（更快）"""
        image_paths = []
        pdf_document = fitz.open(pdf_path)

        # 计算缩放因子（DPI to zoom）
        zoom = dpi / 72.0
        mat = fitz.Matrix(zoom, zoom)

        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            pix = page.get_pixmap(matrix=mat)

            output_path = os.path.join(output_dir, f"{base_name}_page_{page_num + 1:04d}.png")

            # PyMuPDF 1.19+ 使用 pix.save()
            pix.save(output_path)
            image_paths.append(output_path)

        pdf_document.close()
        return image_paths

    def _convert_with_pdf2image(self, pdf_path: str, output_dir: str,
                                base_name: str, dpi: int) -> List[str]:
        """使用pdf2image转换"""
        images = convert_from_path(pdf_path, dpi=dpi)
        image_paths = []

        for idx, image in enumerate(images, 1):
            output_path = os.path.join(output_dir, f"{base_name}_page_{idx:04d}.png")
            image.save(output_path, 'PNG')
            image_paths.append(output_path)

        return image_paths

    def get_pdf_info(self, pdf_path: str) -> Dict:
        """获取PDF信息"""
        info = {
            'pages': 0,
            'title': '',
            'author': '',
            'subject': ''
        }

        if PYMUPDF_AVAILABLE:
            doc = fitz.open(pdf_path)
            info['pages'] = len(doc)
            metadata = doc.metadata
            info['title'] = metadata.get('title', '')
            info['author'] = metadata.get('author', '')
            info['subject'] = metadata.get('subject', '')
            doc.close()

        return info


class ArchiveHandler:
    """压缩包处理器"""

    def __init__(self):
        """初始化压缩包处理器"""
        pass

    def extract_archive(self, archive_path: str, output_dir: str = None) -> str:
        """
        解压缩文件

        Args:
            archive_path: 压缩包路径
            output_dir: 解压目录（默认为临时目录）

        Returns:
            解压后的目录路径
        """
        if not os.path.exists(archive_path):
            raise FileNotFoundError(f"压缩包不存在: {archive_path}")

        if output_dir is None:
            output_dir = tempfile.mkdtemp(prefix='extract_')
        else:
            os.makedirs(output_dir, exist_ok=True)

        ext = Path(archive_path).suffix.lower()
        archive_name = Path(archive_path).stem

        print(f"  正在解压: {Path(archive_path).name}")

        if ext == '.zip':
            self._extract_zip(archive_path, output_dir)
        elif ext == '.rar':
            self._extract_rar(archive_path, output_dir)
        elif ext == '.7z':
            self._extract_7z(archive_path, output_dir)
        elif ext in ['.tar', '.tar.gz', '.tgz']:
            self._extract_tar(archive_path, output_dir)
        else:
            raise ValueError(f"不支持的压缩格式: {ext}")

        print(f"  解压完成: {output_dir}")
        return output_dir

    def _extract_zip(self, archive_path: str, output_dir: str):
        """解压ZIP"""
        with zipfile.ZipFile(archive_path, 'r') as zip_ref:
            zip_ref.extractall(output_dir)

    def _extract_rar(self, archive_path: str, output_dir: str):
        """解压RAR"""
        if not RARFILE_AVAILABLE:
            raise ImportError("RAR解压需要安装 rarfile\n运行: pip install rarfile")

        with rarfile.RarFile(archive_path, 'r') as rar_ref:
            rar_ref.extractall(output_dir)

    def _extract_7z(self, archive_path: str, output_dir: str):
        """解压7Z"""
        if not PY7ZR_AVAILABLE:
            raise ImportError("7Z解压需要安装 py7zr\n运行: pip install py7zr")

        with py7zr.SevenZipFile(archive_path, 'r') as z:
            z.extractall(output_dir)

    def _extract_tar(self, archive_path: str, output_dir: str):
        """解压TAR"""
        with tarfile.open(archive_path, 'r:*') as tar:
            tar.extractall(output_dir)


class FileProcessor:
    """统一文件处理器"""

    def __init__(self, dpi: int = 300):
        """
        初始化文件处理器

        Args:
            dpi: PDF转图片的分辨率（默认300，保证精度）
        """
        self.dpi = dpi
        self.pdf_handler = PDFHandler() if (PYMUPDF_AVAILABLE or PDF2IMAGE_AVAILABLE) else None
        self.archive_handler = ArchiveHandler()
        self.temp_dirs = []  # 记录临时目录用于清理
        self.pdf_text_cache = {}  # 缓存PDF文本数据 {pdf_path: text_data}

    def process_file(self, file_path: str) -> List[str]:
        """
        处理文件，返回可以OCR识别的图片路径列表

        Args:
            file_path: 文件路径

        Returns:
            图片路径列表
        """
        file_type = FileTypeHandler.get_file_type(file_path)

        if file_type == 'image':
            return [file_path]

        elif file_type == 'pdf':
            return self._process_pdf(file_path)

        elif file_type == 'archive':
            return self._process_archive(file_path)

        else:
            print(f"  警告: 不支持的文件类型: {file_path}")
            return []

    def _process_pdf(self, pdf_path: str) -> List[str]:
        """处理PDF文件"""
        if self.pdf_handler is None:
            print("  [!] 错误: PDF处理未启用")
            print("      请运行: pip install PyMuPDF")
            print("      然后重新运行程序")
            return []

        print(f"\nProcessing PDF: {Path(pdf_path).name}")

        # Get PDF info
        info = self.pdf_handler.get_pdf_info(pdf_path)
        print(f"  Pages: {info['pages']}")

        # 提取PDF内嵌文字
        pdf_text_data = self.pdf_handler.extract_pdf_text(pdf_path)
        if pdf_text_data:
            self.pdf_text_cache[pdf_path] = pdf_text_data

        # 转换为图片
        temp_dir = tempfile.mkdtemp(prefix='pdf_images_')
        self.temp_dirs.append(temp_dir)

        image_paths = self.pdf_handler.pdf_to_images(pdf_path, temp_dir, self.dpi)
        return image_paths

    def get_pdf_text_for_page(self, image_path: str, page_num: int = None) -> List[Dict]:
        """
        获取PDF页面的内嵌文字

        Args:
            image_path: 从PDF转换的图片路径
            page_num: 页码（从0开始），如果为None则从文件名推断

        Returns:
            [{text: 文字, bbox: 边界框}]
        """
        # 从图片路径推断原PDF
        for pdf_path, text_data in self.pdf_text_cache.items():
            pdf_stem = Path(pdf_path).stem
            if pdf_stem in image_path:
                # 从文件名提取页码
                if page_num is None:
                    import re
                    match = re.search(r'_page_(\d+)', image_path)
                    if match:
                        page_num = int(match.group(1)) - 1  # 转为0-based

                if page_num is not None and page_num in text_data:
                    return text_data[page_num]

        return []

    def _process_archive(self, archive_path: str) -> List[str]:
        """处理压缩包"""
        print(f"\n处理压缩包: {Path(archive_path).name}")

        # 解压缩
        temp_dir = tempfile.mkdtemp(prefix='archive_')
        self.temp_dirs.append(temp_dir)

        extract_dir = self.archive_handler.extract_archive(archive_path, temp_dir)

        # 递归查找所有可处理的文件
        all_images = []
        for root, dirs, files in os.walk(extract_dir):
            for file in sorted(files):
                file_path = os.path.join(root, file)
                file_type = FileTypeHandler.get_file_type(file_path)

                if file_type == 'image':
                    all_images.append(file_path)
                elif file_type == 'pdf':
                    # 递归处理PDF
                    pdf_images = self._process_pdf(file_path)
                    all_images.extend(pdf_images)

        print(f"  在压缩包中找到 {len(all_images)} 个可处理文件")
        return all_images

    def process_multiple_files(self, file_paths: List[str]) -> List[str]:
        """
        批量处理多个文件

        Args:
            file_paths: 文件路径列表

        Returns:
            所有可识别的图片路径
        """
        all_images = []

        for file_path in file_paths:
            if not os.path.exists(file_path):
                print(f"警告: 文件不存在: {file_path}")
                continue

            images = self.process_file(file_path)
            all_images.extend(images)

        return all_images

    def cleanup(self):
        """清理临时目录"""
        for temp_dir in self.temp_dirs:
            try:
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
            except Exception as e:
                print(f"清理临时目录失败: {temp_dir} - {e}")

        self.temp_dirs = []

    def __del__(self):
        """析构时自动清理"""
        self.cleanup()


def get_supported_formats() -> Dict[str, List[str]]:
    """获取支持的文件格式"""
    formats = {
        '图片格式': list(FileTypeHandler.IMAGE_EXTENSIONS),
        'PDF格式': list(FileTypeHandler.PDF_EXTENSIONS),
        '压缩包格式': list(FileTypeHandler.ARCHIVE_EXTENSIONS)
    }
    return formats


def check_dependencies() -> Dict[str, bool]:
    """检查依赖库是否安装"""
    deps = {
        'PyMuPDF (PDF处理)': PYMUPDF_AVAILABLE,
        'pdf2image (PDF处理备选)': PDF2IMAGE_AVAILABLE,
        'py7zr (7Z解压)': PY7ZR_AVAILABLE,
        'rarfile (RAR解压)': RARFILE_AVAILABLE,
        'PDF处理可用': PYMUPDF_AVAILABLE or PDF2IMAGE_AVAILABLE
    }
    return deps
