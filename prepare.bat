@echo off
chcp 65001 >nul
cd /d "%~dp0"
set PROJ=%~1
if "%PROJ%"=="" set /p PROJ=Nhap ten du an CapCut (vd. 1109):
call .venv\Scripts\activate.bat
python -m capcut_tool.prepare "%PROJ%"
pause
