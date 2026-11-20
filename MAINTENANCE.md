# Maintaining this fork

This repository is marktux's fork of [`theacodes/cmarkgfm`](https://github.com/theacodes/cmarkgfm).
It contains two layers:

| Layer | Repository | Notes |
|---|---|---|
| Python binding + build | `github.com/wachin/cmarkgfm` (this repo) | small; we own it |
| C parser | `github.com/wachin/cmark` (submodule `third_party/cmark`) | our fork of `vnotex/cmark` |

## Upstreams we track

* `theacodes/cmarkgfm` — binding changes.
* `vnotex/cmark` — VNote's parser patches (source extents, math/mark/table nodes).
* `github/cmark-gfm` — the GitHub parser VNote itself forked.

## Reviewing upstream changes (never merge blindly)

```bash
./scripts/fetch-upstream.sh
git -C third_party/cmark log --oneline HEAD..upstream/master
git -C third_party/cmark diff HEAD..upstream/master -- src/ cmake/ data/
```

Review the diff and run the tests **before** moving the pin. Only then:

```bash
git -C third_party/cmark checkout <new-commit>
cd src && python3 cmarkgfm/build_cmark.py     # rebuild _cmark.abi3.so
cd .. && PYTHONPATH=src python3 -m pytest tests
```

Then commit the submodule pointer and mention the new commit in the message;
re-run marktux's suites afterwards.

## Building

```bash
cd src && python3 cmarkgfm/build_cmark.py     # in-place, for development
# or
pip install .
```

A C compiler and `cffi` are needed at **build** time; the resulting
`cmarkgfm/_cmark.abi3.so` is what Python imports at run time. CI builds wheels
(`cibuildwheel` and `pypi-publish.yml`), so end users do not need a compiler.

## Licenses

The binding is MIT. The parser is BSD-2-Clause (John MacFarlane; VNote fork).
Keep `LICENSE.txt` and `third_party/cmark/COPYING` intact.
