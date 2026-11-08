---
name: capcut-auto-edit
description: Dựng tự động dự án CapCut PC bằng capcut-editor-tool (không mở CapCut): khớp cảnh với voice, phụ đề tự động vàng viền đen Montserrat + Color and zoom, SFX khớp khung hình.
---

# CapCut Auto Edit (dùng capcut-editor-tool)

Dùng khi người dùng muốn chỉnh/dựng một dự án CapCut chỉ bằng prompt, ví dụ: "dựng dự án 1109", "đồng bộ hình với voice, tạo phụ đề, thêm SFX cho dự án X". Công cụ ghi trực tiếp vào `draft_content.json`. **Không bao giờ dùng computer use hay mở CapCut.**

## Thông số mặc định (của người dùng này)

| Mục | Giá trị |
|---|---|
| Thư mục công cụ | `C:\Users\PC\Desktop\capcut-editor-tool` (Mac: `~/Desktop/capcut-editor-tool`) |
| Thư mục dự án | `C:\Users\PC\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft\<tên>` |
| Bộ nhớ đệm CapCut | `...\CapCut\User Data\Cache\effect` (font, hiệu ứng chữ), `...\Cache\music` (SFX) |
| Kiểu phụ đề | Montserrat, chữ vàng `#f0ff00`, viền đen 0.06, cỡ 10, `position_y` -0.56, hiệu ứng **Phóng to và tô màu** (Color and zoom, id 7325378104753394178) |
| Voice | thường là mp3 ElevenLabs trong `Downloads`, tiếng Việt, khung 9:16, 30 fps |
| Clip | DJI trên ổ ngoài (`F:\DCIM\DJI_002`, `D:\New folder\DJI_001`), có proxy `.LRF` cạnh mỗi `.MP4` |
| Mẫu kế hoạch | `examples\plan_1107.json`, `examples\transcript_1107.json` trong thư mục công cụ |

Nếu prompt không nói gì khác, dùng các thông số trên. Chỉ hỏi lại khi thiếu **tên dự án**.

## Chọn chế độ chạy

- **A. Chạy trên máy người dùng** — nếu có tool shell trên máy (vd. `mcp__remote-devices__device_bash`) và `.venv` + `models/` đã có trong thư mục công cụ: chạy thẳng các lệnh `python -m capcut_tool...` ở đó. Nhanh nhất, không phải chuyển file.
- **B. Chạy trên cloud** — nếu chỉ có stage/commit file (không có shell trên máy): stage code công cụ + file cần thiết vào cloud, chạy công cụ ở cloud, rồi commit `draft_content.json` về máy. Chi tiết ở mục "Chế độ B".

Cả hai chế độ đều theo cùng một quy trình dưới đây.

## Quy trình

Tạo task list theo các bước sau, báo tiến độ ngắn gọn bằng tiếng Việt.

### 1. Đọc dự án
- Liệt kê `<thư mục dự án>`. Đọc `draft_content.json` (phải là JSON thường; nếu bị mã hoá → dừng, báo người dùng), `draft_meta_info.json` (`draft_materials`: type 0 = video/ảnh, type 1 = voice), `Timelines/project.json`.
- Xác định: file voice, danh sách clip đã import, canvas/fps. Nếu timeline đang có nội dung thì nói rõ sẽ thay thế (có sao lưu).
- Nhắc người dùng **đóng CapCut** trước khi ghi.

### 2. Chép lời voice
`python -m capcut_tool.transcribe "<voice>" -o work/transcript.json --model models/sherpa-onnx-whisper-medium --lang vi`
- Kiểm tra toàn bộ câu: sửa chính tả, tên riêng, từ lóng (vd. "phô mô"→"FOMO", "cắt bà"→"Cát Bà", "chúa tệ"→"chúa tể"). Giữ nguyên `start`/`end`.
- Thêm ` | ` để ngắt dòng ở chỗ tự nhiên (tối đa ~6–7 từ/dòng, không cắt giữa cụm từ). Bỏ dấu chấm cuối dòng.

### 3. Xem clip và chọn cảnh
`python -m capcut_tool.contact_sheet --draft "<thư mục dự án>" -o work/sheets` (công cụ tự dùng `.LRF` nếu có).
- Xem từng ảnh trong `work/sheets` (ảnh 6 khung/clip; khung k ở giây `thời lượng × (k+0.5)/6`); `index.json` ghi số thứ tự ↔ file.
- Ghép cảnh theo **nghĩa của lời thoại**: câu về văn phòng/áp lực → cảnh văn phòng, máy tính; câu về du lịch/tự do → cảnh đường, biển, phong cảnh; câu buồn → cảnh tối/biểu cảm buồn; câu mở đầu → cảnh đẹp nhất làm hook.
- Mỗi cảnh nên dài 1,5–5 s; câu dài thì chia 2 cảnh. Hạn chế lặp clip; nếu lặp thì lấy đoạn `src` khác. Bảo đảm `src + thời lượng` không vượt độ dài clip.

### 4. Lấy tài nguyên CapCut
`python -m capcut_tool.find_resources "<thư mục com.lveditor.draft>" --check`
- Lấy `font` Montserrat, `animation` "Phóng to và tô màu" (type=caption) và các SFX **còn tồn tại** trong Cache.
- Đặt tên ngắn cho SFX: `whoosh` (thêm `"offset_frames": -6`, volume ~0.55), `pop` (~0.8), `click`, `shutter`, `kiss`… Nếu thiếu font/hiệu ứng → bảo người dùng dùng thử chúng một lần trong CapCut.

### 5. Viết kế hoạch `work/plan.json`
Sao chép cấu trúc từ `examples/plan_1107.json` (đầy đủ trường: docs/PLAN_FORMAT.md). Điền:
- `draft_dir`, `transcript: work/transcript.json`, `voice.path`.
- `video.mute: true`; `video.clips`: ưu tiên `{"chunk": N, "file": ..., "src": ...}` để cảnh bắt đầu đúng đầu câu; dùng `at` (giây) khi chia một câu thành nhiều cảnh.
- `captions`: thông số mặc định ở trên.
- `sfx.events` (khoảng 1 SFX mỗi 3–5 s, không dày hơn):
  - `whoosh` tại các điểm chuyển chủ đề: `{"kind":"whoosh","cut":i}`;
  - `pop` tại từ cần nhấn (số tiền, con số, câu chốt, câu mở đầu): `{"kind":"pop","word":"15","near":4.5}`;
  - `click` ở cảnh máy tính, `shutter` ở cảnh du lịch/check-in, `kiss`/`pop` ở chỗ cười đùa;
  - `pop` ở câu kết.

### 6. Dựng thử và kiểm tra
`python -m capcut_tool.build work/plan.json --dry-run` → phải in `Timeline: ...s | N cảnh | N phụ đề | N SFX`, không lỗi.
`python -m capcut_tool.preview work/draft_content.json -o work/preview.mp4` (thêm `--map CŨ=MỚI` nếu đường dẫn media khác).
- Trích vài khung từ preview (ở giữa vài câu) và xem để kiểm tra: cảnh hợp lời, phụ đề đúng chữ, đúng vị trí.
- Sửa plan/transcript rồi chạy lại nếu cần.

### 7. Ghi vào dự án
- Chế độ A: `python -m capcut_tool.build work/plan.json` (tự sao lưu vào `<dự án>/_backup_capcut_tool_<thời gian>/`, ghi cả `Timelines/<main_timeline_id>/draft_content.json`, cập nhật `tm_duration`).
- Chế độ B: xem bên dưới.

### 8. Báo cáo
Ngắn gọn bằng tiếng Việt: số cảnh / dòng phụ đề / SFX; tóm tắt cách ghép cảnh theo từng đoạn lời; SFX đặt ở đâu; chỗ sao lưu và cách khôi phục (`python -m capcut_tool.restore "<thư mục backup>"`); nhắc mở lại CapCut, và rằng mốc *từng chữ* của Color and zoom là ước lượng (có thể dùng nút đồng bộ phụ đề của CapCut). Gửi `preview.mp4` nếu có.

## Chế độ B: chạy trên cloud (chỉ có stage/commit)

1. Stage code: tất cả file trong `capcut-editor-tool/capcut_tool/` (gồm `templates/segments.json`) + `examples/plan_1107.json` + `requirements.txt`. Dựng lại cây thư mục trong workspace cloud (vd. `~/capcut-editor-tool/`).
2. Cài: `pip install sherpa-onnx soundfile numpy --break-system-packages`. Tải model: `python -m capcut_tool.download_model medium` (tải từ GitHub; HuggingFace có thể bị chặn — không cần).
3. Stage dự án: `draft_content.json`, `draft_meta_info.json`, `key_value.json`, `Timelines/project.json`. Chép vào một thư mục cloud có cùng cấu trúc và đặt `draft_dir` trong plan **trỏ tới bản cloud** (build tra cứu media qua `draft_meta_info.json`, không cần file video gốc).
4. Stage voice (mp3) để transcribe. Để xem clip, stage file **`.LRF`** (không stage `.MP4` gốc — quá nặng), chia lô ≤ ~180 MB mỗi lần stage, file >100 MB stage riêng. Chạy `contact_sheet` với danh sách file LRF.
5. Stage các mp3 SFX từ `Cache/music` nếu muốn preview có tiếng; chạy preview với `--map` cho từng tiền tố (vd. `--map "F:/DCIM/DJI_002=<thư mục LRF đã stage>"`).
6. Chạy `build --dry-run --out <outputs>/draft_content.json` (**luôn dry-run ở cloud**).
7. Sao lưu và ghi về máy bằng commit:
   - copy bản gốc đã stage thành `draft_content.backup_<thời gian>.json` → commit vào thư mục dự án;
   - commit `draft_content.json` mới vào **cả hai** `<dự án>/draft_content.json` và `<dự án>/Timelines/<main_timeline_id>/draft_content.json`, dùng `expectedMtimeMs` lấy từ lúc stage;
   - cập nhật `tm_duration` (= `duration` của draft mới) trong `draft_meta_info.json` rồi commit.

## Nguyên tắc
- Không xoá file của người dùng; luôn sao lưu trước khi ghi.
- Không đổi media đã import, không di chuyển clip gốc.
- Mọi mốc thời gian để công cụ làm tròn theo khung hình — không tự viết JSON timeline bằng tay.
- Nếu `build` báo lỗi (thiếu media, `src` vượt độ dài clip, không thấy từ cho SFX) → sửa plan theo thông báo, không bỏ qua kiểm tra.
- Draft bị mã hoá hoặc phiên bản CapCut khác `new_version 187.x` mà mở lỗi → dừng, báo người dùng (xem docs/HOW_IT_WORKS.md mục cập nhật template).
