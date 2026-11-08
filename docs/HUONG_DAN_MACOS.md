# Hướng dẫn A–Z trên MacBook (macOS 12 trở lên, chip Intel hoặc Apple M1/M2/M3/M4)

Thời gian cài lần đầu: khoảng 20–40 phút (phần lớn là tải Homebrew + model ~1,9 GB).
Mọi lệnh gõ trong **Terminal** (⌘ + Space → gõ *Terminal* → Enter).

> Trên Mac, CapCut lưu dự án và bộ nhớ đệm ở chỗ khác Windows, nên **không dùng lại được đường dẫn trong `examples/plan_1107.json`**. Bước B4 sẽ lấy đường dẫn đúng cho máy Mac.

---

## Phần A — Cài đặt (làm 1 lần)

### A1. Cài công cụ dòng lệnh của Apple

```bash
xcode-select --install
```

Bấm *Install* trong hộp thoại. Nếu báo “already installed” thì bỏ qua.

### A2. Cài Homebrew (trình cài phần mềm)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Nhập mật khẩu máy khi được hỏi. **Cuối quá trình, Homebrew in ra 2–3 lệnh “Next steps”** — chạy đúng các lệnh đó. Với Mac chip Apple thường là:

```bash
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```

Kiểm tra: `brew --version`.

### A3. Cài Python và ffmpeg

```bash
brew install python@3.12 ffmpeg
```

Kiểm tra:

```bash
python3 --version     # 3.12.x
ffmpeg -version
```

> Nếu `python3 --version` vẫn ra 3.9 (bản của Apple), dùng `python3.12` thay cho `python3` ở bước A5.

### A4. Chép công cụ sang Mac

Chép nguyên thư mục `capcut-editor-tool` (qua USB, Google Drive, AirDrop…) vào, ví dụ, `~/Desktop/capcut-editor-tool`.

```bash
cd ~/Desktop/capcut-editor-tool
```

> Không cần chép `.venv` và `models` từ máy Windows — sẽ tạo lại trên Mac.

### A5. Cài thư viện + tải model

```bash
chmod +x setup.sh
./setup.sh
```

Chờ đến dòng `Cài đặt xong`. Kết quả: có `.venv/` và `models/sherpa-onnx-whisper-medium/`.

Làm tay (nếu `setup.sh` lỗi):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m capcut_tool.download_model medium
```

### A6. Cấp quyền truy cập ổ đĩa cho Terminal

CapCut trên Mac (bản App Store) lưu dữ liệu trong `~/Library/Containers/...`, macOS chặn Terminal đọc chỗ này nếu chưa cấp quyền:

 > **System Settings → Privacy & Security → Full Disk Access** → bật **Terminal** (bấm `+` nếu chưa có) → thoát Terminal (⌘Q) và mở lại.

Lần đầu đọc ổ ngoài/Desktop/Downloads, macOS có thể hỏi quyền — chọn **Allow**.

### A7. (Tuỳ chọn) Font Montserrat cho video xem trước

<https://fonts.google.com/specimen/Montserrat> → *Get font* → *Download all* → giải nén → nhấp đúp các file `.ttf` → **Install Font**.

### A8. Chuẩn bị CapCut (làm 1 lần)

Mở CapCut, trong một dự án bất kỳ hãy **dùng thử một lần**: phụ đề font **Montserrat**, hiệu ứng chú thích **Color and zoom** (*Phóng to và tô màu*), các hiệu ứng âm thanh muốn dùng. Lưu, rồi **thoát CapCut (⌘Q)**.

---

## Phần B — Dựng một video (mỗi lần làm)

### B0. Mở môi trường

```bash
cd ~/Desktop/capcut-editor-tool
source run.sh
```

### B1. Tìm thư mục dự án CapCut trên Mac

Cách chắc chắn nhất: CapCut → **Settings (Cài đặt) → Draft / Vị trí bản nháp** — xem đường dẫn hiển thị.
Hoặc tìm bằng lệnh:

```bash
find ~ -type d -name "com.lveditor.draft" 2>/dev/null
```

Hay gặp:
- bản tải từ capcut.com: `~/Movies/CapCut/User Data/Projects/com.lveditor.draft`
- bản App Store: `~/Library/Containers/com.lemon.lvoverseas/Data/Movies/CapCut/User Data/Projects/com.lveditor.draft`

Gán biến (thay bằng đường dẫn bạn tìm được, và tên dự án):

```bash
export DRAFTS="$HOME/Movies/CapCut/User Data/Projects/com.lveditor.draft"
export PROJ="$DRAFTS/1107"
ls "$PROJ"        # phải thấy draft_content.json
```

### B2. Tạo dự án trong CapCut

1. CapCut → tạo dự án khung **9:16**.
2. **Import** voice và các clip vào thư viện media.
3. Đặt tên dự án → **thoát CapCut (⌘Q)**.

> Clip trên ổ ngoài có đường dẫn dạng `/Volumes/TÊN_Ổ/DCIM/...`.

### B3. Chép lời voice → phụ đề

```bash
python -m capcut_tool.transcribe ~/Downloads/voice.mp3 -o work/transcript.json
open -e work/transcript.json
```

Sửa chính tả trong `"text"`, thêm ` | ` để ngắt dòng phụ đề. Lưu (⌘S).

### B4. Lấy đường dẫn font / hiệu ứng / âm thanh trên Mac

```bash
python -m capcut_tool.find_resources "$DRAFTS" --check
```

Ghi lại 3 khối in ra: **FONT**, **HIỆU ỨNG CHỮ** (dòng `Phóng to và tô màu`), **HIỆU ỨNG ÂM THANH**.
Nếu khối nào trống → làm lại A8.

### B5. Xem nội dung clip

```bash
python -m capcut_tool.contact_sheet --draft "$PROJ" -o work/sheets
open work/sheets
```

### B6. Viết kế hoạch

```bash
mkdir -p work
cp examples/plan_1107.json work/plan.json
open -e work/plan.json
```

Sửa **toàn bộ đường dẫn sang kiểu Mac**:

| Trường | Ví dụ trên Mac |
|---|---|
| `draft_dir` | `/Users/ten_ban/Movies/CapCut/User Data/Projects/com.lveditor.draft/1107` |
| `transcript` | `work/transcript.json` |
| `voice.path` | `/Users/ten_ban/Downloads/voice.mp3` |
| `captions.font` | dán khối FONT ở B4 |
| `captions.animation` | dán khối HIỆU ỨNG CHỮ ở B4 (`id`, `name`, `path`) |
| `video.clips[].file` | `/Volumes/DJI/DCIM/DJI_002/DJI_..._D.MP4` |
| `sfx.library` | dán khối HIỆU ỨNG ÂM THANH ở B4, đặt tên ngắn (whoosh, pop…) và thêm `"offset_frames": -6` cho whoosh |

> Mẹo: kéo file từ Finder thả vào cửa sổ Terminal để lấy đúng đường dẫn.
> Chi tiết các trường: [PLAN_FORMAT.md](PLAN_FORMAT.md).

### B7. Chạy thử & xem trước

```bash
python -m capcut_tool.build work/plan.json --dry-run
python -m capcut_tool.preview work/draft_content.json -o work/preview.mp4
open work/preview.mp4
```

### B8. Ghi vào dự án

**CapCut phải đã thoát hẳn (⌘Q).**

```bash
python -m capcut_tool.build work/plan.json
```

Mở CapCut → mở dự án → kiểm tra → xuất video.

### B9. Hoàn tác (nếu cần)

```bash
python -m capcut_tool.restore "$PROJ/_backup_capcut_tool_20261108_170000"
```

---

## Lỗi thường gặp (macOS)

| Hiện tượng | Cách xử lý |
|---|---|
| `command not found: brew` | Chạy các lệnh “Next steps” Homebrew in ra (A2), mở Terminal mới. |
| `command not found: python` | Dùng `python3`, hoặc `source run.sh` trước (trong venv có sẵn `python`). |
| `Operation not permitted` khi đọc thư mục CapCut | Cấp **Full Disk Access** cho Terminal (A6), thoát và mở lại Terminal. |
| `pip install` báo lỗi biên dịch | `brew install python@3.12`, xoá thư mục `.venv`, chạy lại `./setup.sh`. |
| `zsh: permission denied: ./setup.sh` | `chmod +x setup.sh` |
| `Không tìm thấy media` | Ổ ngoài phải đang cắm; đường dẫn phải là `/Volumes/...`, không phải `F:/...`. |
| Phụ đề/âm thanh trống trong CapCut | Đường dẫn font/hiệu ứng còn kiểu Windows → làm lại B4 và B6. |
| Mở CapCut vẫn thấy dự án cũ | CapCut chưa thoát hẳn khi build → ⌘Q, chạy lại B8. |
| `Không đọc được ... dạng JSON` | Phiên bản CapCut mã hoá dự án — công cụ không hỗ trợ bản đó. |
| Transcribe chậm | Dùng model nhỏ: `python -m capcut_tool.download_model small` rồi thêm `--model models/sherpa-onnx-whisper-small`. |
