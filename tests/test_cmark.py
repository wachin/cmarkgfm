from __future__ import unicode_literals

import textwrap

from cmarkgfm import cmark
from cmarkgfm.cmark import Options


def _normalize_ws(html):
    return textwrap.dedent(html.strip("\n")).strip("\n")


# ---------------------------------------------------------------------------
# Rendering (upstream API, adapted to vnotex/cmark)
# ---------------------------------------------------------------------------

def test_binding_is_the_vnote_parser():
    # The system package ships 0.29.0.gfm.*; this must be vnotex/cmark.
    assert cmark.CMARK_VERSION == "0.31.2"


def test_markdown_to_html():
    text = u"Hello, **world**!"
    result = cmark.markdown_to_html(text)
    assert result == '<p>Hello, <strong>world</strong>!</p>\n'


def test_markdown_to_html_with_extensions_is_compatible():
    # vnotex/cmark bakes the extensions in, so the argument is ignored.
    text = u"Hello, https://pypa.io!"
    result = cmark.markdown_to_html_with_extensions(
        text, options=Options.CMARK_OPT_LINKIFY, extensions=['autolink'])
    expected = """
        <p>Hello, <a href="https://pypa.io">https://pypa.io</a>!</p>
    """
    assert _normalize_ws(result) == _normalize_ws(expected)


def test_github_flavored_markdown_to_html():
    text = u"Hello, https://pypa.io!"
    result = cmark.github_flavored_markdown_to_html(
        text, options=Options.CMARK_OPT_LINKIFY)
    expected = """
        <p>Hello, <a href="https://pypa.io">https://pypa.io</a>!</p>
    """
    assert _normalize_ws(result) == _normalize_ws(expected)


def test_github_flavored_markdown_to_html_pre_tag():
    text = u"```python\nprint('hello')\n```"
    result = cmark.github_flavored_markdown_to_html(text)
    expected = """
        <pre><code class="language-python">print('hello')
        </code></pre>
    """
    assert _normalize_ws(result) == _normalize_ws(expected)


def test_github_flavored_markdown_to_html_tasklist():
    text = u"- [X] Task 1 Done\n- [ ] Task 2 Incomplete"
    result = cmark.github_flavored_markdown_to_html(
        text, options=Options.CMARK_OPT_TASKLISTS)
    assert 'type="checkbox"' in result
    assert 'checked=""' in result


# ---------------------------------------------------------------------------
# Tree API
# ---------------------------------------------------------------------------

def test_parse_document_returns_a_tree():
    doc = cmark.parse_document(u"Hello, **world**!")
    try:
        assert doc.type_name == "document"
        assert [n.type_name for n in doc.children()] == ["paragraph"]
    finally:
        doc.close()


def test_render_html_accepts_a_node():
    doc = cmark.parse_document(u"Hello, **world**!")
    try:
        assert cmark.render_html(doc) == '<p>Hello, <strong>world</strong>!</p>\n'
    finally:
        doc.close()


def test_parser_interface():
    parser = cmark.parser_new()
    try:
        cmark.parser_feed(parser, u"Hello, **world**!")
        doc = cmark.parser_finish(parser)
        assert cmark.render_html(doc) == '<p>Hello, <strong>world</strong>!</p>\n'
        doc.close()
    finally:
        cmark.parser_free(parser)


def test_document_close_is_idempotent():
    doc = cmark.parse_document(u"x")
    doc.close()
    doc.close()
    with cmark.parse_document(u"x") as ctx_doc:
        assert ctx_doc.type_name == "document"


# ---------------------------------------------------------------------------
# Positions and VNote source-syntax metadata
# ---------------------------------------------------------------------------

SOURCE = u"a **bold** and `code` here\n"


def _walk(source=SOURCE, options=Options.CMARK_OPT_HIGHLIGHT):
    doc = cmark.parse_document(source, options)
    return doc


def test_node_positions_are_one_based():
    doc = _walk()
    try:
        strong = next(n for n in doc.walk() if n.type_name == "strong")
        assert (strong.start_line, strong.start_column,
                strong.end_line, strong.end_column) == (1, 3, 1, 10)
        bold = next(n for n in doc.walk()
                    if n.type_name == "text" and n.literal == "bold")
        assert (bold.start_line, bold.start_column,
                bold.end_line, bold.end_column) == (1, 5, 1, 8)
    finally:
        doc.close()


def test_syntax_extent_and_delimiter_spans():
    doc = _walk()
    try:
        strong = next(n for n in doc.walk() if n.type_name == "strong")
        # Extent end is exclusive, spans are the `**` delimiters themselves.
        assert strong.syntax_extent == (1, 3, 1, 11)
        spans = strong.syntax_spans()
        assert [s["text"] for s in spans] == ["**", "**"]
        assert [s["column"] for s in spans] == [3, 9]
        assert all(s["length"] == 2 for s in spans)

        code = next(n for n in doc.walk() if n.type_name == "code")
        assert code.literal == "code"
        assert code.syntax_extent == (1, 16, 1, 22)
        assert [s["text"] for s in code.syntax_spans()] == ["`", "`"]
    finally:
        doc.close()


def test_syntax_metadata_requires_the_option():
    doc = cmark.parse_document(SOURCE)  # no CMARK_OPT_SOURCE_SYNTAX
    try:
        strong = next(n for n in doc.walk() if n.type_name == "strong")
        assert strong.syntax_extent is None
        assert strong.syntax_spans() == []
    finally:
        doc.close()


def test_vnote_node_types():
    source = (
        "---\ntitle: x\n---\n\n"
        "~~gone~~ $a+b$\n\n"
        "| a | b |\n|---|---|\n| 1 | 2 |\n"
    )
    doc = _walk(source)
    try:
        names = [n.type_name for n in doc.walk()]
        for expected in ("frontmatter", "strikethrough", "formula_inline",
                         "table", "table_row", "table_cell"):
            assert expected in names, expected
    finally:
        doc.close()


def test_render_xml_carries_sourcepos():
    doc = _walk()
    try:
        xml = cmark.render_xml(doc, Options.CMARK_OPT_SOURCEPOS)
        assert "<document" in xml
        assert 'sourcepos="1:1-' in xml
        assert "<strong" in xml
    finally:
        doc.close()
