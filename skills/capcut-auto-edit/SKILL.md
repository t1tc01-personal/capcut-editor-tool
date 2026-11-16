---
name: capcut-auto-edit
description: Dựng tự động dự án CapCut PC (Windows hoặc macOS) bằng capcut-editor-tool, không mở CapCut - khớp cảnh với voice, phụ đề tự động vàng viền đen Montserrat + Color and zoom, SFX khớp khung hình. Dùng khi người dùng nhắn kiểu "dựng dự án 1109", "đồng bộ hình với voice, tạo phụ đề, thêm SFX cho dự án X".
---

# CapCut Auto Edit (capcut-editor-tool, mọi máy / mọi hệ điều hành)

Dùng khi người dùng muốn dựng/chỉnh một dự án CapCut chỉ bằng prompt. Công cụ ghi trực tiếp vào `draft_content.json`. **Không dùng computer use, không mở CapCut.**

Trong skill này:
- **Máy người dùng** = máy cài CapCut và capcut-editor-tool (Windows 10/11, hoặc macOS Intel / Apple Silicon). CapCut không có bản Linux, nên máy người dùng không bao giờ là Linux.
- **Môi trường của Claude** = nơi Claude chạy lệnh. Có thể chính là máy người dùng (Claude Code, shell từ xa) hoặc một sandbox trên cloud (thường là Linux).
- **Không bao giờ giả định** tên người dùng, ổ đĩa, thư mục hay hệ điều hành. Mọi đường dẫn đều phải dò ra (Bước 0) hoặc đọc từ `info.json`.

## QUY TẮC SỐ 1: KHÔNG TỰ CÀI ĐẶT GÌ

Phần nặng (chép lời bằng Whisper, ảnh clip) **luôn chạy trên máy người dùng**, bằng `prepare`, dùng môi trường đã cài (`.venv`, `models/sherpa-onnx-whisper-*`).
- **Không** tự chạy `setup.bat` / `setup.sh`, `pip install`, `download_model`, không tải model Whisper, không cài sherpa-onnx.
- **Không** stage file video/âm thanh (`.MP4`, `.MOV`, `.LRF`, `.mp3`…) lên cloud.
- Phần `build` chỉ cần Python 3.8+ thuần (thư viện chuẩn), chạy được ở bất kỳ đâu.
- Nếu máy người dùng **chưa cài** (không có `.venv` hoặc thư mục `models/`): dừng lại và hướng dẫn họ tự cài theo hệ điều hành (bảng dưới), rồi chờ họ báo xong.

## Bảng tra theo hệ điều hành của máy người dùng

| Mục | Windows | macOS |
|---|---|---|
| Thư mục dự án CapCut (`DRAFTS`) | `%LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft` | bản capcut.com: `~/Movies/CapCut/User Data/Projects/com.lveditor.draft`; bản App Store: `~/Library/Containers/com.lemon.lvoverseas/Data/Movies/CapCut/User Data/Projects/com.lveditor.draft` |
| Python trong môi trường | `.venv\Scripts\python.exe` | `.venv/bin/python` |
| Cài đặt (người dùng tự chạy) | nhấp đúp `setup.bat` | `bash setup.sh` |
| Chuẩn bị dự án | nhấp đúp `prepare.bat` rồi nhập tên, hoặc `prepare.bat <tên>` | `bash prepare.sh <tên>` |
| Mở môi trường để gõ lệnh | `run.bat` | `source run.sh` |
| Ổ ngoài (DJI…) | `F:\DCIM\...` (chữ ổ thay đổi) | `/Volumes/<TÊN_Ổ>/DCIM/...` |
| Kiểm tra CapCut đang chạy | `tasklist /FI "IMAGENAME eq CapCut.exe"` | `pgrep -ix capcut` |
| Thoát CapCut | đóng cửa sổ (kiểm tra cả khay hệ thống) | ⌘Q |
| Mở file/thư mục | `start "" "<đường dẫn>"` | `open "<đường dẫn>"` |

Nếu không thấy `com.lveditor.draft` ở các chỗ trên (người dùng đổi vị trí lưu trong CapCut → Cài đặt → Bản nháp), dò bằng
`python -c "import os;[print(r) for r,d,f in os.walk(os.path.expanduser('~')) if r.endswith('com.lveditor.draft')]"` hoặc hỏi người dùng, rồi truyền `--drafts-root "<đường dẫn>"` cho `prepare`.

## Thông số mặc định

| Mục | Giá trị |
|---|---|
| Thư mục công cụ (`TOOL`) | thư mục chứa `capcut_tool/` và `prepare.bat`/`prepare.sh` (xem Bước 0) |
| Thư mục dự án (`PROJ`) | `DRAFTS/<tên>`; sau khi `prepare` xong thì lấy **chính xác** từ `info.json` → `draft_dir` |
| Dữ liệu chuẩn bị | `TOOL/work/<tên>/` gồm `READY`, `info.json`, `transcript.json`, `resources.json`, `sheets/grid_*.jpg` |
| Kiểu phụ đề | Montserrat, chữ vàng `#f0ff00`, viền đen 0.06, cỡ 10, `position_y` -0.56, hiệu ứng **Phóng to và tô màu** (Color and zoom, id 7325378104753394178) |
| Mẫu kế hoạch | `TOOL/examples/plan_1107.json` (đường dẫn trong mẫu là của một máy Windows cụ thể – **chỉ lấy cấu trúc, không chép đường dẫn**) |

Chỉ hỏi lại khi thiếu **tên dự án** hoặc không tự dò được `TOOL`.

## Quy ước đường dẫn (quan trọng cho đa nền tảng)

- Đường dẫn media/font/hiệu ứng/SFX trong plan **phải là đường dẫn trên máy người dùng**, lấy nguyên văn từ `info.json` và `resources.json` (CapCut lưu bằng dấu `/`, vd. `C:/Users/.../a.mp4` hoặc `/Volumes/DJI/DCIM/a.MP4`). Không tự đổi dấu gạch, chữ hoa/thường hay ổ đĩa.
- Đường dẫn trong plan nên dùng `/` trên mọi hệ điều hành (Python trên Windows vẫn hiểu).
- Đường dẫn có dấu cách (`User Data`, `Application Support`) luôn phải đặt trong ngoặc kép khi gõ lệnh.
- `transcript` trong plan là đường dẫn **tương đối với thư mục đang chạy lệnh**, nên luôn chạy `build` từ `TOOL` (hoặc từ thư mục code đã chép lên cloud).
- Khi gọi công cụ file từ xa (`device_*`), dùng đường dẫn đầy đủ đúng kiểu của máy người dùng (Windows: `C:\...`; macOS: `/Users/...`).

## Bước 0: xác định cách chạy, hệ điều hành và `TOOL`

**0a. Chọn chế độ** (theo công cụ đang có):
- **Chế độ A – có shell trên máy người dùng**: Claude Code chạy trên máy đó (Bash/PowerShell), hoặc có tool shell từ xa như `mcp__remote-devices__device_bash`. Chạy mọi thứ trên máy người dùng.
- **Chế độ B – chỉ có công cụ file từ xa** (`device_list_dir` / `device_stage_files` / `device_commit_files`, thường gặp trong Cowork): Claude đọc file nhỏ, chạy `build` trên cloud, rồi ghi file về máy.
- **Chế độ C – không truy cập được máy người dùng**: hướng dẫn người dùng chạy `prepare`, gửi/tải lên các file nhỏ trong `work/<tên>/` cùng `draft_content.json`, `draft_meta_info.json`, `Timelines/project.json`; Claude dựng như chế độ B rồi trả file kèm hướng dẫn chép đè (đã sao lưu) – hoặc trả `plan.json` để người dùng tự chạy `build`.

Lưu ý: shell của Claude chạy trên cloud (sandbox Linux) **không** phải chế độ A.

**0b. Xác định hệ điều hành của máy người dùng**:
- Chế độ A: `python -c "import platform;print(platform.system(), platform.machine())"` (hoặc `python3`, `py`). Trên Windows, shell có thể là PowerShell, cmd hoặc Git Bash – viết lệnh đúng cú pháp của shell đang dùng.
- Chế độ B: nhìn dạng đường dẫn (`C:\...` → Windows; `/Users/...` → macOS) hoặc trường `draft_dir` trong `info.json`.

**0c. Tìm `TOOL`**, theo thứ tự:
1. Thư mục làm việc hiện tại (hoặc thư mục cha) nếu có `capcut_tool/` và `prepare.py` trong đó.
2. Đường dẫn người dùng đã nói trong hội thoại.
3. Vị trí hay gặp: `~/Desktop/capcut-editor-tool`, `~/Documents/capcut-editor-tool`, `~/Downloads/capcut-editor-tool` (Windows: `%USERPROFILE%\Desktop\...`, có thể nằm trong OneDrive: `%USERPROFILE%\OneDrive\Desktop\...`).
4. Không thấy thì hỏi người dùng.

Kiểm tra đã cài: có `.venv` (đúng file Python theo bảng) và `models/sherpa-onnx-whisper-medium` (hoặc `-small` nếu máy yếu; khi đó truyền `--model models/sherpa-onnx-whisper-small` cho `prepare`).

## Quy trình

Tạo task list, báo tiến độ ngắn bằng tiếng Việt.

### 1. Kiểm tra / chạy `prepare`
- Xem `TOOL/work/<tên>/`. Có file `READY` thì sang bước 2 (đọc `info.json` để lấy `draft_dir`, voice, clip).
- Chưa có `READY`:
  - **Chế độ A**: tự chạy trong `TOOL`, với Python của `.venv`:
    - Windows: `.venv\Scripts\python.exe -m capcut_tool.prepare <tên>` (PowerShell: `& ".venv\Scripts\python.exe" -m capcut_tool.prepare <tên>`)
    - macOS: `.venv/bin/python -m capcut_tool.prepare <tên>`

    Mất khoảng 3–10 phút tuỳ máy (máy yếu / không có GPU lâu hơn): chạy nền hoặc đặt timeout dài, không chạy lại khi đang chạy. Nên ghi log ra `work/prepare_<tên>.log`.
  - **Chế độ B/C**: **dừng lại và nhờ người dùng chạy trên máy họ** (dùng câu hướng dẫn đúng hệ điều hành):
    > Đóng CapCut. **Windows**: nhấp đúp `prepare.bat` trong thư mục `capcut-editor-tool` và nhập `<tên>`. **macOS**: mở Terminal, `cd` vào thư mục `capcut-editor-tool` rồi gõ `bash prepare.sh <tên>`. Chờ đến khi hiện chữ **XONG** rồi nhắn lại cho tôi.

    Khi người dùng báo xong, kiểm tra lại `READY`. Không tự chuyển sang cài đặt trên cloud.
- Nếu `prepare` báo lỗi: đọc thông báo rồi hướng dẫn xử lý, vd.
  - `Không thấy dự án` → sai tên, hoặc CapCut lưu nháp ở chỗ khác → dùng `--drafts-root`;
  - `chưa import voice` → import voice vào thư viện media của dự án;
  - `[thiếu file]` → ổ ngoài (thẻ nhớ DJI…) chưa cắm, hoặc chữ ổ / tên ổ khác lúc import;
  - `Không tìm thấy 'ffmpeg'` → người dùng cài ffmpeg (Windows: `winget install Gyan.FFmpeg`; macOS: `brew install ffmpeg`).

### 2. Đưa dữ liệu tới chỗ chạy `build`
- **Chế độ A**: không cần chép gì; đọc trực tiếp các file trong `work/<tên>/` và `PROJ`.
- **Chế độ B**: gom vào **một** lần `device_stage_files`:
  - `TOOL/work/<tên>/info.json`, `transcript.json`, `resources.json`, cùng mọi `sheets/grid_*.jpg` (tên lấy từ `info.json` → `grids`).
  - Code: `TOOL/capcut_tool/` gồm `__init__.py, common.py, draft.py, build.py, find_resources.py` và `templates/segments.json`.
  - Dự án: `PROJ/draft_content.json`, `draft_meta_info.json`, `key_value.json`, `Timelines/project.json`. Ghi lại `mtimeMs` của từng file.

  Chép code vào một thư mục trên cloud (vd. `~/cct/capcut_tool/...`) và dự án vào `~/cct/draft/<tên>/` với **đúng cấu trúc** (có `Timelines/project.json`).

### 3. Đọc và sửa lời thoại
- Đọc `transcript.json`, sửa chính tả, tên riêng và từ lóng (vd. "phô mô"→"FOMO", "cắt bà"→"Cát Bà"). Giữ nguyên `start` và `end`.
- Thêm ` | ` để ngắt dòng ở chỗ tự nhiên, khoảng 6–7 từ mỗi dòng. Bỏ dấu chấm cuối câu.
- Lưu bản đã sửa vào `work/<tên>/transcript.json` (chế độ A) hoặc thư mục làm việc trên cloud (chế độ B).

### 4. Chọn cảnh
- Đọc các ảnh `grid_*.jpg`. Mỗi hàng là một clip gồm 6 khung, khung thứ k nằm ở giây `thời lượng × (k+0.5)/6`. `info.json` → `clips` cho biết số thứ tự, đường dẫn, thời lượng và `available` của từng clip.
- Ghép cảnh theo nghĩa của lời thoại:
  - đi làm, văn phòng → cảnh văn phòng, máy tính;
  - du lịch, tự do → cảnh đường đi, biển, phong cảnh;
  - đoạn buồn → cảnh tối hoặc biểu cảm buồn;
  - câu mở đầu → cảnh đẹp nhất làm hook.
- Mỗi cảnh dài 1,5–5 giây; câu dài thì chia thành 2 cảnh. Hạn chế lặp clip. `src + thời lượng` không được vượt độ dài clip. Không dùng clip có `available: false`.

### 5. Viết `plan.json`
Lấy cấu trúc từ `examples/plan_1107.json` (xem `docs/PLAN_FORMAT.md`), **thay mọi đường dẫn** bằng giá trị của máy hiện tại:
- `draft_dir`: chế độ A → `info.json` → `draft_dir`; chế độ B → bản trên cloud `~/cct/draft/<tên>` (đổi lại ở bước 6).
- `transcript`: file transcript đã sửa (đường dẫn tương đối với thư mục chạy `build`, vd. `work/<tên>/transcript.json`).
- `voice.path`: lấy nguyên văn từ `info.json` → `voice.path`.
- `video`: `mute: true`. `clips` ưu tiên dạng `{"chunk": N, "file": "<đường dẫn nguyên văn trong info.json>", "src": s}`; dùng `at` khi chia một câu thành nhiều cảnh.
- `captions`: dùng thông số mặc định. Lấy `font` (Montserrat) và `animation` (dòng "Phóng to và tô màu") từ `resources.json` – **không** chép đường dẫn Cache trong file mẫu vì mỗi máy/hệ điều hành một khác.
- `sfx.library`: lấy từ `resources.json` → `sounds`. Đặt tên ngắn: whoosh (`offset_frames` -6, volume 0.55), pop 0.8, click, shutter, kiss.
- `sfx.events`: khoảng 3–5 giây một SFX.
  - whoosh tại các điểm chuyển chủ đề: `{"kind":"whoosh","cut":i}`.
  - pop tại con số, câu chốt, câu mở đầu và câu kết: `{"kind":"pop","word":"15","near":4.5}`.
  - click ở cảnh máy tính, shutter ở cảnh du lịch.
- `resources.json` thiếu font / hiệu ứng / SFX nào: nhờ người dùng dùng thử thứ đó một lần trong CapCut (để CapCut tải về Cache), lưu, đóng CapCut, rồi chạy lại `prepare <tên> --no-sheets` (hoặc chế độ A: tự chạy lại).
- Lưu plan vào `work/<tên>/plan.json`.

### 6. Dựng và ghi vào dự án
**Chế độ A** (trong `TOOL`, dùng Python của `.venv`, hoặc Python hệ thống bất kỳ vì `build` không cần thư viện ngoài):
1. `<python> -m capcut_tool.build work/<tên>/plan.json --dry-run --out work/<tên>/draft_content.json` → phải in đủ số cảnh, phụ đề, SFX, không lỗi. Lỗi thì sửa plan rồi chạy lại.
2. Kiểm tra CapCut đã tắt (lệnh trong bảng). Đang chạy thì nhờ người dùng thoát hẳn rồi mới ghi.
3. `<python> -m capcut_tool.build work/<tên>/plan.json --out work/<tên>/draft_content.json` → tự sao lưu vào `PROJ/_backup_capcut_tool_<thời gian>/` rồi ghi `draft_content.json` (cả bản trong `Timelines/<id>/`) và cập nhật `draft_meta_info.json`.
4. (Tuỳ chọn) xem trước: `<python> -m capcut_tool.preview work/<tên>/draft_content.json -o work/<tên>/preview.mp4`.

**Chế độ B**:
1. `cd ~/cct && python3 -m capcut_tool.build plan.json --dry-run --out <outputs>/<tên>/draft_content.json` (dùng `python` nếu không có `python3`). Kết quả phải in đủ số cảnh, phụ đề và SFX, không lỗi.
2. Đổi `draft_dir` trong plan về giá trị thật (`info.json` → `draft_dir`), lưu `plan.json` cùng `transcript.json` đã sửa vào outputs.
3. Gọi `device_commit_files` **một lần duy nhất**, dùng đường dẫn đúng kiểu của máy người dùng (`<id>` = `main_timeline_id` trong `Timelines/project.json`, `<stamp>` = `yyyymmdd_hhmmss`):
   1. sao lưu các bản gốc đã stage vào `PROJ/_backup_capcut_tool_<stamp>/` với tên `draft_content.json`, `Timelines__<id>__draft_content.json`, `draft_meta_info.json` (đúng định dạng để `capcut_tool.restore` khôi phục được trên mọi hệ điều hành);
   2. draft mới → `PROJ/draft_content.json` và `PROJ/Timelines/<id>/draft_content.json`, kèm `expectedMtimeMs`;
   3. `draft_meta_info.json` đã cập nhật `tm_duration` bằng `duration` của draft mới → `PROJ/draft_meta_info.json`, kèm `expectedMtimeMs`;
   4. `plan.json`, `transcript.json`, `draft_content.json` → `TOOL/work/<tên>/`, để người dùng có thể chạy lại hoặc xem trước trên máy.
4. Nếu `device_commit_files` báo mtime đổi, nghĩa là CapCut đang mở hoặc vừa lưu. Nhắc người dùng thoát CapCut, stage lại rồi ghi lại.

**Chế độ C**: trả `plan.json`, `transcript.json` đã sửa, và hướng dẫn người dùng (đã cài công cụ) chạy `build` như chế độ A bằng `run.bat` / `source run.sh`.

### 7. Báo cáo (ngắn, tiếng Việt)
- Số cảnh, số dòng phụ đề, số SFX.
- Cảnh được ghép theo từng đoạn lời ra sao, SFX đặt ở đâu.
- Bản sao lưu nằm ở đâu và cách khôi phục (trong `TOOL`, sau khi mở `run.bat` / `source run.sh`):
  `python -m capcut_tool.restore "<PROJ>/_backup_capcut_tool_<stamp>"`
- Muốn xem trước trên máy: `python -m capcut_tool.preview work/<tên>/draft_content.json -o work/<tên>/preview.mp4` (Windows có thể viết `work\<tên>\...`).
- Nhắc mở lại CapCut. Thời điểm từng chữ đổi màu (Color and zoom) chỉ là ước lượng; nếu lệch, dùng nút đồng bộ phụ đề của CapCut.
- Viết mọi lệnh hướng dẫn đúng cú pháp của hệ điều hành người dùng.

## Nguyên tắc
- Luôn sao lưu trước khi ghi. Không xoá và không di chuyển file của người dùng.
- Không viết JSON timeline bằng tay; để `build` lo việc căn khung hình và kiểm tra.
- Nếu `build` báo lỗi (thiếu media, `src` vượt độ dài clip, không tìm thấy từ cho SFX): sửa plan theo thông báo, không bỏ qua bước kiểm tra.
- Không đổi media đã import, không di chuyển clip gốc.
- Không đem đường dẫn của máy này (hoặc của file mẫu) sang máy khác; luôn lấy lại từ `info.json` / `resources.json` của chính dự án.
- Nếu draft bị mã hoá, hoặc phiên bản CapCut khác `new_version 187.x` mà mở bị lỗi: dừng và báo người dùng.
