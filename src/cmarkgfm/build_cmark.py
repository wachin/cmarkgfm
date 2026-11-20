import glob
import os
import sys

# setuptools provides the ``distutils`` shim that cffi's build machinery still
# imports on Python 3.12+.
import setuptools  # noqa: F401
import distutils.ccompiler
import distutils.dist
import cffi


# The cmark sources live under libs/cmark (our fork of vnotex/cmark). VNote bakes
# the GitHub extensions plus math/mark/footnotes into the core, so there is no
# extensions/ directory to compile.
HERE = os.path.dirname(os.path.abspath(__file__))
PACKAGE_ROOT = os.path.abspath(os.path.join(HERE, '../../'))
SRC_DIR = os.path.join(PACKAGE_ROOT, 'libs/cmark/src')
# Generated headers that CMake would normally emit (cmark_export.h,
# cmark_version.h); vnotex/cmark checks in the generated scanner sources.
GENERATED_SRC_DIR = os.path.join(PACKAGE_ROOT, 'generated/vnotex')

CMARK_DEF_H_PATH = os.path.join(HERE, 'cmark.cffi.h')
CMARK_MODULE_H_PATH = os.path.join(HERE, 'cmark_module.h')

with open(CMARK_DEF_H_PATH, encoding='utf-8') as fh:
    CMARK_DEF_H = fh.read()

with open(CMARK_MODULE_H_PATH, encoding='utf-8') as fh:
    CMARK_MODULE_H = fh.read()


def _get_sources(dir, exclude=set()):
    sources = glob.iglob(os.path.join(dir, '*.c'))
    # Absolute paths keep the build independent of the working directory
    # (cffi resolves relative sources against the cwd).
    return sorted([
        os.path.abspath(path)
        for path in sources
        if os.path.basename(path) not in exclude
    ])


SOURCES = _get_sources(SRC_DIR, exclude={'main.c'})


def _compiler_type():
    """Compiler type, so the right flags/sources are chosen.

    On Windows with MSVC this is "msvc"; on macOS and Linux it is "unix".
    """
    dist = distutils.dist.Distribution()
    dist.parse_config_files()
    cmd = dist.get_command_obj('build')
    cmd.ensure_finalized()
    compiler = distutils.ccompiler.new_compiler(compiler=cmd.compiler)
    return compiler.compiler_type


COMPILER_TYPE = _compiler_type()
if COMPILER_TYPE in {'unix', 'mingw32'}:
    EXTRA_COMPILE_ARGS = ['-std=c99']
elif COMPILER_TYPE == 'msvc':
    EXTRA_COMPILE_ARGS = ['/TP']
else:
    raise AssertionError("unsupported compiler: %s" % COMPILER_TYPE)


ffibuilder = cffi.FFI()
ffibuilder.cdef(CMARK_DEF_H)
ffibuilder.set_source(
    'cmarkgfm._cmark',
    CMARK_MODULE_H,
    sources=SOURCES,
    include_dirs=[SRC_DIR, GENERATED_SRC_DIR],
    define_macros=[('CMARK_STATIC_DEFINE', '1')],
    extra_compile_args=EXTRA_COMPILE_ARGS,
)


if __name__ == "__main__":
    # In-place development build. cffi mirrors absolute source paths into the
    # build directory, so build in a temp dir and copy only the extension back.
    import shutil
    import tempfile

    build_dir = tempfile.mkdtemp(prefix="cmarkgfm-build-")
    try:
        output = ffibuilder.compile(tmpdir=build_dir, verbose=True)
        target = os.path.join(HERE, os.path.basename(output))
        shutil.copy2(output, target)
        print("built:", target)
    finally:
        shutil.rmtree(build_dir, ignore_errors=True)
