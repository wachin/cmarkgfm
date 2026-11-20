/* cffi declarations for vnotex/cmark (VNote's cmark fork).
 *
 * The parser is compiled into the extension (see build_cmark.py) and vnotex
 * bakes GitHub's extensions plus VNote's math/mark/footnote/alerts support into
 * the core, so there is no extension-registration API here. On top of the
 * usual node getters this exposes VNote's source-syntax metadata
 * (cmark_node_get_syntax_extent / _syntax_span*), which is what syntax
 * highlighting and marker concealment need.
 */

typedef struct cmark_node cmark_node;
typedef struct cmark_parser cmark_parser;

const char *cmark_version_string(void);

/* Simple API */
char *cmark_markdown_to_html(const char *text, size_t len, int options);

/* Node tree */
cmark_node *cmark_parse_document(const char *buffer, size_t len, int options);
char *cmark_render_html(cmark_node *root, int options);
char *cmark_render_xml(cmark_node *root, int options);

int cmark_node_get_type(cmark_node *node);
const char *cmark_node_get_type_string(cmark_node *node);
cmark_node *cmark_node_first_child(cmark_node *node);
cmark_node *cmark_node_next(cmark_node *node);
void cmark_node_free(cmark_node *node);

/* Positions (1-based; columns are UTF-8 byte offsets) */
int cmark_node_get_start_line(cmark_node *node);
int cmark_node_get_start_column(cmark_node *node);
int cmark_node_get_end_line(cmark_node *node);
int cmark_node_get_end_column(cmark_node *node);
int cmark_node_get_content_start_line(cmark_node *node);

/* Node payload */
const char *cmark_node_get_literal(cmark_node *node);
const char *cmark_node_get_url(cmark_node *node);
const char *cmark_node_get_title(cmark_node *node);
int cmark_node_get_heading_level(cmark_node *node);
const char *cmark_node_get_fence_info(cmark_node *node);
int cmark_node_get_list_type(cmark_node *node);
int cmark_node_get_list_start(cmark_node *node);
int cmark_node_get_list_tight(cmark_node *node);
int cmark_node_get_task_checked(cmark_node *node);
const char *cmark_node_get_alert_type(cmark_node *node);
const char *cmark_node_get_formula_label(cmark_node *node);
int cmark_node_get_formula_display(cmark_node *node);
int cmark_node_get_image_width(cmark_node *node);
int cmark_node_get_image_height(cmark_node *node);

/* VNote source-syntax metadata (requires CMARK_OPT_SOURCE_SYNTAX) */
int cmark_node_get_syntax_extent(cmark_node *node, int *start_line,
                                 int *start_column, int *end_line,
                                 int *end_column);
int cmark_node_get_syntax_span_count(cmark_node *node);
const char *cmark_node_get_syntax_span(cmark_node *node, int index,
                                       int *line, int *column, int *length);

/* Streaming parser */
cmark_parser *cmark_parser_new(int options);
void cmark_parser_free(cmark_parser *parser);
void cmark_parser_feed(cmark_parser *parser, const char *buffer, size_t len);
cmark_node *cmark_parser_finish(cmark_parser *parser);

/* libc, to release strings rendered by cmark */
void free(void *ptr);

#define CMARK_OPT_DEFAULT ...
#define CMARK_OPT_SOURCEPOS ...
#define CMARK_OPT_HARDBREAKS ...
#define CMARK_OPT_SAFE ...
#define CMARK_OPT_UNSAFE ...
#define CMARK_OPT_NOBREAKS ...
#define CMARK_OPT_NORMALIZE ...
#define CMARK_OPT_VALIDATE_UTF8 ...
#define CMARK_OPT_SMART ...
#define CMARK_OPT_NO_EXTENSIONS ...
#define CMARK_OPT_HTML_AS_TEXT ...
#define CMARK_OPT_LINKIFY ...
#define CMARK_OPT_SUBSCRIPT ...
#define CMARK_OPT_SUPERSCRIPT ...
#define CMARK_OPT_TASKLISTS ...
#define CMARK_OPT_ALERTS ...
#define CMARK_OPT_TOC ...
#define CMARK_OPT_MATH_RAW ...
#define CMARK_OPT_VIEWER_COMPAT ...
#define CMARK_OPT_SOURCE_SYNTAX ...
#define CMARK_OPT_VIEWER ...
