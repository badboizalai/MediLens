#!/usr/bin/env bash
# Zip each skill into dist/skills/<name>.zip for upload to claude.ai / Skills API.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p dist/skills
for d in .claude/skills/medilens-*/; do
  n=$(basename "$d")
  (cd .claude/skills && zip -qr "../../dist/skills/$n.zip" "$n" -x '*/__pycache__/*')
  echo "packaged $n"
done
