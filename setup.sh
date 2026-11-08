#!/usr/bin/env bash
# CapCut Editor Tool – cài đặt cho macOS (và Linux)
set -e
cd "$(dirname "$0")"
echo "=== CapCut Editor Tool - cài đặt ==="

command -v python3 >/dev/null || { echo "[LỖI] Chưa có python3. Chạy: brew install python@3.12"; exit 1; }
command -v ffmpeg  >/dev/null || { echo "[LỖI] Chưa có ffmpeg. Chạy: brew install ffmpeg"; exit 1; }

PYV=$(python3 -c 'import sys;print("%d%02d"%sys.version_info[:2])')
if [ "$PYV" -lt 310 ]; then
  echo "[CẢNH BÁO] Python $(python3 -V) cũ. Nên dùng 3.10+: brew install python@3.12"
fi

[ -d .venv ] || python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m capcut_tool.download_model "${1:-medium}"

echo
echo "=== Cài đặt xong. Mỗi lần dùng: source run.sh (hoặc: source .venv/bin/activate) ==="
