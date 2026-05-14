"""
Simple OCR extractor (legacy ocr_reader.py functionality)
"""
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

try:
    from paddleocr import PaddleOCR
    PADDLEOCR_AVAILABLE = True
except ImportError:
    PADDLEOCR_AVAILABLE = False


class SimpleOCR:
    """
    Simple OCR text recognition (legacy functionality)

    For basic OCR text extraction without structure analysis.
    """

    def __init__(
        self,
        lang: str = 'japan',
        use_gpu: bool = True,
        confidence_threshold: float = 0.5,
        handwriting_mode: bool = False,
        enable_correction: bool = True
    ):
        """
        Initialize simple OCR

        Args:
            lang: OCR language
            use_gpu: Use GPU acceleration
            confidence_threshold: Minimum confidence threshold
            handwriting_mode: Enable handwriting recognition mode
            enable_correction: Enable text correction
        """
        if not PADDLEOCR_AVAILABLE:
            raise ImportError("PaddleOCR not available. Install: pip install paddleocr")

        self.lang = lang
        self.confidence_threshold = confidence_threshold
        self.handwriting_mode = handwriting_mode
        self.enable_correction = enable_correction

        # Initialize OCR
        device = 'gpu' if use_gpu else 'cpu'

        if handwriting_mode:
            self.ocr = PaddleOCR(
                use_angle_cls=True,
                lang=lang,
                device=device,
                show_log=False,
                use_textline_orientation=True,
                # PaddleOCR v4 models (auto-download)
                rec_model_dir=None,  # Will use v4 rec model
                det_model_dir=None,  # Will use v4 det model
            )
        else:
            self.ocr = PaddleOCR(
                use_angle_cls=False,
                lang=lang,
                device=device,
                show_log=False,
                # PaddleOCR v4 models - 30% faster than v3
                det_model_dir=None,  # Auto-download v4 det model
                rec_model_dir=None,  # Auto-download v4 rec model
            )

        # Text corrector
        if enable_correction:
            try:
                from ocr_invoice_reader.utils.text_corrector import TextCorrector
                self.text_corrector = TextCorrector(
                    enable_english=True,
                    enable_chinese=True,
                    enable_rules=True
                )
            except:
                self.text_corrector = None
        else:
            self.text_corrector = None

    def recognize(self, image_path: str) -> Dict[str, Any]:
        """
        Recognize text from image

        Args:
            image_path: Path to image file

        Returns:
            Dictionary with recognition results
        """
        result = self.ocr.ocr(image_path, cls=False)

        if not result or not result[0]:
            return {
                'image_path': image_path,
                'timestamp': datetime.now().isoformat(),
                'total_lines': 0,
                'results': [],
                'full_text': ''
            }

        # Process results
        results = []
        texts = []

        for line in result[0]:
            if line:
                box, (text, confidence) = line

                if confidence >= self.confidence_threshold:
                    # Apply correction if enabled
                    original_text = text
                    if self.text_corrector:
                        text = self.text_corrector.correct_text(text, lang_hint=self.lang)

                    results.append({
                        'text': text,
                        'original_text': original_text,
                        'confidence': float(confidence),
                        'box': [[float(p[0]), float(p[1])] for p in box]
                    })
                    texts.append(text)

        return {
            'image_path': image_path,
            'timestamp': datetime.now().isoformat(),
            'total_lines': len(results),
            'results': results,
            'full_text': '\n'.join(texts)
        }

    def batch_recognize(
        self,
        input_dir: str,
        output_dir: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Batch recognize multiple images

        Args:
            input_dir: Input directory
            output_dir: Output directory

        Returns:
            List of recognition results
        """
        if output_dir is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = f"ocr_results/{timestamp}"

        os.makedirs(output_dir, exist_ok=True)

        # Get image files
        image_files = []
        for ext in ['.jpg', '.jpeg', '.png', '.bmp']:
            image_files.extend(Path(input_dir).glob(f"*{ext}"))

        results = []
        for image_path in image_files:
            print(f"Processing: {image_path.name}")
            result = self.recognize(str(image_path))
            results.append(result)

            # Save result
            output_file = Path(output_dir) / f"{image_path.stem}_ocr.json"
            import json
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

        return results
