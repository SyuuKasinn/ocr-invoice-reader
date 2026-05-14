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

from ocr_invoice_reader.processors.structure_analyzer import LayoutRegion
from ocr_invoice_reader.utils.text_processor import TextProcessor
from ocr_invoice_reader.utils.image_optimizer import ImageOptimizer


class EnhancedStructureAnalyzer:
    """Enhanced structure analyzer with better table detection"""

    def __init__(self, use_gpu: bool = True, lang: str = 'ch', optimize_images: bool = False):
        if not PPSTRUCTURE_AVAILABLE:
            raise ImportError("PaddleOCR not available")

        self.use_gpu = use_gpu
        self.lang = lang
        self.optimize_images = optimize_images
        self.text_processor = TextProcessor()
        self.image_optimizer = ImageOptimizer(max_size=2000) if optimize_images else None
        device = 'gpu' if use_gpu else 'cpu'

        print("Initializing Enhanced PP-Structure with OCR v4 models...")

        # PP-Structure with optimized parameters for table detection
        self.structure_engine = PPStructure(
            layout=True,
            table=True,
            ocr=True,
            show_log=False,
            lang='ch',
            device=device,
            use_angle_cls=False,
            # PaddleOCR v4 models (faster and more accurate)
            det_model_dir=None,  # Will auto-download ch_PP-OCRv4_det
            rec_model_dir=None,  # Will auto-download ch_PP-OCRv4_rec
            # Enhanced table detection parameters
            table_max_len=488,
            layout_score_threshold=0.4,  # Balanced threshold
            layout_nms_threshold=0.4,    # Balanced NMS for overlapping regions
        )

        # Separate OCR engine for better text recognition with v4 models
        self.ocr_engine = PaddleOCR(
            use_angle_cls=False,
            lang=lang,
            device=device,
            show_log=False,
            # PaddleOCR v4 models - 30% faster than v3
            det_model_dir=None,  # Will auto-download corresponding v4 det model
            rec_model_dir=None,  # Will auto-download corresponding v4 rec model
            det_db_thresh=0.3,      # Balanced threshold for text detection
            det_db_box_thresh=0.5,  # Balanced box detection
            rec_batch_num=6,        # Batch processing for better performance
        )

        print("Enhanced PP-Structure initialized")

    def analyze(self, image_path: str) -> Dict[str, Any]:
        """Analyze with enhanced structure detection"""

        # Read image
        img = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError(f"Cannot read image: {image_path}")

        # Optimize image for faster processing
        if self.image_optimizer:
            img = self.image_optimizer.optimize(img, verbose=False)

        print(f"\n[Enhanced Analysis] {Path(image_path).name}")

        # Try PP-Structure first
        print("  Running PP-Structure with enhanced parameters...")
        try:
            result = self.structure_engine(img)

            if result and len(result) > 1:
                # Multiple regions detected - process them
                print(f"  PP-Structure detected {len(result)} regions")

                # Check region types
                region_types = [item.get('type', 'unknown') for item in result]
                table_count = region_types.count('table')

                print(f"    Region types: {dict((t, region_types.count(t)) for t in set(region_types))}")

                # If no tables detected but we expect them (invoice-like documents)
                # Use coordinate-based analysis which is better at finding tables
                if table_count == 0:
                    print("  WARNING: No tables detected by PP-Structure")
                    print("  Using coordinate-based analysis for better table detection...")
                    return self._coordinate_based_analysis(img, image_path)

                processed_result = self._process_ppstructure_result(result, img, image_path)

                # Validate: check if we have meaningful content
                total_text_length = sum(
                    len(r.text.strip()) for r in processed_result['regions']
                    if hasattr(r, 'text') and r.text
                )

                # Check if we have reasonable amount of content
                # For typical invoices, expect at least 200 chars
                has_sufficient_content = total_text_length > 200

                # Also check if there are any table regions with content
                has_tables = any(
                    r.type == 'table' and len(r.text.strip()) > 50
                    for r in processed_result['regions']
                    if hasattr(r, 'text') and r.text
                )

                if has_sufficient_content or has_tables:
                    return processed_result
                else:
                    print(f"  ⚠ PP-Structure found insufficient content ({total_text_length} chars)")
                    print("  Falling back to coordinate-based analysis...")
                    return self._coordinate_based_analysis(img, image_path)
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
            confidence = item.get('confidence', 0.0)

            # Create LayoutRegion object
            region = LayoutRegion(
                region_type=region_type,
                bbox=bbox,
                confidence=confidence
            )

            if region_type == 'table':
                region.table_html = item.get('res', {}).get('html', '')

                # Extract text from table result
                table_text = ""
                res = item.get('res', {})
                if isinstance(res, dict):
                    # Try to get text from HTML
                    html = res.get('html', '')
                    if html:
                        # Simple HTML text extraction
                        import re
                        # Remove HTML tags
                        text_only = re.sub(r'<[^>]+>', ' ', html)
                        text_only = re.sub(r'\s+', ' ', text_only).strip()
                        table_text = text_only

                # Fallback: If table content is empty or too short, use OCR on table region
                if not table_text or len(table_text) < 10:
                    print(f"    ⚠ Table region has empty/minimal content, using OCR fallback...")
                    table_text = self._ocr_table_region(img, bbox)
                    region.table_html = ""  # Clear invalid HTML

                region.text = table_text
                print(f"    ✓ Table region: {len(table_text)} chars")
            else:
                res = item.get('res', [])
                if isinstance(res, list):
                    texts = []
                    for line in res:
                        if isinstance(line, dict):
                            text = line.get('text', '')
                        elif isinstance(line, (list, tuple)) and len(line) >= 2:
                            text = str(line[1][0])
                        else:
                            continue

                        # Process text to fix concatenation issues
                        text = self.text_processor.process_ocr_result(text, split_words=True)
                        texts.append(text)

                    region.text = '\n'.join(texts)
                    print(f"    ✓ {region_type} region: {len(texts)} lines")

            regions.append(region)

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

                # Process text to improve quality
                processed_text = self.text_processor.process_ocr_result(text, split_words=True)

                boxes.append({
                    'bbox': [int(x1), int(y1), int(x2), int(y2)],
                    'text': processed_text,
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

    def _detect_table_regions(self, boxes: List[Dict], img_shape: Tuple) -> List[LayoutRegion]:
        """Detect table regions based on coordinate analysis"""

        if not boxes:
            return []

        # Filter out noise boxes (single characters that are likely artifacts)
        filtered_boxes = []
        for box in boxes:
            text = box['text'].strip()
            # Keep box if:
            # 1. Text has more than 1 character, OR
            # 2. It's a number or common punctuation, OR
            # 3. Text has high confidence (>0.98) and is part of a larger structure
            if len(text) > 1 or text.isdigit() or text in '.,;:()[]{}+-=':
                filtered_boxes.append(box)
            elif box['confidence'] > 0.98 and len(text) == 1:
                # Single character with very high confidence - might be valid
                # Check if it's surrounded by other boxes (not isolated)
                nearby_boxes = [b for b in boxes if b != box and
                               abs(b['center_y'] - box['center_y']) < 50 and
                               abs(b['center_x'] - box['center_x']) < 200]
                if len(nearby_boxes) > 0:
                    filtered_boxes.append(box)

        if not filtered_boxes:
            return []

        boxes = filtered_boxes

        # Group boxes by horizontal position (columns)
        # Group boxes by vertical position (rows)

        # Sort by Y position (top to bottom)
        sorted_boxes = sorted(boxes, key=lambda b: b['center_y'])

        # Detect rows (boxes at similar Y positions)
        rows = []
        current_row = [sorted_boxes[0]]
        row_threshold = 35  # pixels tolerance (increased for better grouping)

        for box in sorted_boxes[1:]:
            if abs(box['center_y'] - current_row[-1]['center_y']) < row_threshold:
                current_row.append(box)
            else:
                rows.append(current_row)
                current_row = [box]
        rows.append(current_row)

        print(f"    Detected {len(rows)} rows (from {len(boxes)} filtered boxes)")

        # Detect table-like patterns (multiple rows with similar column structure)
        table_regions = []
        current_table = []
        min_table_rows = 2  # Minimum rows to be considered a table (lowered to catch more tables)

        for i, row in enumerate(rows):
            # Sort boxes in row by X position
            row_sorted = sorted(row, key=lambda b: b['center_x'])

            # Filter out very short text in single-item rows (likely noise)
            if len(row_sorted) == 1:
                text = row_sorted[0]['text'].strip()
                # Skip single character rows unless they're numbers or in top 30%
                if len(text) <= 1 and not text.isdigit() and i > len(rows) * 0.3:
                    continue

            if len(row_sorted) >= 2:  # Row has multiple columns
                current_table.append((i, row_sorted))
            else:
                # Single column - might be title or section header
                # Check if we should extend current table (might be a merged row)
                if current_table:
                    last_table_row = current_table[-1]
                    # If this single-column row is close to the table, it might be part of it
                    if i - last_table_row[0] <= 2:  # Within 2 rows
                        # Add to table as a full-width row
                        current_table.append((i, row_sorted))
                        continue

                if current_table and len(current_table) >= min_table_rows:
                    # Save current table
                    table_regions.append(self._create_table_region(current_table))
                    current_table = []

                # Add as text region (with minimum text length check)
                if row_sorted:
                    combined_text = ' '.join(b['text'] for b in row_sorted).strip()

                    # Skip if text is too short (likely noise)
                    if len(combined_text) < 2:
                        continue

                    # Determine region type based on position and content
                    if i < len(rows) * 0.15 and len(combined_text) < 50:
                        region_type = 'title'
                    else:
                        region_type = 'text'

                    region = LayoutRegion(
                        region_type=region_type,
                        bbox=self._get_region_bbox(row_sorted),
                        confidence=sum(b['confidence'] for b in row_sorted) / len(row_sorted)
                    )
                    region.text = combined_text
                    table_regions.append(region)

        # Don't forget the last table
        if current_table and len(current_table) >= min_table_rows:
            table_regions.append(self._create_table_region(current_table))

        # Post-process: merge adjacent table regions if they're close
        table_regions = self._merge_adjacent_tables(table_regions)

        # Filter out empty or near-empty regions
        table_regions = self._filter_empty_regions(table_regions)

        return table_regions

    def _filter_empty_regions(self, regions: List[LayoutRegion]) -> List[LayoutRegion]:
        """Filter out empty or near-empty regions"""
        filtered = []

        for region in regions:
            # Check if region has meaningful content
            text = region.text.strip() if region.text else ''

            # Skip if:
            # 1. Text is empty
            # 2. Text is too short (< 2 chars) and not a number
            # 3. Text is only whitespace or punctuation
            if not text:
                continue

            if len(text) < 2 and not text.isdigit():
                continue

            # Check if text is only punctuation/symbols
            if all(c in '.,;:!?()[]{}|-_/' for c in text):
                continue

            # Keep this region
            filtered.append(region)

        return filtered

    def _create_table_region(self, table_rows: List[Tuple]) -> LayoutRegion:
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

        # Create LayoutRegion
        region = LayoutRegion(
            region_type='table',
            bbox=self._get_region_bbox(all_boxes),
            confidence=sum(b['confidence'] for b in all_boxes) / len(all_boxes)
        )
        region.text = '\n'.join([' | '.join(b['text'] for b in row) for _, row in table_rows])
        region.table_html = table_html

        # Store additional table info as attributes
        region.rows = len(table_rows)
        region.columns = max(len(row) for _, row in table_rows)

        # Store OCR boxes for visualization
        region.ocr_boxes = all_boxes

        return region

    def _get_region_bbox(self, boxes: List[Dict]) -> List[int]:
        """Get bounding box for a group of boxes"""
        if not boxes:
            return [0, 0, 0, 0]

        x1 = min(b['bbox'][0] for b in boxes)
        y1 = min(b['bbox'][1] for b in boxes)
        x2 = max(b['bbox'][2] for b in boxes)
        y2 = max(b['bbox'][3] for b in boxes)

        return [x1, y1, x2, y2]

    def _ocr_table_region(self, img: np.ndarray, bbox: List[int]) -> str:
        """
        OCR a specific table region when PP-Structure fails

        Args:
            img: Full image
            bbox: Bounding box [x1, y1, x2, y2]

        Returns:
            Extracted text from the region
        """
        try:
            # Extract region from image
            x1, y1, x2, y2 = bbox
            x1, y1 = max(0, int(x1)), max(0, int(y1))
            x2, y2 = min(img.shape[1], int(x2)), min(img.shape[0], int(y2))

            # Add padding for better recognition
            padding = 10
            x1 = max(0, x1 - padding)
            y1 = max(0, y1 - padding)
            x2 = min(img.shape[1], x2 + padding)
            y2 = min(img.shape[0], y2 + padding)

            region_img = img[y1:y2, x1:x2]

            if region_img.size == 0:
                return ""

            # Run OCR on the region
            ocr_result = self.ocr_engine.ocr(region_img, cls=False)

            if not ocr_result or not ocr_result[0]:
                return ""

            # Extract and process text
            lines = []
            for line in ocr_result[0]:
                if line:
                    _, (text, conf) = line
                    if conf > 0.5:  # Only use high confidence results
                        # Process text
                        text = self.text_processor.process_ocr_result(text, split_words=True)
                        lines.append(text)

            return '\n'.join(lines)

        except Exception as e:
            print(f"      Error in OCR fallback: {e}")
            return ""

    def _merge_adjacent_tables(self, regions: List[LayoutRegion]) -> List[LayoutRegion]:
        """Merge adjacent table regions that are likely part of the same table"""
        if len(regions) < 2:
            return regions

        merged = []
        i = 0

        while i < len(regions):
            current = regions[i]

            # Only try to merge tables
            if current.type != 'table':
                merged.append(current)
                i += 1
                continue

            # Look ahead for adjacent tables
            j = i + 1
            tables_to_merge = [current]

            while j < len(regions):
                next_region = regions[j]

                # Check if next region is a table and is close vertically
                if next_region.type == 'table':
                    # Calculate vertical distance
                    current_bottom = current.bbox[3]
                    next_top = next_region.bbox[1]
                    vertical_gap = next_top - current_bottom

                    # Check horizontal overlap
                    current_left = current.bbox[0]
                    current_right = current.bbox[2]
                    next_left = next_region.bbox[0]
                    next_right = next_region.bbox[2]

                    horizontal_overlap = min(current_right, next_right) - max(current_left, next_left)
                    overlap_ratio = horizontal_overlap / max(current_right - current_left, next_right - next_left)

                    # Merge if: close vertically AND significant horizontal overlap
                    if vertical_gap < 100 and overlap_ratio > 0.5:
                        tables_to_merge.append(next_region)
                        current = next_region  # Update current for next iteration
                        j += 1
                    else:
                        break
                else:
                    # Non-table region, stop merging
                    break

            # Merge collected tables
            if len(tables_to_merge) > 1:
                merged_region = self._merge_table_regions(tables_to_merge)
                merged.append(merged_region)
                i = j
            else:
                merged.append(current)
                i += 1

        return merged

    def _merge_table_regions(self, table_regions: List[LayoutRegion]) -> LayoutRegion:
        """Merge multiple table regions into one"""
        # Calculate merged bounding box
        x1 = min(r.bbox[0] for r in table_regions)
        y1 = min(r.bbox[1] for r in table_regions)
        x2 = max(r.bbox[2] for r in table_regions)
        y2 = max(r.bbox[3] for r in table_regions)

        # Merge text
        merged_text = '\n'.join(r.text for r in table_regions if r.text)

        # Merge HTML
        merged_html = ''
        for r in table_regions:
            if hasattr(r, 'table_html') and r.table_html:
                # Extract table body content
                html = r.table_html.replace('<table>', '').replace('</table>', '')
                merged_html += html

        if merged_html:
            merged_html = f'<table>{merged_html}</table>'

        # Calculate average confidence
        avg_confidence = sum(r.confidence for r in table_regions) / len(table_regions)

        # Create merged region
        merged = LayoutRegion(
            region_type='table',
            bbox=[x1, y1, x2, y2],
            confidence=avg_confidence
        )
        merged.text = merged_text
        merged.table_html = merged_html if merged_html else None

        # Sum rows and columns
        total_rows = sum(getattr(r, 'rows', 0) for r in table_regions)
        max_columns = max(getattr(r, 'columns', 0) for r in table_regions)

        merged.rows = total_rows
        merged.columns = max_columns

        return merged
