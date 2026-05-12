"""
Enhanced structure analyzer with better table detection
"""
import os
import cv2
import numpy as np
from typing import List, Dict, Any, Tuple
from pathlib import Path

try:
    from paddleocr import PPStructure, PaddleOCR
    PPSTRUCTURE_AVAILABLE = True
except ImportError:
    PPSTRUCTURE_AVAILABLE = False


class EnhancedStructureAnalyzer:
    """Enhanced structure analyzer with better table detection"""

    def __init__(self, use_gpu: bool = True, lang: str = 'ch'):
        if not PPSTRUCTURE_AVAILABLE:
            raise ImportError("PaddleOCR not available")

        self.use_gpu = use_gpu
        self.lang = lang
        device = 'gpu' if use_gpu else 'cpu'

        print("Initializing Enhanced PP-Structure...")

        # PP-Structure with optimized parameters for table detection
        self.structure_engine = PPStructure(
            layout=True,
            table=True,
            ocr=True,
            show_log=False,
            lang='ch',
            device=device,
            use_angle_cls=False,
            # Enhanced table detection parameters
            table_max_len=488,
            layout_score_threshold=0.3,  # Lower threshold to detect more regions
            layout_nms_threshold=0.3,     # Lower NMS for overlapping regions
        )

        # Separate OCR engine for better text recognition
        self.ocr_engine = PaddleOCR(
            use_angle_cls=False,
            lang=lang,
            device=device,
            show_log=False,
            det_db_thresh=0.2,      # Lower threshold for text detection
            det_db_box_thresh=0.4,  # More sensitive box detection
        )

        print("Enhanced PP-Structure initialized")

    def analyze(self, image_path: str) -> Dict[str, Any]:
        """Analyze with enhanced structure detection"""

        # Read image
        img = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError(f"Cannot read image: {image_path}")

        print(f"\n[Enhanced Analysis] {Path(image_path).name}")

        # Try PP-Structure first
        print("  Running PP-Structure with enhanced parameters...")
        try:
            result = self.structure_engine(img)

            if result and len(result) > 1:
                # Multiple regions detected - good!
                print(f"  PP-Structure detected {len(result)} regions")
                return self._process_ppstructure_result(result, img, image_path)
            else:
                print(f"  PP-Structure only found {len(result) if result else 0} region(s)")
                print("  Falling back to coordinate-based analysis...")
                return self._coordinate_based_analysis(img, image_path)

        except Exception as e:
            print(f"  PP-Structure failed: {e}")
            print("  Falling back to coordinate-based analysis...")
            return self._coordinate_based_analysis(img, image_path)

    def _process_ppstructure_result(self, result: List, img: np.ndarray, image_path: str) -> Dict[str, Any]:
        """Process PP-Structure result"""
        regions = []

        for item in result:
            region_type = item.get('type', 'text')
            bbox = item.get('bbox', [0, 0, 100, 100])

            region_info = {
                'type': region_type,
                'bbox': bbox,
                'confidence': item.get('confidence', 0.0),
                'text': '',
                'table_html': None,
            }

            if region_type == 'table':
                region_info['table_html'] = item.get('res', {}).get('html', '')
                print(f"    ✓ Table region: {len(region_info['table_html'])} chars")
            else:
                res = item.get('res', [])
                if isinstance(res, list):
                    texts = []
                    for line in res:
                        if isinstance(line, dict):
                            texts.append(line.get('text', ''))
                        elif isinstance(line, (list, tuple)) and len(line) >= 2:
                            texts.append(str(line[1][0]))
                    region_info['text'] = '\n'.join(texts)
                    print(f"    ✓ {region_type} region: {len(texts)} lines")

            regions.append(region_info)

        return {
            'method': 'ppstructure_enhanced',
            'regions': regions,
            'image_path': image_path
        }

    def _coordinate_based_analysis(self, img: np.ndarray, image_path: str) -> Dict[str, Any]:
        """Fallback: coordinate-based structure detection"""
        print("  Running OCR for coordinate analysis...")

        # Run OCR
        ocr_result = self.ocr_engine.ocr(img, cls=False)

        if not ocr_result or not ocr_result[0]:
            return {'method': 'coordinate_based', 'regions': [], 'image_path': image_path}

        # Extract all text boxes with coordinates
        boxes = []
        for line in ocr_result[0]:
            if line:
                box, (text, conf) = line
                # Convert box to [x1, y1, x2, y2]
                box_np = np.array(box)
                x1, y1 = box_np[:, 0].min(), box_np[:, 1].min()
                x2, y2 = box_np[:, 0].max(), box_np[:, 1].max()

                boxes.append({
                    'bbox': [int(x1), int(y1), int(x2), int(y2)],
                    'text': text,
                    'confidence': conf,
                    'center_y': (y1 + y2) / 2,
                    'center_x': (x1 + x2) / 2,
                })

        print(f"  OCR detected {len(boxes)} text boxes")

        # Detect table structure by analyzing spatial layout
        regions = self._detect_table_regions(boxes, img.shape)

        print(f"  Detected {len(regions)} structured regions")

        return {
            'method': 'coordinate_based',
            'regions': regions,
            'image_path': image_path,
            'ocr_boxes': boxes  # Include raw OCR boxes for further analysis
        }

    def _detect_table_regions(self, boxes: List[Dict], img_shape: Tuple) -> List[Dict]:
        """Detect table regions based on coordinate analysis"""

        if not boxes:
            return []

        # Group boxes by horizontal position (columns)
        # Group boxes by vertical position (rows)

        # Sort by Y position (top to bottom)
        sorted_boxes = sorted(boxes, key=lambda b: b['center_y'])

        # Detect rows (boxes at similar Y positions)
        rows = []
        current_row = [sorted_boxes[0]]
        row_threshold = 30  # pixels tolerance

        for box in sorted_boxes[1:]:
            if abs(box['center_y'] - current_row[-1]['center_y']) < row_threshold:
                current_row.append(box)
            else:
                rows.append(current_row)
                current_row = [box]
        rows.append(current_row)

        print(f"    Detected {len(rows)} rows")

        # Detect table-like patterns (multiple rows with similar column structure)
        table_regions = []
        current_table = []

        for i, row in enumerate(rows):
            # Sort boxes in row by X position
            row_sorted = sorted(row, key=lambda b: b['center_x'])

            if len(row_sorted) >= 2:  # Row has multiple columns
                current_table.append((i, row_sorted))
            else:
                # Single column - might be title or section header
                if current_table and len(current_table) >= 2:
                    # Save current table
                    table_regions.append(self._create_table_region(current_table))
                    current_table = []

                # Add as text region
                if row_sorted:
                    table_regions.append({
                        'type': 'title' if i < len(rows) * 0.2 else 'text',
                        'bbox': self._get_region_bbox(row_sorted),
                        'confidence': sum(b['confidence'] for b in row_sorted) / len(row_sorted),
                        'text': ' '.join(b['text'] for b in row_sorted),
                        'table_html': None,
                    })

        # Don't forget the last table
        if current_table and len(current_table) >= 2:
            table_regions.append(self._create_table_region(current_table))

        return table_regions

    def _create_table_region(self, table_rows: List[Tuple]) -> Dict:
        """Create a table region from detected rows"""
        all_boxes = []
        for _, row in table_rows:
            all_boxes.extend(row)

        # Generate simple HTML table
        html_rows = []
        for row_idx, row_boxes in table_rows:
            cells = [f"<td>{box['text']}</td>" for box in row_boxes]
            html_rows.append(f"<tr>{''.join(cells)}</tr>")

        table_html = f"<table>{''.join(html_rows)}</table>"

        return {
            'type': 'table',
            'bbox': self._get_region_bbox(all_boxes),
            'confidence': sum(b['confidence'] for b in all_boxes) / len(all_boxes),
            'text': '\n'.join([' | '.join(b['text'] for b in row) for _, row in table_rows]),
            'table_html': table_html,
            'rows': len(table_rows),
            'columns': max(len(row) for _, row in table_rows),
        }

    def _get_region_bbox(self, boxes: List[Dict]) -> List[int]:
        """Get bounding box for a group of boxes"""
        if not boxes:
            return [0, 0, 0, 0]

        x1 = min(b['bbox'][0] for b in boxes)
        y1 = min(b['bbox'][1] for b in boxes)
        x2 = max(b['bbox'][2] for b in boxes)
        y2 = max(b['bbox'][3] for b in boxes)

        return [x1, y1, x2, y2]
