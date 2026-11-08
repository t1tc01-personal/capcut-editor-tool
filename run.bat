@echo off
chcp 65001 >nul
cd /d "%~dp0"
call .venv\Scripts\activate.bat
echo Moi truong da san sang. Vi du lenh:
echo   python -m capcut_tool.transcribe "C:\Users\PC\Downloads\voice.mp3" -o work\transcript.json
echo   python -m capcut_tool.contact_sheet --draft "%LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft\1107" -o work\sheets
echo   python -m capcut_tool.build examples\plan_1107.json --dry-run
echo   python -m capcut_tool.preview work\draft_content.json -o work\preview.mp4
echo   python -m capcut_tool.build examples\plan_1107.json
echo.
cmd /k
