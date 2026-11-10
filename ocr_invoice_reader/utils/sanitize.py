"""
Allow-list sanitizer for the table HTML that PaddleOCR-VL produces.

The model transcribes text it sees in the document, so a crafted PDF or image
can put arbitrary markup (e.g. ``<script>``) into ``block.html``. Only table
structure tags and a few harmless attributes are kept; everything else is
dropped or escaped. Standard library only.
"""
from __future__ import annotations

import html
from html.parser import HTMLParser
from typing import List, Optional, Tuple

_ALLOWED_TAGS = {
    "table", "thead", "tbody", "tfoot", "tr", "th", "td",
    "caption", "colgroup", "col", "br", "b", "strong", "i", "em",
    "sub", "sup", "span", "p",
}
_VOID_TAGS = {"br", "col"}
# Tags whose *content* must be discarded entirely, not just the tag.
_DROP_CONTENT_TAGS = {"script", "style", "iframe", "object", "embed", "template", "noscript"}
_ALLOWED_ATTRS = {"colspan", "rowspan", "align", "valign"}


class _TableSanitizer(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.out: List[str] = []
        self._drop_depth = 0

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        if tag in _DROP_CONTENT_TAGS:
            self._drop_depth += 1
            return
        if self._drop_depth or tag not in _ALLOWED_TAGS:
            return
        kept = []
        for name, value in attrs:
            if name in _ALLOWED_ATTRS and value is not None:
                if name in {"colspan", "rowspan"} and not value.isdigit():
                    continue
                kept.append(f' {name}="{html.escape(value, quote=True)}"')
        self.out.append(f"<{tag}{''.join(kept)}>")

    def handle_startendtag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        if tag in _DROP_CONTENT_TAGS:
            return
        self.handle_starttag(tag, attrs)
        if tag in _ALLOWED_TAGS and tag not in _VOID_TAGS and not self._drop_depth:
            self.out.append(f"</{tag}>")

    def handle_endtag(self, tag: str) -> None:
        if tag in _DROP_CONTENT_TAGS:
            self._drop_depth = max(0, self._drop_depth - 1)
            return
        if self._drop_depth or tag not in _ALLOWED_TAGS or tag in _VOID_TAGS:
            return
        self.out.append(f"</{tag}>")

    def handle_data(self, data: str) -> None:
        if not self._drop_depth:
            self.out.append(html.escape(data, quote=False))


def sanitize_table_html(fragment: str) -> str:
    """Return ``fragment`` with only safe table markup left."""
    parser = _TableSanitizer()
    parser.feed(fragment or "")
    parser.close()
    return "".join(parser.out)
