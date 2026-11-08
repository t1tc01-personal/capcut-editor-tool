# File kế hoạch (plan JSON)

Ví dụ đầy đủ: [`examples/plan_1107.json`](../examples/plan_1107.json). Đường dẫn Windows viết bằng `/` (hoặc `\\` trong JSON).

```jsonc
{
  "draft_dir": "C:/Users/PC/AppData/Local/CapCut/User Data/Projects/com.lveditor.draft/1107",
  "transcript": "work/transcript.json",          // từ capcut_tool.transcribe
  "end": null,                                     // (tuỳ chọn) cắt video ở giây này; mặc định = hết voice

  "voice": { "path": "C:/Users/PC/Downloads/voice.mp3", "volume": 1.0 },

  "captions": { ... },
  "video":    { "mute": true, "clips": [ ... ] },
  "sfx":      { "library": { ... }, "events": [ ... ] }
}
```

## `transcript`

```json
{ "chunks": [ { "start": 0.88, "end": 2.36, "text": "Biết thế tao nghỉ | việc sớm hơn" } ] }
```

- Mỗi `chunk` là một câu (tách theo khoảng lặng của voice). **Không sửa `start`/`end`** trừ khi chắc chắn.
- Sửa chính tả trực tiếp trong `text`.
- ` | ` = ngắt thành dòng phụ đề mới. Câu không có ` | ` mà dài hơn `max_words` sẽ tự chia đều.

## `captions`

| Khoá | Mặc định | Ý nghĩa |
|---|---|---|
| `texts` | – | (tuỳ chọn) danh sách thay thế toàn bộ `text` của transcript, **đúng số câu**. |
| `replace` | `{}` | Sửa nhanh, vd. `{"phô mô": "FOMO", "cắt bà": "Cát Bà"}`. |
| `max_words` | 6 | Số từ tối đa/dòng khi tự chia. |
| `color` | `#f0ff00` | Màu chữ (vàng mặc định của CapCut). |
| `stroke_color` / `stroke_width` | `#000000` / `0.06` | Viền đen. |
| `font_size` | 10 | Cỡ chữ CapCut. |
| `position_y` | -0.56 | Vị trí dọc (-1 đáy … 1 đỉnh). |
| `tail` | 0.25 | Giữ phụ đề thêm (giây) sau chữ cuối nếu chưa tới câu sau. |
| `font` | Montserrat | `{id, title, path}` – font trong Cache\effect. |
| `animation` | Color and zoom | `{id, name, path}`; đặt `null` để không dùng hiệu ứng. |

Hiệu ứng *Color and zoom* đổi màu/phóng to từng chữ dựa trên `words` (mốc từng chữ) mà công cụ tự tính.

## `video.clips`

Danh sách cảnh **theo thứ tự**. Mỗi cảnh kéo dài tới khi cảnh sau bắt đầu (cảnh cuối tới hết voice).

```json
{ "chunk": 3, "file": "F:/DCIM/DJI_002/DJI_20261017180236_0377_D.MP4", "src": 0 }
{ "at": 19.9, "file": "D:/New folder/DJI_001/mới2/DJI_20260617115702_0111_D.MP4", "src": 1 }
```

| Khoá | Ý nghĩa |
|---|---|
| `chunk` | Bắt đầu cảnh đúng đầu câu số N (đếm từ 0) – cách tốt nhất để khớp hình với lời. |
| `at` | Hoặc thời điểm tuyệt đối (giây). Cảnh đầu luôn bắt đầu ở 0. |
| `file` | Đường dẫn clip (nên đã import vào thư viện dự án; nếu chưa, công cụ đọc bằng ffprobe). |
| `src` | Lấy từ giây thứ mấy trong clip (xem ảnh contact sheet: khung k ở `thời lượng × (k+0.5)/6`). |
| `scale` | (tuỳ chọn) phóng to cảnh, mặc định 1.0. |
| `volume` | (tuỳ chọn) âm lượng clip khi `video.mute = false`. |

`video.mute: true` tắt tiếng gốc của clip để chỉ nghe voice.

## `sfx`

`library` khai báo âm thanh dùng được (lấy từ Cache\music của CapCut hoặc file mp3/wav bất kỳ):

```json
"whoosh": { "name": "\"whoosh\" (Badminton racket swing) D(966368)",
            "path": "C:/Users/PC/AppData/Local/CapCut/User Data/Cache/music/43000c5d7742793472d186bd8a7ed6a7.mp3",
            "duration_us": 400000, "effect_id": "6930311127939155969",
            "volume": 0.55, "offset_frames": -6 }
```

`offset_frames` dịch SFX theo khung hình (vd. -6 = bắt đầu sớm 0.2 s để đỉnh tiếng whoosh rơi đúng điểm cắt).

`events` – mỗi sự kiện chọn **một** cách neo thời gian:

| Neo | Ví dụ | Ý nghĩa |
|---|---|---|
| `cut` | `{"kind":"whoosh","cut":7}` | Tại điểm bắt đầu cảnh số 7 (đếm từ 0). |
| `word` + `near` | `{"kind":"pop","word":"15","near":4.5}` | Tại chữ "15" gần giây 4.5 nhất. |
| `chunk` | `{"kind":"pop","chunk":12}` | Tại đầu câu số 12. |
| `at` | `{"kind":"click","at":10.3}` | Thời điểm tuyệt đối. |

Tuỳ chọn mỗi sự kiện: `volume`, `offset_frames`. Các SFX chồng nhau được tự xếp sang track âm thanh mới.

## Gợi ý chọn SFX

- **whoosh**: các lần chuyển cảnh lớn (chuyển chủ đề).
- **pop**: chữ cần nhấn (con số, từ cảm thán, câu chốt).
- **click chuột/bàn phím**: cảnh máy tính, văn phòng.
- **chụp ảnh**: cảnh du lịch, check-in, khoe đồ.
- Không nên quá 1 SFX mỗi 2–3 giây để khỏi rối.
