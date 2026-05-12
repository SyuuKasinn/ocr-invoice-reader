"""
Document information extraction system
"""
import os
from pathlib import Path
from typing import List, Optional
from datetime import datetime
import json

from ocr_invoice_reader.processors.structure_analyzer import StructureAnalyzer
from ocr_invoice_reader.processors.field_extractor import FieldExtractor
from ocr_invoice_reader.processors.file_handler import FileProcessor
from ocr_invoice_reader.models.base import BaseDocument


class DocumentExtractor:
    """
    Document information extraction system

    Extracts structured information from invoices, waybills, and other documents.
    Uses PP-Structure for layout analysis and rule-based field extraction.
    """

    def __init__(self, use_gpu: bool = True, lang: str = 'japan'):
        """
        Initialize document extractor

        Args:
            use_gpu: Use GPU acceleration
            lang: Language for OCR (ch/en/japan/korean/latin)
        """
        self.structure_analyzer = StructureAnalyzer(use_gpu=use_gpu, lang=lang)
        self.field_extractor = FieldExtractor()
        self.file_processor = FileProcessor()

    def extract(self, image_path: str, visualize: bool = False) -> BaseDocument:
        """
        Extract structured information from document image

        Args:
            image_path: Path to document image or PDF
            visualize: Save visualization result

        Returns:
            BaseDocument with extracted fields
        """
        # Check if PDF - convert first
        if Path(image_path).suffix.lower() == '.pdf':
            temp_images = self.file_processor.process_file(image_path)
            if not temp_images:
                raise ValueError(f"Failed to convert PDF: {image_path}")
            # Use first page
            image_path = temp_images[0]

        # Step 1: Structure analysis
        structure_result = self.structure_analyzer.analyze(image_path, visualize=visualize)

        # Step 2: Extract fields
        all_text = self.structure_analyzer.extract_all_text(structure_result)
        document = self.field_extractor.extract(
            text=all_text,
            regions=structure_result['regions'],
            source_file=image_path
        )

        return document

    def batch_extract(
        self,
        input_path: str,
        output_dir: Optional[str] = None,
        visualize: bool = False
    ) -> List[BaseDocument]:
        """
        Batch extract from multiple files

        Args:
            input_path: Input file or directory
            output_dir: Output directory (auto-generated if None)
            visualize: Save visualization results

        Returns:
            List of extracted documents
        """
        # Create output directory
        if output_dir is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = f"extracted_data/{timestamp}"

        os.makedirs(output_dir, exist_ok=True)

        # Get image files
        if os.path.isfile(input_path):
            image_paths = self.file_processor.process_file(input_path)
        elif os.path.isdir(input_path):
            all_files = []
            for ext in ['.jpg', '.jpeg', '.png', '.pdf']:
                all_files.extend(Path(input_path).glob(f"*{ext}"))

            image_paths = []
            for file in all_files:
                image_paths.extend(self.file_processor.process_file(str(file)))
        else:
            raise ValueError(f"Invalid input path: {input_path}")

        if not image_paths:
            return []

        # Process each image
        documents = []
        for idx, image_path in enumerate(image_paths, 1):
            print(f"\nProcessing {idx}/{len(image_paths)}: {Path(image_path).name}")

            try:
                document = self.extract(image_path, visualize=visualize)
                documents.append(document)

                # Save result
                base_name = Path(image_path).stem
                output_file = Path(output_dir) / f"{base_name}_extracted.json"
                document.save_to_file(str(output_file))

            except Exception as e:
                print(f"Error processing {Path(image_path).name}: {e}")

        # Generate summary
        self._generate_summary(documents, output_dir)

        # Cleanup temp files
        self.file_processor.cleanup()

        return documents

    def _generate_summary(self, documents: List[BaseDocument], output_dir: str):
        """Generate summary report"""
        summary_file = Path(output_dir) / "extraction_summary.json"

        summary = {
            'timestamp': datetime.now().isoformat(),
            'total_documents': len(documents),
            'documents': [doc.get_summary() for doc in documents],
            'statistics': {
                'avg_confidence': sum(d.confidence for d in documents) / len(documents) if documents else 0,
                'document_types': {},
                'extraction_methods': {}
            }
        }

        for doc in documents:
            doc_type = doc.document_type
            summary['statistics']['document_types'][doc_type] = \
                summary['statistics']['document_types'].get(doc_type, 0) + 1

            method = doc.extraction_method
            summary['statistics']['extraction_methods'][method] = \
                summary['statistics']['extraction_methods'].get(method, 0) + 1

        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
