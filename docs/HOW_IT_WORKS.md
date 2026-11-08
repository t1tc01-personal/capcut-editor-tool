# Cách công cụ hoạt động

## Cấu trúc một dự án CapCut PC

```
com.lveditor.draft/<tên dự án>/
├─ draft_content.json          ← timeline (tracks + materials) – công cụ ghi file này
├─ draft_meta_info.json        ← thư viện media đã import, tm_duration
├─ key_value.json              ← md5 của media, lịch sử dùng hiệu ứng
└─ Timelines/
   ├─ project.json             ← main_timeline_id
   └─ <main_timeline_id>/draft_content.json   ← bản sao timeline (cũng được ghi)
```

`draft_content.json`:

- `tracks[]` – mỗi track có `type` (`video`, `text`, `audio`), `flag` (1 = track phụ đề), `segments[]`.
- Mỗi segment có `target_timerange` (vị trí trên timeline), `source_timerange` (đoạn lấy từ file), đơn vị **micro-giây**, `material_id` + `extra_material_refs` trỏ tới `materials`.
- `materials` gồm `videos`, `audios`, `texts`, `material_animations` (hiệu ứng chữ), `speeds`, `canvases`, `beats`, `sound_channel_mappings`, `vocal_separations`, …

## Công cụ ghi gì

1. Đọc `draft_content.json` hiện tại (giữ nguyên cấu hình canvas 9:16, fps, id dự án…).
2. Nhân bản các **segment mẫu** trong `capcut_tool/templates/segments.json` (lấy từ dự án CapCut thật, phiên bản 187.0.0) và thay id, đường dẫn, thời gian:
   - **video** (track chính, `attribute: 1`), volume 0 khi `mute`;
   - **voice** (`type: extract_music`);
   - **phụ đề** (`type: subtitle`, `add_type: 1`) với `content` chứa màu/viền/font, `words` chứa mốc từng chữ (ms, tương đối đầu dòng), animation `type: caption` = *Phóng to và tô màu*;
   - **SFX** (`type: sound`) trỏ tới mp3 trong `Cache\music`.
3. Mọi mốc thời gian làm tròn về **khung hình** (`round(giây × fps)` → µs) nên điểm cắt, phụ đề và SFX luôn rơi đúng frame.
4. Kiểm tra: không chồng lấn trên cùng track, mọi `material_id` đều tồn tại, cảnh không vượt độ dài clip.
5. Sao lưu `draft_content.json` (cả 2 bản) + `draft_meta_info.json` vào `_backup_capcut_tool_<thời gian>/`, rồi ghi mới và cập nhật `tm_duration`.

## Chép lời

`transcribe.py`: ffmpeg `silencedetect` tách câu theo khoảng lặng → mỗi câu (đệm 0.3 s lặng đầu, 1 s cuối để không mất chữ cuối) đưa vào Whisper medium bản ONNX (sherpa-onnx), ngôn ngữ `vi`. Mốc câu chính xác theo khoảng lặng; mốc từng chữ do `build.py` chia theo độ dài chữ (tiếng Việt mỗi từ ~ 1 âm tiết, voice AI đọc đều nên sai lệch nhỏ).

## Cập nhật khi CapCut đổi phiên bản

Nếu CapCut mới báo lỗi mở dự án: tạo một dự án nhỏ có đủ 1 clip, 1 voice, 1 phụ đề tự động có Color and zoom, 1 SFX, lưu, rồi trích lại `templates/segments.json` (mỗi mục: `segment` + danh sách `[loại_material, material]` theo thứ tự `material_id`, `extra_material_refs`).
