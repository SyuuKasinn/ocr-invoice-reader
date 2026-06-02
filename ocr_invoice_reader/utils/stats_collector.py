"""
统计收集模块：收集和分析文档处理统计信息

与现有 OCRVisualizer 配合使用，提供性能监控和准确率分析
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class PageStats:
    """单页统计"""
    page_index: int
    processing_time: float  # 秒
    region_count: int
    text_region_count: int
    table_count: int
    figure_count: int
    total_text_length: int
    avg_confidence: Optional[float] = None
    has_low_confidence: bool = False  # 是否有置信度 < 0.7 的区域


@dataclass
class DocumentStats:
    """文档级统计"""
    document_name: str
    total_pages: int
    total_processing_time: float  # 秒
    avg_page_time: float  # 秒/页

    # 内容统计
    total_regions: int
    total_tables: int
    total_figures: int
    total_text_length: int

    # 性能指标
    throughput: float  # 页/秒
    avg_confidence: Optional[float] = None
    low_confidence_pages: List[int] = field(default_factory=list)

    # 每页详细统计
    page_stats: List[PageStats] = field(default_factory=list)

    @property
    def tables_per_page(self) -> float:
        return self.total_tables / self.total_pages if self.total_pages > 0 else 0.0

    @property
    def regions_per_page(self) -> float:
        return self.total_regions / self.total_pages if self.total_pages > 0 else 0.0


class StatsCollector:
    """统计信息收集器 - 与现有系统集成"""

    CONFIDENCE_THRESHOLD = 0.7

    def __init__(self):
        self.page_timings: Dict[int, tuple[float, float]] = {}  # page_idx: (start, end)
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.document_name: str = ""

    def start_document(self, name: str = ""):
        """开始文档处理计时"""
        self.start_time = time.perf_counter()
        self.document_name = name

    def end_document(self) -> None:
        """结束文档处理计时"""
        self.end_time = time.perf_counter()

    def start_page(self, page_index: int) -> None:
        """开始页面处理计时"""
        self.page_timings[page_index] = (time.perf_counter(), 0.0)

    def end_page(self, page_index: int) -> None:
        """结束页面处理计时"""
        if page_index in self.page_timings:
            start, _ = self.page_timings[page_index]
            self.page_timings[page_index] = (start, time.perf_counter())

    def collect_page_stats(self, regions: List[Dict], page_index: int) -> PageStats:
        """
        从结构分析结果收集单页统计信息

        Args:
            regions: StructureAnalyzer 返回的 regions 列表
            page_index: 页码索引

        Returns:
            PageStats 对象
        """
        # 计算处理时间
        processing_time = 0.0
        if page_index in self.page_timings:
            start, end = self.page_timings[page_index]
            if end > 0:
                processing_time = end - start

        # 统计区域
        region_count = len(regions)
        table_count = sum(1 for r in regions if r.get('type') == 'table')
        figure_count = sum(1 for r in regions if r.get('type') in {'figure', 'image'})
        text_region_count = region_count - table_count - figure_count

        # 统计文本长度
        total_text_length = sum(len(r.get('text', '')) for r in regions)

        # 计算平均置信度
        confidences = [r['confidence'] for r in regions if 'confidence' in r]
        avg_confidence = sum(confidences) / len(confidences) if confidences else None

        # 检查低置信度区域
        has_low_confidence = any(
            c < self.CONFIDENCE_THRESHOLD for c in confidences
        ) if confidences else False

        return PageStats(
            page_index=page_index,
            processing_time=processing_time,
            region_count=region_count,
            text_region_count=text_region_count,
            table_count=table_count,
            figure_count=figure_count,
            total_text_length=total_text_length,
            avg_confidence=avg_confidence,
            has_low_confidence=has_low_confidence,
        )

    def collect_document_stats(
        self,
        all_pages_regions: List[List[Dict]],
        document_name: str = None
    ) -> DocumentStats:
        """
        收集文档级统计信息

        Args:
            all_pages_regions: 所有页面的 regions 列表
            document_name: 文档名称

        Returns:
            DocumentStats 对象
        """
        # 计算总处理时间
        total_time = 0.0
        if self.start_time and self.end_time:
            total_time = self.end_time - self.start_time

        # 收集每页统计
        page_stats_list = []
        for idx, regions in enumerate(all_pages_regions):
            page_stats = self.collect_page_stats(regions, idx)
            page_stats_list.append(page_stats)

        # 聚合统计
        total_regions = sum(ps.region_count for ps in page_stats_list)
        total_tables = sum(ps.table_count for ps in page_stats_list)
        total_figures = sum(ps.figure_count for ps in page_stats_list)
        total_text_length = sum(ps.total_text_length for ps in page_stats_list)

        # 计算平均置信度
        confidences = [
            ps.avg_confidence for ps in page_stats_list
            if ps.avg_confidence is not None
        ]
        avg_confidence = sum(confidences) / len(confidences) if confidences else None

        # 找出低置信度页面
        low_confidence_pages = [
            ps.page_index for ps in page_stats_list
            if ps.has_low_confidence
        ]

        # 计算吞吐量
        total_pages = len(all_pages_regions)
        avg_page_time = total_time / total_pages if total_pages > 0 else 0.0
        throughput = total_pages / total_time if total_time > 0 else 0.0

        return DocumentStats(
            document_name=document_name or self.document_name or "document",
            total_pages=total_pages,
            total_processing_time=total_time,
            avg_page_time=avg_page_time,
            total_regions=total_regions,
            total_tables=total_tables,
            total_figures=total_figures,
            total_text_length=total_text_length,
            throughput=throughput,
            avg_confidence=avg_confidence,
            low_confidence_pages=low_confidence_pages,
            page_stats=page_stats_list,
        )


def format_stats_summary(stats: DocumentStats) -> str:
    """格式化统计摘要为可读文本"""
    lines = [
        f"📄 Document: {stats.document_name}",
        f"📊 Pages: {stats.total_pages}",
        f"⏱️  Total Time: {stats.total_processing_time:.2f}s",
        f"⚡ Throughput: {stats.throughput:.2f} pages/sec",
        f"📝 Regions: {stats.total_regions} (avg {stats.regions_per_page:.1f}/page)",
        f"📋 Tables: {stats.total_tables}",
        f"🖼️  Figures: {stats.total_figures}",
        f"📏 Text Length: {stats.total_text_length:,} chars",
    ]

    if stats.avg_confidence is not None:
        lines.append(f"🎯 Avg Confidence: {stats.avg_confidence:.2%}")

    if stats.low_confidence_pages:
        pages_str = ", ".join(str(p + 1) for p in stats.low_confidence_pages[:5])
        if len(stats.low_confidence_pages) > 5:
            pages_str += f" ... ({len(stats.low_confidence_pages)} total)"
        lines.append(f"⚠️  Low Confidence Pages: {pages_str}")

    return "\n".join(lines)
