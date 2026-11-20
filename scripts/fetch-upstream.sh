#!/usr/bin/env bash
# Fetch VNote's cmark changes for review. Never merges or checks anything out.
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cmark="$here/third_party/cmark"
upstream_url="https://github.com/vnotex/cmark"

if ! git -C "$cmark" remote get-url upstream >/dev/null 2>&1; then
    git -C "$cmark" remote add upstream "$upstream_url"
fi

git -C "$cmark" fetch upstream master

cat <<EOF
Upstream fetched. Review before merging:

  git -C $cmark log --oneline HEAD..upstream/master
  git -C $cmark diff HEAD..upstream/master -- src/ cmake/ data/

Then rebuild and run the tests (see MAINTENANCE.md).
EOF
