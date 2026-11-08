# Cài đặt (Windows 10/11)

## 1. Python 3.10 trở lên

- Tải tại <https://www.python.org/downloads/> → khi cài **tích "Add python.exe to PATH"**.
- Hoặc bằng winget (PowerShell):

  ```powershell
  winget install Python.Python.3.12
  ```

Kiểm tra: mở cửa sổ lệnh mới, gõ `python --version`.

## 2. ffmpeg (bắt buộc)

```powershell
winget install Gyan.FFmpeg
```

Đóng và mở lại cửa sổ lệnh, kiểm tra `ffmpeg -version` và `ffprobe -version`.
Không dùng winget được: tải bản "release full" tại <https://www.gyan.dev/ffmpeg/builds/>, giải nén vào `C:\ffmpeg` và thêm `C:\ffmpeg\bin` vào biến môi trường **Path**.

## 3. Cài công cụ

Nhấp đúp **`setup.bat`** trong thư mục `capcut-editor-tool`. Script sẽ:

1. tạo môi trường ảo `.venv`;
2. `pip install -r requirements.txt` (sherpa-onnx, soundfile, numpy);
3. tải model Whisper **medium** (~1.9 GB) vào `models\sherpa-onnx-whisper-medium` – chỉ làm một lần.

Làm thủ công (tương đương):

```bat
cd %USERPROFILE%\Desktop\capcut-editor-tool
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m capcut_tool.download_model medium
```

Máy yếu/ít dung lượng: `python -m capcut_tool.download_model small` rồi chạy transcribe với `--model models\sherpa-onnx-whisper-small` (nhanh hơn, sai chính tả nhiều hơn).

## 4. Mỗi lần sử dụng

Nhấp đúp **`run.bat`** (hoặc `.venv\Scripts\activate` trong thư mục công cụ) rồi chạy các lệnh trong README.

## 5. Font cho video xem trước (tuỳ chọn)

`preview.py` vẽ phụ đề bằng font cài trong Windows. Cài Montserrat từ <https://fonts.google.com/specimen/Montserrat> (Download family → chuột phải các file `.ttf` → Install). Nếu không cài, ffmpeg dùng font thay thế – chỉ ảnh hưởng bản xem trước, không ảnh hưởng dự án CapCut.

## 6. Vị trí thư mục quan trọng

| Gì | Đường dẫn |
|---|---|
| Dự án CapCut | `%LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft\<tên dự án>` |
| Hiệu ứng / font đã tải | `%LOCALAPPDATA%\CapCut\User Data\Cache\effect\<id>\<md5>` |
| Âm thanh SFX đã tải | `%LOCALAPPDATA%\CapCut\User Data\Cache\music\<md5>.mp3` |

Tìm đường dẫn của một hiệu ứng/SFX: trong CapCut dùng nó một lần trong dự án bất kỳ, lưu, rồi mở `draft_content.json` của dự án đó và tìm theo tên (vd. `"Phóng to và tô màu"`, `"whoosh"`) – lấy `path`, `effect_id`/`resource_id`, `duration`.

## Xử lý lỗi thường gặp

| Thông báo | Cách xử lý |
|---|---|
| `Không tìm thấy 'ffmpeg'` | Cài ffmpeg (mục 2), mở lại cửa sổ lệnh. |
| `Không đọc được ... draft_content.json dạng JSON` | Bản CapCut mã hoá draft – công cụ không hỗ trợ. |
| `Không tìm thấy media: ...` | Kiểm tra đường dẫn clip/voice trong plan; ổ đĩa ngoài (F:, D:) phải đang cắm. |
| `Cảnh #i: ... không đủ từ src=...` | Giảm `src` hoặc chọn clip dài hơn cho cảnh đó. |
| `SFX: không tìm thấy từ '...'` | Từ trong `word` phải xuất hiện trong phụ đề (sau khi sửa). |
| Mở CapCut thấy dự án như cũ | CapCut đang mở khi chạy build → đóng CapCut, chạy lại `build`. |
| Chữ/hiệu ứng/SFX bị trống trong CapCut | Tài nguyên chưa có trong Cache → dùng thử một lần trong CapCut, cập nhật đường dẫn trong plan. |
| Phụ đề sai chính tả | Sửa trong `work\transcript.json` (trường `text`) hoặc dùng `captions.replace` trong plan. |
