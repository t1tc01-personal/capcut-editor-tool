---
name: capcut-auto-edit
description: Dựng tự động dự án CapCut PC bằng capcut-editor-tool (không mở CapCut): khớp cảnh với voice, phụ đề tự động vàng viền đen Montserrat + Color and zoom, SFX khớp khung hình.
---

# CapCut Auto Edit (dùng capcut-editor-tool trên máy HP của người dùng)

Dùng khi người dùng muốn dựng/chỉnh một dự án CapCut chỉ bằng prompt, vd. "dựng dự án 1109", "đồng bộ hình với voice, tạo phụ đề, thêm SFX cho dự án X". Công cụ ghi trực tiếp vào `draft_content.json`. **Không dùng computer use, không mở CapCut.**

## QUY TẮC SỐ 1: KHÔNG CÀI ĐẶT GÌ

Môi trường đã cài sẵn trên máy HP (`.venv`, `models\sherpa-onnx-whisper-medium`). Phần nặng (chép lời, ảnh clip) **luôn chạy trên máy HP**, bằng `prepare`.
- **Không** chạy `setup.bat`, `pip install`, `download_model`.
- **Không** cài sherpa-onnx, **không** tải model Whisper, **không** stage file `.MP4` / `.LRF` lên cloud.
- Phần chạy trên cloud (`build`) chỉ cần Python thường, không cần thư viện nào.

## Thông số mặc định

| Mục | Giá trị |
|---|---|
| Thư mục công cụ (`TOOL`) | `C:\Users\PC\Desktop\capcut-editor-tool` |
| Thư mục dự án (`PROJ`) | `C:\Users\PC\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft\<tên>` |
| Dữ liệu chuẩn bị | `TOOL\work\<tên>\` gồm `READY`, `info.json`, `transcript.json`, `resources.json`, `sheets\grid_*.jpg` |
| Kiểu phụ đề | Montserrat, chữ vàng `#f0ff00`, viền đen 0.06, cỡ 10, `position_y` -0.56, hiệu ứng **Phóng to và tô màu** (Color and zoom, id 7325378104753394178) |
| Mẫu kế hoạch | `TOOL\examples\plan_1107.json` |

Chỉ hỏi lại khi thiếu **tên dự án**.

## Bước 0: chọn cách chạy

- **Có shell trên máy HP** (công cụ dạng `mcp__remote-devices__device_bash` có trong danh sách tool): chạy mọi lệnh trên máy HP, trong `TOOL`, bằng `.venv\Scripts\python.exe -m capcut_tool.<lệnh>`. Bước 1 thì tự chạy `prepare <tên>`; bước 6 thì chạy `build work\<tên>\plan.json` (tự sao lưu và ghi) và `preview`.
- **Không có shell** (chỉ có `device_list_dir` / `device_stage_files` / `device_commit_files`, đây là trường hợp thường gặp trong Cowork): làm theo các bước dưới đây. Cloud chỉ đọc file nhỏ và chạy `build`.

## Quy trình

Tạo task list, báo tiến độ ngắn bằng tiếng Việt.

### 1. Kiểm tra dữ liệu đã chuẩn bị
- `device_list_dir` thư mục `TOOL\work\<tên>`. Có file `READY` thì sang bước 2.
- Chưa có `READY`: **dừng lại và nhờ người dùng chạy trên máy HP** (khoảng 3–6 phút, dùng môi trường đã cài):
  > Đóng CapCut, nhấp đúp `prepare.bat` trong `capcut-editor-tool` và nhập `<tên>`, hoặc gõ `prepare.bat <tên>` trong thư mục đó. Chờ đến khi hiện chữ **XONG** rồi nhắn lại cho tôi.

  Khi người dùng báo xong, kiểm tra lại `READY`. Không tự chuyển sang cài đặt trên cloud.
- Nếu `prepare` báo lỗi: đọc thông báo rồi hướng dẫn người dùng xử lý (ổ DJI chưa cắm, dự án chưa import voice, v.v.).

### 2. Stage file nhỏ lên cloud
Gom vào một lần `device_stage_files`:
- `TOOL\work\<tên>\info.json`, `transcript.json`, `resources.json`, cùng mọi `sheets\grid_*.jpg` (tên lấy từ `info.json` → `grids`).
- Code công cụ: `TOOL\capcut_tool\` gồm `__init__.py, common.py, draft.py, build.py, find_resources.py` và `templates\segments.json`.
- Dự án: `PROJ\draft_content.json`, `draft_meta_info.json`, `key_value.json`, `Timelines\project.json`. Ghi lại `mtimeMs` của từng file.

Chép code vào một thư mục cloud (vd. `~/cct/capcut_tool/...`), và chép dự án vào `~/cct/draft/<tên>/` với **đúng cấu trúc** (có `Timelines/project.json`).

### 3. Đọc và sửa lời thoại
- Đọc `transcript.json`, sửa chính tả, tên riêng và từ lóng (vd. "phô mô"→"FOMO", "cắt bà"→"Cát Bà"). Giữ nguyên `start` và `end`.
- Thêm ` | ` để ngắt dòng ở chỗ tự nhiên, khoảng 6–7 từ mỗi dòng. Bỏ dấu chấm cuối câu.

### 4. Chọn cảnh
- Đọc các ảnh `grid_*.jpg`. Mỗi hàng là một clip gồm 6 khung, khung thứ k nằm ở giây `thời lượng × (k+0.5)/6`. `info.json` → `clips` cho biết số thứ tự, đường dẫn, thời lượng và `available` của từng clip.
- Ghép cảnh theo nghĩa của lời thoại:
  - đi làm, văn phòng → cảnh văn phòng, máy tính;
  - du lịch, tự do → cảnh đường đi, biển, phong cảnh;
  - đoạn buồn → cảnh tối hoặc biểu cảm buồn;
  - câu mở đầu → cảnh đẹp nhất làm hook.
- Mỗi cảnh dài 1,5–5 giây; câu dài thì chia thành 2 cảnh. Hạn chế lặp clip. `src + thời lượng` không được vượt độ dài clip. Không dùng clip có `available: false`.

### 5. Viết `plan.json`
Lấy cấu trúc từ `examples/plan_1107.json` (xem docs/PLAN_FORMAT.md):
- `draft_dir`: thư mục dự án **bản cloud**, `~/cct/draft/<tên>`.
- `transcript`: file transcript đã sửa. `voice.path`: lấy từ `info.json` (giữ nguyên đường dẫn Windows).
- `video`: `mute: true`. `clips` ưu tiên dạng `{"chunk": N, "file": "<đường dẫn Windows trong info.json>", "src": s}`; dùng `at` khi chia một câu thành nhiều cảnh.
- `captions`: dùng thông số mặc định. Lấy `font` và `animation` (dòng "Phóng to và tô màu") từ `resources.json`.
- `sfx.library`: lấy từ `resources.json` → `sounds`. Đặt tên ngắn: whoosh (`offset_frames` -6, volume 0.55), pop 0.8, click, shutter, kiss.
- `sfx.events`: khoảng 3–5 giây một SFX.
  - whoosh tại các điểm chuyển chủ đề: `{"kind":"whoosh","cut":i}`.
  - pop tại con số, câu chốt, câu mở đầu và câu kết: `{"kind":"pop","word":"15","near":4.5}`.
  - click ở cảnh máy tính, shutter ở cảnh du lịch.

### 6. Dựng và ghi về máy HP
- Chạy `cd ~/cct && python3 -m capcut_tool.build plan.json --dry-run --out <outputs>/<tên>/draft_content.json`. Kết quả phải in đủ số cảnh, phụ đề và SFX, không có lỗi. Nếu lỗi thì sửa plan rồi chạy lại.
- Đổi `draft_dir` trong plan về đường dẫn Windows thật, rồi lưu `plan.json` cùng `transcript.json` đã sửa vào outputs.
- Gọi `device_commit_files` một lần duy nhất:
  1. bản gốc đã stage → `PROJ\draft_content.backup_<yyyymmdd_hhmm>.json`;
  2. draft mới → `PROJ\draft_content.json` và `PROJ\Timelines\<main_timeline_id>\draft_content.json`, kèm `expectedMtimeMs`;
  3. `draft_meta_info.json` đã cập nhật `tm_duration` bằng `duration` của draft mới → `PROJ\draft_meta_info.json`, kèm `expectedMtimeMs`;
  4. `plan.json`, `transcript.json`, `draft_content.json` → `TOOL\work\<tên>\`, để người dùng có thể chạy lại hoặc xem trước trên máy.
- Nếu `device_commit_files` báo mtime đổi, nghĩa là CapCut đang mở hoặc vừa lưu. Nhắc người dùng đóng CapCut, stage lại rồi ghi lại.

### 7. Báo cáo (ngắn, tiếng Việt)
- Số cảnh, số dòng phụ đề, số SFX.
- Cảnh được ghép theo từng đoạn lời ra sao, SFX đặt ở đâu.
- Bản sao lưu nằm ở đâu. Muốn quay lại bản cũ thì đổi tên file backup thành `draft_content.json`.
- Muốn xem trước trên máy thì chạy: `python -m capcut_tool.preview work\<tên>\draft_content.json -o work\<tên>\preview.mp4` (trong `run.bat`).
- Nhắc mở lại CapCut. Thời điểm từng chữ đổi màu (Color and zoom) chỉ là ước lượng; nếu lệch, dùng nút đồng bộ phụ đề của CapCut.

## Nguyên tắc
- Luôn sao lưu trước khi ghi. Không xoá và không di chuyển file của người dùng.
- Không viết JSON timeline bằng tay; để `build` lo việc căn khung hình và kiểm tra.
- Nếu `build` báo lỗi (thiếu media, `src` vượt độ dài clip, không tìm thấy từ cho SFX): sửa plan theo thông báo, không bỏ qua bước kiểm tra.
- Không đổi media đã import, không di chuyển clip gốc.
- Nếu draft bị mã hoá, hoặc phiên bản CapCut khác `new_version 187.x` mà mở bị lỗi: dừng và báo người dùng.
