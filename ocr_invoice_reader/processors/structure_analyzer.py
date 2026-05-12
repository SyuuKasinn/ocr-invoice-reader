"""
Document structure analyzer using PaddleOCR PP-Structure
"""
import os
import cv2
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path
import json

try:
    from paddleocr import PPStructure, PaddleOCR
    from paddleocr.ppstructure.recovery.recovery_to_doc import sorted_layout_boxes
    PPSTRUCTURE_AVAILABLE = True
except ImportError:
    PPSTRUCTURE_AVAILABLE = False


class LayoutRegion:
    """Layout region (text, table, figure, title)"""

    def __init__(self, region_type: str, bbox: List[int], content: Any = None, confidence: float = 0.0):
        self.type = region_type  # text/table/figure/title
        self.bbox = bbox  # [x1, y1, x2, y2]
        self.content = content
        self.confidence = confidence
        self.text = ""
        self.table_html = ""
        self.ocr_results = []

    def __repr__(self):
        return f"LayoutRegion(type={self.type}, bbox={self.bbox}, confidence={self.confidence:.2f})"

    def get_area(self) -> int:
        """Get region area"""
        return (self.bbox[2] - self.bbox[0]) * (self.bbox[3] - self.bbox[1])

    def get_center(self) -> Tuple[int, int]:
        """Get region center"""
        return (
            (self.bbox[0] + self.bbox[2]) // 2,
            (self.bbox[1] + self.bbox[3]) // 2
        )


class StructureAnalyzer:
    """Document structure analyzer using PP-Structure"""

    def __init__(self, use_gpu: bool = True, lang: str = 'japan'):
        """
        Initialize structure analyzer

        Args:
            use_gpu: Use GPU acceleration
            lang: Language for OCR (ch/en/japan/korean/latin/arabic)
        """
        if not PPSTRUCTURE_AVAILABLE:
            raise ImportError(
                "PP-Structure not available. Please ensure PaddleOCR >= 2.7 is installed.\n"
                "Run: pip install paddleocr>=2.7"
            )

        self.use_gpu = use_gpu
        self.lang = lang

        # Initialize PP-Structure
        print("Initializing PP-Structure...")
        try:
            device = 'gpu' if use_gpu else 'cpu'

            # PP-Structure layout models only support 'ch' and 'en'
            # Use 'ch' for Japanese/Korean/Chinese (works well for CJK)
            layout_lang = 'ch' if lang not in ['en'] else 'en'

            # PP-Structure for layout + table
            self.structure_engine = PPStructure(
                layout=True,           # Enable layout analysis
                table=True,           # Enable table recognition
                ocr=True,             # Enable OCR
                show_log=False,
                lang=layout_lang,     # Use ch for CJK, en for English
                device=device,
                use_angle_cls=False,   # Disable angle classification for speed
                layout_model_dir=None, # Use default model
                table_model_dir=None,  # Use default model
            )

            # Create separate OCR engine for the specified language
            if lang != layout_lang:
                print(f"  Creating separate OCR engine for language: {lang}")
                self.ocr_engine = PaddleOCR(
                    use_angle_cls=False,
                    lang=lang,
                    device=device,
                    show_log=False
                )
            else:
                self.ocr_engine = None

            print("PP-Structure initialized successfully")
            self.available = True

        except Exception as e:
            print(f"Warning: PP-Structure initialization failed - {e}")
            print("Falling back to basic OCR...")

            # Fallback to basic OCR
            device = 'gpu' if use_gpu else 'cpu'
            self.structure_engine = PaddleOCR(
                use_angle_cls=False,
                lang=lang,
                device=device,
                show_log=False
            )
            self.available = False

    def analyze(self, image_path: str, visualize: bool = False) -> Dict[str, Any]:
        """
        Analyze document structure

        Args:
            image_path: Path to image file
            visualize: Save visualization result

        Returns:
            {
                'regions': [LayoutRegion, ...],
                'raw_result': [...],
                'image_path': str
            }
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")

        print(f"\nAnalyzing document structure: {Path(image_path).name}")

        # Read image (use numpy for non-ASCII paths)
        try:
            img = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), cv2.IMREAD_COLOR)
        except:
            img = cv2.imread(image_path)

        if img is None:
            raise ValueError(f"Cannot read image: {image_path}")

        # Run structure analysis
        if self.available:
            result = self._analyze_with_ppstructure(img, image_path)
        else:
            result = self._analyze_with_ocr(img, image_path)

        # Visualize if requested
        if visualize:
            output_path = str(Path(image_path).parent / f"{Path(image_path).stem}_structure.jpg")
            self._visualize_structure(img, result['regions'], output_path)
            result['visualization'] = output_path

        return result

    def _analyze_with_ppstructure(self, img: np.ndarray, image_path: str) -> Dict[str, Any]:
        """Analyze with PP-Structure"""
        print("  Running PP-Structure analysis...")

        try:
            # Run PP-Structure
            raw_result = self.structure_engine(img)

            # Parse results
            regions = []

            for item in raw_result:
                region_type = item.get('type', 'text')
                bbox = item.get('bbox', [0, 0, 100, 100])

                # Convert bbox format
                if len(bbox) == 4:
                    bbox = [int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])]

                region = LayoutRegion(
                    region_type=region_type,
                    bbox=bbox,
                    content=item.get('res'),
                    confidence=item.get('confidence', 0.0)
                )

                # Process based on type
                if region_type == 'table':
                    # Table result
                    region.table_html = item.get('res', {}).get('html', '')
                    region.text = self._table_to_text(region.table_html)
                    print(f"    Found table: {len(region.table_html)} chars")

                elif region_type == 'text' or region_type == 'title':
                    # Text/Title result
                    res = item.get('res', [])
                    if isinstance(res, list):
                        region.ocr_results = res
                        region.text = "\n".join([line['text'] if isinstance(line, dict) else str(line[1][0]) for line in res])
                    else:
                        region.text = str(res)

                    print(f"    Found {region_type}: {len(region.text)} chars")

                elif region_type == 'figure':
                    # PP-Structure identified as figure
                    # First try to use PP-Structure's OCR results if available
                    res = item.get('res', [])

                    if isinstance(res, list) and res:
                        # PP-Structure already ran OCR on this figure
                        print(f"    Found figure with {len(res)} OCR lines")
                        texts = []
                        for line in res:
                            if isinstance(line, dict):
                                # New format: {'text': ..., 'confidence': ..., 'text_region': ...}
                                text = line.get('text', '')
                                if text:
                                    texts.append(text)
                                    region.ocr_results.append({
                                        'text': text,
                                        'confidence': line.get('confidence', 0.0),
                                        'box': line.get('text_region', [])
                                    })
                            elif isinstance(line, (list, tuple)) and len(line) >= 2:
                                # Old format: [box, (text, conf)]
                                box, (text, conf) = line
                                if text:
                                    texts.append(text)
                                    region.ocr_results.append({
                                        'text': text,
                                        'confidence': conf,
                                        'box': box
                                    })

                        if texts:
                            region.text = "\n".join(texts)
                            region.type = 'text'  # Reclassify as text
                            print(f"      Extracted {len(texts)} lines from figure (using PP-Structure OCR)")

                    # If no OCR results in figure, try running OCR manually
                    if not region.text:
                        print(f"    Figure has no OCR results - attempting manual OCR...")
                        x1, y1, x2, y2 = bbox
                        roi = img[y1:y2, x1:x2]

                        if self.ocr_engine:
                            try:
                                ocr_result = self.ocr_engine.ocr(roi, cls=False)
                                if ocr_result and ocr_result[0]:
                                    texts = []
                                    for line in ocr_result[0]:
                                        if line:
                                            box, (text, conf) = line
                                            texts.append(text)
                                            region.ocr_results.append({
                                                'text': text,
                                                'confidence': conf,
                                                'box': box
                                            })
                                    region.text = "\n".join(texts)
                                    region.type = 'text'
                                    print(f"      Extracted {len(texts)} lines (manual OCR)")
                            except Exception as e:
                                print(f"      Manual OCR failed: {e}")

                regions.append(region)

            print(f"  Total regions found: {len(regions)}")

            # If no useful regions found (all empty), fallback to OCR
            has_content = any(r.text.strip() for r in regions)
            if not has_content and regions:
                print("  Warning: No text extracted from regions, falling back to full OCR...")
                return self._analyze_with_ocr(img, image_path)

            return {
                'regions': regions,
                'raw_result': raw_result,
                'image_path': image_path,
                'method': 'ppstructure'
            }

        except Exception as e:
            print(f"  PP-Structure analysis failed: {e}")
            print("  Falling back to OCR...")
            return self._analyze_with_ocr(img, image_path)

    def _analyze_with_ocr(self, img: np.ndarray, image_path: str) -> Dict[str, Any]:
        """Fallback: analyze with basic OCR"""
        print("  Running basic OCR fallback...")

        # Use separate OCR engine if available (for correct language)
        if self.ocr_engine:
            print(f"    Using {self.lang} OCR engine")
            result = self.ocr_engine.ocr(img, cls=False)
        else:
            # PPStructure doesn't have ocr() method, create a PaddleOCR instance
            print("    Creating temporary OCR engine")
            from paddleocr import PaddleOCR
            device = 'gpu' if self.use_gpu else 'cpu'
            temp_ocr = PaddleOCR(
                use_angle_cls=False,
                lang=self.lang,
                device=device,
                show_log=False
            )
            result = temp_ocr.ocr(img, cls=False)

        if not result or not result[0]:
            return {
                'regions': [],
                'raw_result': [],
                'image_path': image_path,
                'method': 'ocr_fallback'
            }

        # Create single text region
        h, w = img.shape[:2]
        region = LayoutRegion(
            region_type='text',
            bbox=[0, 0, w, h],
            confidence=1.0
        )

        # Extract text
        texts = []
        ocr_results = []

        for line in result[0]:
            if line:
                box, (text, conf) = line
                texts.append(text)
                ocr_results.append({
                    'text': text,
                    'confidence': conf,
                    'box': box
                })

        region.text = "\n".join(texts)
        region.ocr_results = ocr_results

        print(f"  OCR extracted {len(texts)} lines")

        return {
            'regions': [region],
            'raw_result': result,
            'image_path': image_path,
            'method': 'ocr_fallback'
        }

    def _table_to_text(self, html: str) -> str:
        """Convert HTML table to text"""
        if not html:
            return ""

        # Simple HTML tag removal
        import re
        text = re.sub(r'<[^>]+>', ' ', html)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def _visualize_structure(self, img: np.ndarray, regions: List[LayoutRegion], output_path: str):
        """Visualize structure analysis result"""
        from PIL import Image, ImageDraw, ImageFont

        # Convert to PIL
        img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(img_pil)

        # Load font
        try:
            font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 20)
        except:
            font = ImageFont.load_default()

        # Color map
        colors = {
            'text': (0, 200, 83),      # Green
            'title': (33, 150, 243),   # Blue
            'table': (255, 152, 0),    # Orange
            'figure': (156, 39, 176)   # Purple
        }

        # Draw regions
        for region in regions:
            color = colors.get(region.type, (128, 128, 128))

            # Draw box
            draw.rectangle(
                [(region.bbox[0], region.bbox[1]), (region.bbox[2], region.bbox[3])],
                outline=color,
                width=3
            )

            # Draw label
            label = f"{region.type.upper()} ({region.confidence:.2f})"
            draw.text(
                (region.bbox[0], region.bbox[1] - 25),
                label,
                font=font,
                fill=color
            )

        # Convert back to OpenCV
        img_out = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

        # Save
        try:
            _, encoded = cv2.imencode('.jpg', img_out)
            encoded.tofile(output_path)
        except:
            cv2.imwrite(output_path, img_out)

        print(f"  Structure visualization saved: {output_path}")

    def get_text_regions(self, result: Dict[str, Any]) -> List[LayoutRegion]:
        """Get text regions only"""
        return [r for r in result['regions'] if r.type in ['text', 'title']]

    def get_table_regions(self, result: Dict[str, Any]) -> List[LayoutRegion]:
        """Get table regions only"""
        return [r for r in result['regions'] if r.type == 'table']

    def extract_all_text(self, result: Dict[str, Any]) -> str:
        """Extract all text from analysis result"""
        texts = []

        # Sort regions by position (top to bottom, left to right)
        regions = sorted(result['regions'], key=lambda r: (r.bbox[1], r.bbox[0]))

        for region in regions:
            if region.text:
                texts.append(region.text)

        return "\n\n".join(texts)

    def batch_analyze(self, image_paths: List[str], output_dir: str = None, visualize: bool = False) -> List[Dict[str, Any]]:
        """Batch analyze multiple images"""
        results = []

        for image_path in image_paths:
            try:
                result = self.analyze(image_path, visualize=visualize)
                results.append(result)

                # Save result
                if output_dir:
                    os.makedirs(output_dir, exist_ok=True)
                    output_file = Path(output_dir) / f"{Path(image_path).stem}_structure.json"

                    # Serialize result (regions are not JSON serializable)
                    serializable = {
                        'image_path': result['image_path'],
                        'method': result['method'],
                        'regions': [
                            {
                                'type': r.type,
                                'bbox': r.bbox,
                                'confidence': r.confidence,
                                'text': r.text[:500] if r.text else "",  # Truncate
                                'text_length': len(r.text) if r.text else 0
                            }
                            for r in result['regions']
                        ]
                    }

                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(serializable, f, indent=2, ensure_ascii=False)

            except Exception as e:
                print(f"Error analyzing {image_path}: {e}")
                results.append({
                    'image_path': image_path,
                    'error': str(e),
                    'regions': []
                })

        return results
