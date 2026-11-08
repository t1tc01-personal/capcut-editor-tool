@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo === CapCut Editor Tool - cai dat ===

where python >nul 2>nul || (echo [LOI] Chua cai Python. Xem docs\INSTALL.md & pause & exit /b 1)
where ffmpeg >nul 2>nul || (echo [LOI] Chua cai ffmpeg. Chay: winget install Gyan.FFmpeg  roi mo lai cua so. & pause & exit /b 1)

if not exist .venv (
  python -m venv .venv || (echo [LOI] Khong tao duoc venv & pause & exit /b 1)
)
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt || (echo [LOI] pip install that bai & pause & exit /b 1)

python -m capcut_tool.download_model medium

echo.
echo === Cai dat xong. Mo run.bat hoac xem README.md ===
pause
