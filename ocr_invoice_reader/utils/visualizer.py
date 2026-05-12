"""
Visualization utilities for OCR results
Similar to PaddleOCR official visualization
"""
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from typing import List, Dict, Tuple, Optional
from pathlib import Path


class OCRVisualizer:
    """OCR result visualizer"""

    def __init__(self):
        # Load font
        self.font = self._load_font()

        # Colors
        self.region_colors = {
            'text': (0, 200, 83),      # Green
            'title': (33, 150, 243),   # Blue
            'table': (255, 152, 0),    # Orange
            'figure': (156, 39, 176)   # Purple
        }

        self.text_color = (255, 0, 0)  # Red for OCR text boxes

    def _load_font(self, size: int = 18):
        """Load font for drawing text"""
        try:
            # Try common font paths
            font_paths = [
                "C:/Windows/Fonts/msyh.ttc",      # Microsoft YaHei
                "C:/Windows/Fonts/simhei.ttf",    # SimHei
                "C:/Windows/Fonts/simsun.ttc",    # SimSun
                "/System/Library/Fonts/PingFang.ttc",  # macOS
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
            ]

            for font_path in font_paths:
                if Path(font_path).exists():
                    return ImageFont.truetype(font_path, size)

            # Fallback
            return ImageFont.load_default()
        except:
            return ImageFont.load_default()

    def visualize_regions(
        self,
        image: np.ndarray,
        regions: List[Dict],
        show_text: bool = True,
        show_boxes: bool = True
    ) -> np.ndarray:
        """
        Visualize detected regions with OCR text boxes

        Args:
            image: Input image (BGR)
            regions: List of regions with structure:
                {
                    'type': str,
                    'bbox': [x1, y1, x2, y2],
                    'confidence': float,
                    'text': str,
                    'ocr_boxes': List[Dict] (optional)
                }
            show_text: Draw OCR text boxes
            show_boxes: Draw region boxes

        Returns:
            Annotated image (BGR)
        """
        # Convert to PIL
        img_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(img_pil, 'RGBA')

        # Draw OCR text boxes first (background layer)
        if show_text:
            for region in regions:
                if 'ocr_boxes' in region and region['ocr_boxes']:
                    self._draw_ocr_boxes(draw, region['ocr_boxes'])

        # Draw region boxes (foreground layer)
        if show_boxes:
            for region in regions:
                self._draw_region_box(draw, region)

        # Convert back to OpenCV
        return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

    def _draw_ocr_boxes(self, draw: ImageDraw, ocr_boxes: List[Dict]):
        """Draw OCR text boxes (similar to PaddleOCR style)"""
        for box_info in ocr_boxes:
            # Get box coordinates
            if 'box' in box_info:
                box = box_info['box']
            elif 'text_region' in box_info:
                box = box_info['text_region']
            elif 'bbox' in box_info:
                bbox = box_info['bbox']
                box = [[bbox[0], bbox[1]], [bbox[2], bbox[1]],
                       [bbox[2], bbox[3]], [bbox[0], bbox[3]]]
            else:
                continue

            # Convert to point list
            if isinstance(box, list) and len(box) == 4:
                if isinstance(box[0], list):
                    # Already in [[x,y], [x,y], ...] format
                    points = [(int(p[0]), int(p[1])) for p in box]
                elif len(box) == 4 and all(isinstance(x, (int, float)) for x in box):
                    # [x1, y1, x2, y2] format
                    x1, y1, x2, y2 = box
                    points = [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]
                else:
                    continue
            else:
                continue

            # Draw polygon outline
            draw.polygon(points, outline=self.text_color, width=2)

            # Draw text
            text = box_info.get('text', '')
            if text and len(points) >= 2:
                # Position text at top-left of box
                text_pos = (points[0][0], max(0, points[0][1] - 20))

                # Draw background for text
                text_bbox = draw.textbbox(text_pos, text, font=self.font)
                draw.rectangle(text_bbox, fill=(255, 255, 255, 200))

                # Draw text
                draw.text(text_pos, text, fill=self.text_color, font=self.font)

    def _draw_region_box(self, draw: ImageDraw, region: Dict):
        """Draw region bounding box"""
        bbox = region['bbox']
        region_type = region.get('type', 'text')
        color = self.region_colors.get(region_type, (128, 128, 128))

        # Draw thick rectangle
        for i in range(5):  # Draw multiple lines for thickness
            draw.rectangle(
                [(bbox[0] + i, bbox[1] + i), (bbox[2] - i, bbox[3] - i)],
                outline=color,
                width=1
            )

        # Draw label with background
        label = f"{region_type.upper()}"
        if region.get('confidence'):
            label += f" ({region['confidence']:.2f})"

        if region_type == 'table' and 'rows' in region:
            label += f" {region['rows']}x{region.get('columns', '?')}"

        label_pos = (bbox[0] + 5, bbox[1] + 5)

        # Background
        label_bbox = draw.textbbox(label_pos, label, font=self.font)
        draw.rectangle(
            [(label_bbox[0] - 3, label_bbox[1] - 3),
             (label_bbox[2] + 3, label_bbox[3] + 3)],
            fill=color + (200,)  # Semi-transparent
        )

        # Text
        draw.text(label_pos, label, fill=(255, 255, 255), font=self.font)

    def save_visualization(
        self,
        image: np.ndarray,
        regions: List[Dict],
        output_path: str,
        show_text: bool = True,
        show_boxes: bool = True
    ):
        """Save visualization to file"""
        result = self.visualize_regions(image, regions, show_text, show_boxes)

        # Save with support for non-ASCII paths
        output_path = str(output_path)
        try:
            _, encoded = cv2.imencode('.jpg', result)
            encoded.tofile(output_path)
        except:
            cv2.imwrite(output_path, result)

        print(f"  Visualization saved: {output_path}")


def draw_ocr_result(
    image_path: str,
    ocr_result: List,
    output_path: str
):
    """
    Draw OCR result in PaddleOCR style

    Args:
        image_path: Input image path
        ocr_result: PaddleOCR result format: [[box, (text, conf)], ...]
        output_path: Output image path
    """
    # Read image
    img = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), cv2.IMREAD_COLOR)

    # Convert OCR result to boxes format
    ocr_boxes = []
    for line in ocr_result:
        if line:
            box, (text, conf) = line
            ocr_boxes.append({
                'box': box,
                'text': text,
                'confidence': conf
            })

    # Create dummy region covering entire image
    h, w = img.shape[:2]
    regions = [{
        'type': 'text',
        'bbox': [0, 0, w, h],
        'confidence': 1.0,
        'ocr_boxes': ocr_boxes
    }]

    # Visualize
    visualizer = OCRVisualizer()
    visualizer.save_visualization(
        img,
        regions,
        output_path,
        show_text=True,
        show_boxes=False  # Don't show the full-image box
    )
