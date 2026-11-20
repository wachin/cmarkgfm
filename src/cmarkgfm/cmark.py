"""Python bindings to vnotex/cmark, VNote's cmark fork.

The fork keeps GitHub's extensions (tables, strikethrough, task lists,
autolinks) and adds VNote's own node types (formulas, front matter, alerts,
TOC, wikilinks) *into the core*, so there is no extension-registration API:
everything is enabled by default and ``CMARK_OPT_NO_EXTENSIONS`` turns it off.

Beyond the usual tree API this binding exposes the source-syntax metadata VNote
added for its highlighter:

* :meth:`Node.syntax_extent` -- the exact parser-consumed extent of a node.
* :meth:`Node.syntax_spans` -- the delimiter spans inside it (the ``**`` of
  emphasis, the backticks of code, the brackets of links...). Positions are
  1-based and columns are UTF-8 byte offsets, exactly as cmark reports them.

Both require ``Options.CMARK_OPT_SOURCE_SYNTAX`` at parse time.
"""

from __future__ import annotations

from typing import Iterator, List, Optional, Union

from cmarkgfm import _cmark

_ffi = _cmark.ffi
_lib = _cmark.lib

def _decode(ptr) -> str:
    """Decode a NUL-terminated C string, tolerating NULL."""
    if ptr == _ffi.NULL:
        return ""
    return _ffi.string(ptr).decode("utf-8", "replace")


def _release(ptr) -> None:
    if ptr != _ffi.NULL:
        _lib.free(ptr)


CMARK_VERSION = _decode(_lib.cmark_version_string())


class Options:
    CMARK_OPT_DEFAULT = _lib.CMARK_OPT_DEFAULT
    CMARK_OPT_SOURCEPOS = _lib.CMARK_OPT_SOURCEPOS
    CMARK_OPT_HARDBREAKS = _lib.CMARK_OPT_HARDBREAKS
    CMARK_OPT_SAFE = _lib.CMARK_OPT_SAFE
    CMARK_OPT_UNSAFE = _lib.CMARK_OPT_UNSAFE
    CMARK_OPT_NOBREAKS = _lib.CMARK_OPT_NOBREAKS
    CMARK_OPT_NORMALIZE = _lib.CMARK_OPT_NORMALIZE
    CMARK_OPT_VALIDATE_UTF8 = _lib.CMARK_OPT_VALIDATE_UTF8
    CMARK_OPT_SMART = _lib.CMARK_OPT_SMART
    CMARK_OPT_NO_EXTENSIONS = _lib.CMARK_OPT_NO_EXTENSIONS
    CMARK_OPT_HTML_AS_TEXT = _lib.CMARK_OPT_HTML_AS_TEXT
    CMARK_OPT_LINKIFY = _lib.CMARK_OPT_LINKIFY
    CMARK_OPT_SUBSCRIPT = _lib.CMARK_OPT_SUBSCRIPT
    CMARK_OPT_SUPERSCRIPT = _lib.CMARK_OPT_SUPERSCRIPT
    CMARK_OPT_TASKLISTS = _lib.CMARK_OPT_TASKLISTS
    CMARK_OPT_ALERTS = _lib.CMARK_OPT_ALERTS
    CMARK_OPT_TOC = _lib.CMARK_OPT_TOC
    CMARK_OPT_MATH_RAW = _lib.CMARK_OPT_MATH_RAW
    CMARK_OPT_VIEWER_COMPAT = _lib.CMARK_OPT_VIEWER_COMPAT
    CMARK_OPT_SOURCE_SYNTAX = _lib.CMARK_OPT_SOURCE_SYNTAX
    CMARK_OPT_VIEWER = _lib.CMARK_OPT_VIEWER

    # Positions plus exact syntax spans: what a highlighter needs.
    CMARK_OPT_HIGHLIGHT = CMARK_OPT_SOURCEPOS | CMARK_OPT_SOURCE_SYNTAX


class Node:
    """A node in a cmark tree.

    Nodes obtained from :meth:`children`/:meth:`walk` are *views*: they borrow
    the :class:`Document` (which keeps it alive) and never free it themselves.
    """

    __slots__ = ("_ptr", "_doc")

    def __init__(self, ptr, document: "Optional[Document]" = None):
        self._ptr = ptr
        self._doc = document

    # -- identity -----------------------------------------------------------
    def __bool__(self) -> bool:
        return self._ptr != _ffi.NULL

    def __repr__(self) -> str:
        return "<Node {} {}:{}-{}:{}>".format(
            self.type_name, self.start_line, self.start_column,
            self.end_line, self.end_column)

    @property
    def ptr(self):
        return self._ptr

    @property
    def type(self) -> int:
        return int(_lib.cmark_node_get_type(self._ptr))

    @property
    def type_name(self) -> str:
        return _decode(_lib.cmark_node_get_type_string(self._ptr))

    # -- positions (1-based; columns are UTF-8 byte offsets) ----------------
    @property
    def start_line(self) -> int:
        return int(_lib.cmark_node_get_start_line(self._ptr))

    @property
    def start_column(self) -> int:
        return int(_lib.cmark_node_get_start_column(self._ptr))

    @property
    def end_line(self) -> int:
        return int(_lib.cmark_node_get_end_line(self._ptr))

    @property
    def end_column(self) -> int:
        return int(_lib.cmark_node_get_end_column(self._ptr))

    @property
    def content_start_line(self) -> int:
        return int(_lib.cmark_node_get_content_start_line(self._ptr))

    # -- payload ------------------------------------------------------------
    @property
    def literal(self) -> str:
        return _decode(_lib.cmark_node_get_literal(self._ptr))

    @property
    def url(self) -> str:
        return _decode(_lib.cmark_node_get_url(self._ptr))

    @property
    def title(self) -> str:
        return _decode(_lib.cmark_node_get_title(self._ptr))

    @property
    def heading_level(self) -> int:
        return int(_lib.cmark_node_get_heading_level(self._ptr))

    @property
    def fence_info(self) -> str:
        return _decode(_lib.cmark_node_get_fence_info(self._ptr))

    @property
    def list_type(self) -> int:
        return int(_lib.cmark_node_get_list_type(self._ptr))

    @property
    def list_start(self) -> int:
        return int(_lib.cmark_node_get_list_start(self._ptr))

    @property
    def list_tight(self) -> bool:
        return bool(_lib.cmark_node_get_list_tight(self._ptr))

    @property
    def task_checked(self) -> int:
        """-1 when the item is not a task, else 0/1."""
        return int(_lib.cmark_node_get_task_checked(self._ptr))

    @property
    def alert_type(self) -> str:
        return _decode(_lib.cmark_node_get_alert_type(self._ptr))

    @property
    def formula_label(self) -> str:
        return _decode(_lib.cmark_node_get_formula_label(self._ptr))

    @property
    def formula_display(self) -> bool:
        return bool(_lib.cmark_node_get_formula_display(self._ptr))

    @property
    def image_width(self) -> int:
        return int(_lib.cmark_node_get_image_width(self._ptr))

    @property
    def image_height(self) -> int:
        return int(_lib.cmark_node_get_image_height(self._ptr))

    # -- VNote source syntax ------------------------------------------------
    @property
    def syntax_extent(self) -> Optional[tuple]:
        """``(start_line, start_column, end_line, end_column)`` or ``None``."""
        start_line, start_col = _ffi.new("int *"), _ffi.new("int *")
        end_line, end_col = _ffi.new("int *"), _ffi.new("int *")
        found = _lib.cmark_node_get_syntax_extent(
            self._ptr, start_line, start_col, end_line, end_col)
        if not found:
            return None
        return (start_line[0], start_col[0], end_line[0], end_col[0])

    def syntax_spans(self) -> List[dict]:
        """Delimiter spans: ``{"line", "column", "length", "text"}`` dicts."""
        count = int(_lib.cmark_node_get_syntax_span_count(self._ptr))
        spans: List[dict] = []
        for index in range(max(0, count)):
            line, column, length = _ffi.new("int *"), _ffi.new("int *"), _ffi.new("int *")
            raw = _lib.cmark_node_get_syntax_span(
                self._ptr, index, line, column, length)
            text = "" if raw == _ffi.NULL else _ffi.string(
                raw, length[0]).decode("utf-8", "replace")
            spans.append({
                "line": int(line[0]),
                "column": int(column[0]),
                "length": int(length[0]),
                "text": text,
            })
        return spans

    # -- traversal ----------------------------------------------------------
    def children(self) -> Iterator["Node"]:
        child = _lib.cmark_node_first_child(self._ptr)
        while child != _ffi.NULL:
            yield Node(child, self._doc)
            child = _lib.cmark_node_next(child)

    def walk(self) -> Iterator["Node"]:
        """Pre-order traversal, including this node."""
        yield self
        for child in self.children():
            yield from child.walk()


class Document(Node):
    """Owns a parsed tree and frees it on :meth:`close` or collection."""

    __slots__ = ("_closed",)

    def __init__(self, ptr):
        super().__init__(ptr, None)
        self._closed = False

    def close(self) -> None:
        if not self._closed and self._ptr != _ffi.NULL:
            _lib.cmark_node_free(self._ptr)
            self._ptr = _ffi.NULL
            self._closed = True

    def __enter__(self) -> "Document":
        return self

    def __exit__(self, *_exc) -> None:
        self.close()

    def __del__(self):
        try:
            self.close()
        except Exception:  # pragma: no cover - interpreter shutdown
            pass


# ---------------------------------------------------------------------------
# Parsing and rendering
# ---------------------------------------------------------------------------

def parse_document(text: str, options: int = 0) -> Document:
    """Parse ``text`` and return the tree's root as a :class:`Document`."""
    encoded = text.encode("utf-8")
    ptr = _lib.cmark_parse_document(encoded, len(encoded), options)
    if ptr == _ffi.NULL:
        raise ValueError("cmark could not parse the document")
    return Document(ptr)


def _ptr_of(node: Union[Node, object]):
    return node.ptr if isinstance(node, Node) else node


def render_html(node: Union[Node, object], options: int = 0) -> str:
    out = _lib.cmark_render_html(_ptr_of(node), options)
    if out == _ffi.NULL:
        return ""
    try:
        return _ffi.string(out).decode("utf-8", "replace")
    finally:
        _release(out)


def render_xml(node: Union[Node, object], options: int = 0) -> str:
    out = _lib.cmark_render_xml(_ptr_of(node), options)
    if out == _ffi.NULL:
        return ""
    try:
        return _ffi.string(out).decode("utf-8", "replace")
    finally:
        _release(out)


def markdown_to_html(text: str, options: int = 0) -> str:
    """Render ``text`` to HTML with the default (all) extensions."""
    doc = parse_document(text, options)
    try:
        return render_html(doc, options)
    finally:
        doc.close()


def markdown_to_html_with_extensions(text: str, options: int = 0,
                                     extensions=None) -> str:
    """Compatibility wrapper.

    vnotex/cmark bakes the GitHub extensions into the core, so ``extensions``
    is accepted for API compatibility but has no effect.
    """
    return markdown_to_html(text, options)


def github_flavored_markdown_to_html(text: str, options: int = 0) -> str:
    """GitHub-flavored rendering (the default behaviour of this parser)."""
    return markdown_to_html(text, options)


# ---------------------------------------------------------------------------
# Streaming parser
# ---------------------------------------------------------------------------

def parser_new(options: int = 0):
    return _lib.cmark_parser_new(options)


def parser_free(parser) -> None:
    _lib.cmark_parser_free(parser)


def parser_feed(parser, text: str) -> None:
    encoded = text.encode("utf-8")
    _lib.cmark_parser_feed(parser, encoded, len(encoded))


def parser_finish(parser) -> Document:
    ptr = _lib.cmark_parser_finish(parser)
    if ptr == _ffi.NULL:
        raise ValueError("cmark could not finish the document")
    return Document(ptr)
