# Hướng dẫn A–Z trên Windows 10 / 11

Thời gian cài lần đầu: khoảng 15–30 phút (phần lớn là tải model ~1,9 GB).
Mọi lệnh gõ trong **Command Prompt** (cmd) trừ khi ghi khác.

---

## Phần A — Cài đặt (làm 1 lần)

### A1. Cài Python

1. Vào <https://www.python.org/downloads/windows/> → tải **Python 3.12** (Windows installer 64-bit).
2. Mở file cài đặt → **tích ô “Add python.exe to PATH”** ở màn hình đầu → *Install Now*.
3. Kiểm tra: mở **cmd mới** (phím Windows → gõ `cmd` → Enter):

   ```bat
   python --version
   ```

   Thấy `Python 3.12.x` là được.

> Cách khác (PowerShell): `winget install Python.Python.3.12`

### A2. Cài ffmpeg

Cách nhanh — mở **PowerShell**:

```powershell
winget install Gyan.FFmpeg
```

Đóng và mở lại cmd, kiểm tra:

```bat
ffmpeg -version
ffprobe -version
```

Không có winget:
1. Tải `ffmpeg-release-full.7z` tại <https://www.gyan.dev/ffmpeg/builds/>, giải nén vào `C:\ffmpeg` (sao cho có `C:\ffmpeg\bin\ffmpeg.exe`).
2. Phím Windows → gõ *environment* → **Edit the system environment variables** → *Environment Variables…* → chọn **Path** (ở User variables) → *Edit* → *New* → nhập `C:\ffmpeg\bin` → OK.
3. Mở cmd mới, chạy `ffmpeg -version`.

### A3. Chép công cụ

Thư mục công cụ: `C:\Users\PC\Desktop\capcut-editor-tool` (đã có sẵn). Nếu dùng máy khác, chép nguyên thư mục này sang.

### A4. Cài thư viện + tải model

Nhấp đúp **`setup.bat`** trong thư mục công cụ. Chờ đến dòng `Cai dat xong`.

Làm tay (nếu `setup.bat` lỗi):

```bat
cd %USERPROFILE%\Desktop\capcut-editor-tool
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m capcut_tool.download_model medium
```

Kết quả: có thư mục `.venv\` và `models\sherpa-onnx-whisper-medium\`.

### A5. (Tuỳ chọn) Cài font Montserrat cho video xem trước

<https://fonts.google.com/specimen/Montserrat> → *Get font* → *Download all* → giải nén → chọn các file `.ttf` → chuột phải → **Install**.

### A6. Chuẩn bị CapCut (làm 1 lần)

Mở CapCut, trong một dự án bất kỳ hãy **dùng thử một lần**:
- phụ đề với font **Montserrat**;
- hiệu ứng chú thích **Color and zoom** (*Phóng to và tô màu*);
- các hiệu ứng âm thanh muốn dùng (whoosh, pop, click…).

Việc này để CapCut tải chúng vào bộ nhớ đệm (`%LOCALAPPDATA%\CapCut\User Data\Cache`). Lưu lại rồi **đóng CapCut**.

---

## Phần B — Dựng một video (mỗi lần làm)

### B0. Mở môi trường

Nhấp đúp **`run.bat`** → hiện cửa sổ cmd đã sẵn sàng. Các lệnh dưới đều gõ trong cửa sổ này.

Đặt biến cho gọn (thay `1107` bằng tên dự án):

```bat
set DRAFTS=%LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft
set PROJ=%DRAFTS%\1107
```

### B1. Tạo dự án trong CapCut

1. CapCut → *Tạo dự án* → khung **9:16**.
2. **Import** voice (mp3) và các clip vào thư viện media (không cần kéo vào timeline).
3. Đặt tên dự án (vd. `1107`) → **đóng CapCut hoàn toàn** (kể cả biểu tượng dưới khay hệ thống).

### B2. Chép lời voice → phụ đề

```bat
python -m capcut_tool.transcribe "C:\Users\PC\Downloads\voice.mp3" -o work\transcript.json
```

Mở `work\transcript.json` bằng Notepad:
- sửa chính tả trong `"text"`;
- thêm ` | ` để ngắt dòng phụ đề, vd. `"Từ bỏ công việc marketing | lương 15 triệu"`.

### B3. Xem nội dung clip

```bat
python -m capcut_tool.contact_sheet --draft "%PROJ%" -o work\sheets
```

Mở thư mục `work\sheets`: mỗi ảnh = 6 khung hình của 1 clip (số thứ tự, tên, độ dài). Ghi chú clip nào hợp câu nào.

### B4. Lấy đường dẫn font / hiệu ứng / âm thanh

```bat
python -m capcut_tool.find_resources "%DRAFTS%" --check
```

In ra các khối JSON `font`, `animation`, `sfx.library` đang có trên máy — dán vào kế hoạch ở bước sau.

### B5. Viết kế hoạch

```bat
if not exist work mkdir work
copy examples\plan_1107.json work\plan.json
notepad work\plan.json
```

Sửa:
- `draft_dir` → đường dẫn dự án (dùng `/`), vd. `C:/Users/PC/AppData/Local/CapCut/User Data/Projects/com.lveditor.draft/1107`
- `transcript` → `work/transcript.json`
- `voice.path` → file voice
- `video.clips` → mỗi cảnh: `{"chunk": số_câu, "file": "đường_dẫn_clip", "src": giây_bắt_đầu}`
- `sfx.events` → hiệu ứng âm thanh (theo `cut`, `word`, `chunk` hoặc `at`)

Chi tiết từng trường: [PLAN_FORMAT.md](PLAN_FORMAT.md).

### B6. Chạy thử & xem trước

```bat
python -m capcut_tool.build work\plan.json --dry-run
python -m capcut_tool.preview work\draft_content.json -o work\preview.mp4
start work\preview.mp4
```

Chưa ưng → sửa `plan.json`/`transcript.json` → chạy lại B6.

### B7. Ghi vào dự án

**CapCut phải đang đóng.**

```bat
python -m capcut_tool.build work\plan.json
```

Màn hình in thư mục sao lưu `_backup_capcut_tool_...`. Mở CapCut → mở dự án → kiểm tra → xuất video.

### B8. Hoàn tác (nếu cần)

```bat
python -m capcut_tool.restore "%PROJ%\_backup_capcut_tool_20261108_170000"
```

---

## Lỗi thường gặp (Windows)

| Hiện tượng | Cách xử lý |
|---|---|
| `'python' is not recognized` | Cài lại Python, tích *Add to PATH*; hoặc dùng `py` thay `python`. |
| `'ffmpeg' is not recognized` | Làm lại A2, **mở cmd mới**. |
| Chữ tiếng Việt bị lỗi trong cmd | Chạy `chcp 65001` (run.bat đã làm sẵn). |
| `setup.bat` dừng ở pip | Kiểm tra mạng; chạy lại `setup.bat`. |
| Tải model lỗi giữa chừng | Xoá file `models\*.tar.bz2` rồi `python -m capcut_tool.download_model medium`. |
| `Không tìm thấy media` | Ổ ngoài (F:, D:) phải đang cắm, đường dẫn đúng chữ hoa/thường. |
| Mở CapCut vẫn thấy dự án cũ | CapCut đang chạy lúc build → tắt hẳn CapCut (cả khay hệ thống), chạy lại B7. |
| Phụ đề/âm thanh trống trong CapCut | Tài nguyên chưa có trong Cache → làm lại A6 rồi B4. |
| `Không đọc được ... dạng JSON` | Phiên bản CapCut mã hoá dự án — công cụ không hỗ trợ bản đó. |
