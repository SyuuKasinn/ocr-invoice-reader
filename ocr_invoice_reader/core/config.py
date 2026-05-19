"""Centralized configuration for the PaddleOCR-VL pipeline."""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class VLConfig:
    """PaddleOCR-VL 1.5 pipeline options."""
    use_gpu: bool = True
    lang: Optional[str] = None
    use_doc_orientation_classify: bool = False
    use_doc_unwarping: bool = False


@dataclass
class IOConfig:
    output_dir: str = "results"
    pdf_dpi: int = 300
    save_markdown: bool = True
    save_visualization: bool = True
    save_per_page_json: bool = True
    inline_images_in_html: bool = True


@dataclass
class PipelineConfig:
    vl: VLConfig = field(default_factory=VLConfig)
    io: IOConfig = field(default_factory=IOConfig)

    @classmethod
    def default(cls) -> "PipelineConfig":
        return cls()
