# Dùng:  source run.sh   (chạy trong Terminal, tại thư mục capcut-editor-tool)
cd "$(dirname "${BASH_SOURCE[0]:-$0}")"
source .venv/bin/activate
export PYTHONIOENCODING=utf-8
echo "Môi trường đã sẵn sàng. Ví dụ lệnh:"
echo '  python -m capcut_tool.transcribe ~/Downloads/voice.mp3 -o work/transcript.json'
echo '  python -m capcut_tool.find_resources "$DRAFTS"'
echo '  python -m capcut_tool.contact_sheet --draft "$DRAFTS/1107" -o work/sheets'
echo '  python -m capcut_tool.build work/plan.json --dry-run'
echo '  python -m capcut_tool.preview work/draft_content.json -o work/preview.mp4'
echo '  python -m capcut_tool.build work/plan.json'
