#!/usr/bin/env bash
# Dùng: ./prepare.sh 1109
cd "$(dirname "$0")"
source .venv/bin/activate
export PYTHONIOENCODING=utf-8
PROJ="${1:-}"
[ -z "$PROJ" ] && read -rp "Tên dự án CapCut (vd. 1109): " PROJ
python -m capcut_tool.prepare "$PROJ"
