#!/usr/bin/env bash
set -euo pipefail

TAG="${1:-}"
if [[ -z "$TAG" ]]; then
  echo "Usage: $0 <tag>"
  exit 2
fi

git fetch origin master --tags >/dev/null 2>&1

if git rev-parse -q --verify "refs/tags/$TAG" >/dev/null; then
  echo "[FAIL] tag '$TAG' already exists"
  exit 1
fi

HEAD_SHA="$(git rev-parse HEAD)"
MASTER_SHA="$(git rev-parse origin/master)"

if [[ "$HEAD_SHA" != "$MASTER_SHA" ]]; then
  echo "[FAIL] HEAD ($HEAD_SHA) is not origin/master ($MASTER_SHA)"
  echo "       Please merge PR and fast-forward master first."
  exit 1
fi

echo "[OK] release guard passed on $HEAD_SHA"

