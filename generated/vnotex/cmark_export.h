#ifndef CMARK_EXPORT_H
#define CMARK_EXPORT_H

/* Static build: cmark is compiled into the extension, so no visibility
 * attributes are required. Mirrors what CMake's generate_export_header()
 * produces for a static library with CMARK_STATIC_DEFINE. */

#define CMARK_EXPORT
#define CMARK_NO_EXPORT
#define CMARK_DEPRECATED
#define CMARK_DEPRECATED_EXPORT
#define CMARK_DEPRECATED_NO_EXPORT

#endif /* CMARK_EXPORT_H */
