# CapCut Editor Tool

Dựng timeline CapCut **không cần mở CapCut**: công cụ ghi thẳng vào file dự án (`draft_content.json`) để

- **đồng bộ hình ảnh với voice** – mỗi cảnh cắt đúng đầu câu, khớp từng khung hình (30 fps);
- **tạo phụ đề tự động** từ voice (Whisper chạy offline), font **Montserrat**, **chữ vàng viền đen**;
- gắn hiệu ứng chú thích **Color and zoom (Phóng to và tô màu)** – từng chữ phóng to/đổi màu theo lời nói;
- **thêm hiệu ứng âm thanh** (whoosh, pop, click, chụp ảnh…) đặt chính xác theo khung hình: tại điểm cắt cảnh hoặc tại một từ trong lời thoại;
- xuất **video xem trước** để kiểm tra nhanh, và **tự sao lưu** dự án trước khi ghi.

> Đã dùng để dựng dự án `1107` (voice 83 s, 28 cảnh, 67 dòng phụ đề, 20 SFX). File kế hoạch mẫu nằm trong `examples/`.

## Cài đặt & sử dụng từ A–Z

| Hệ điều hành | Hướng dẫn | Script cài |
|---|---|---|
| **Windows 10/11** | [docs/HUONG_DAN_WINDOWS.md](docs/HUONG_DAN_WINDOWS.md) | `setup.bat`, `run.bat` |
| **macOS (MacBook Intel / Apple M)** | [docs/HUONG_DAN_MACOS.md](docs/HUONG_DAN_MACOS.md) | `setup.sh`, `run.sh` |

Tóm tắt: cài **Python 3.10+** và **ffmpeg** → chạy script cài (tạo môi trường, cài thư viện, tải model Whisper ~1.9 GB) → mỗi lần dùng mở `run.bat` / `source run.sh`.

## Cách nhanh nhất: chuẩn bị trên máy, dựng bằng prompt

1. Import voice + clip vào dự án CapCut, đóng CapCut.
2. Nhấp đúp **`prepare.bat`** (Mac: `./prepare.sh 1109`) → nhập tên dự án. Máy bạn tự chép lời voice, tạo ảnh xem clip, tìm font/hiệu ứng/SFX vào `work\<dự án>\` (dùng môi trường đã cài, không tải lại gì).
3. Nhắn Claude: *"Dựng dự án 1109"* (skill `capcut-auto-edit`). Claude chỉ đọc các file nhỏ trong `work\<dự án>\`, viết kế hoạch và ghi thẳng vào dự án — không cài đặt, không tải model.

## Quy trình 5 bước

> ⚠️ **Đóng dự án trong CapCut** (hoặc tắt CapCut) trước bước 4, nếu không CapCut sẽ ghi đè thay đổi.

| Bước | Lệnh | Kết quả |
|---|---|---|
| 0. Chuẩn bị | Trong CapCut: tạo dự án, **import** voice + các clip vào thư viện (không cần kéo vào timeline), dùng thử hiệu ứng chú thích *Color and zoom*, font *Montserrat* và các SFX một lần để CapCut tải về bộ nhớ đệm. Đóng CapCut. | |
| 1. Chép lời | `python -m capcut_tool.transcribe "C:\Users\PC\Downloads\voice.mp3" -o work\transcript.json` | Câu + mốc thời gian. Sửa chính tả, thêm ` \| ` để ngắt dòng phụ đề. |
| 1b. Lấy tài nguyên | `python -m capcut_tool.find_resources "<thư mục com.lveditor.draft>" --check` | Đường dẫn font, hiệu ứng chữ, SFX trên máy (bắt buộc khi dùng Mac / máy khác). |
| 2. Xem clip | `python -m capcut_tool.contact_sheet --draft "<thư mục dự án>" -o work\sheets` | Ảnh 6 khung/clip + `index.json` để chọn cảnh. |
| 3. Viết kế hoạch | Sao chép `examples\plan_1107.json` → `work\plan.json`, sửa: `draft_dir`, `voice`, danh sách `clips`, `sfx.events`. | Xem [docs/PLAN_FORMAT.md](docs/PLAN_FORMAT.md). |
| 4. Dựng | `python -m capcut_tool.build work\plan.json --dry-run` rồi `python -m capcut_tool.preview work\draft_content.json -o work\preview.mp4` để kiểm tra; ổn thì chạy `python -m capcut_tool.build work\plan.json` | Ghi vào dự án + thư mục sao lưu `_backup_capcut_tool_<thời gian>`. |
| 5. Hoàn thiện | Mở dự án trong CapCut, xem lại, xuất video. | |

Khôi phục bản trước khi dựng:

```bat
python -m capcut_tool.restore "%LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft\1107\_backup_capcut_tool_20261108_170000"
```

## Dùng bằng prompt (Claude Skill)

`skills/capcut-auto-edit/SKILL.md` là skill để Claude (Cowork / Claude Code) tự chạy toàn bộ quy trình chỉ từ một câu lệnh, vd. *"Dựng dự án 1109 bằng capcut-auto-edit"*.
Cài: lưu skill từ thẻ đề xuất trong Claude, hoặc chép thư mục `skills/capcut-auto-edit` vào thư mục skills của Claude (vd. `~/.claude/skills/`).

## Cấu trúc thư mục

```
capcut-editor-tool/
├─ README.md                 – tài liệu này
├─ setup.bat / run.bat       – cài đặt & mở môi trường (Windows)
├─ setup.sh / run.sh         – cài đặt & mở môi trường (macOS)
├─ prepare.bat / prepare.sh  – chuẩn bị dữ liệu cho một dự án (chạy trên máy)
├─ requirements.txt
├─ docs/
│  ├─ HUONG_DAN_WINDOWS.md   – cài đặt & sử dụng A–Z trên Windows
│  ├─ HUONG_DAN_MACOS.md     – cài đặt & sử dụng A–Z trên macOS
│  ├─ INSTALL.md             – ghi chú cài đặt chung
│  ├─ PLAN_FORMAT.md         – mô tả đầy đủ file kế hoạch
│  └─ HOW_IT_WORKS.md        – cấu trúc file dự án CapCut & cách công cụ ghi
├─ capcut_tool/
│  ├─ transcribe.py          – voice → transcript (Whisper/sherpa-onnx, offline)
│  ├─ contact_sheet.py       – ảnh xem nhanh clip (ưu tiên proxy .LRF của DJI)
│  ├─ build.py               – plan → draft_content.json (cảnh, phụ đề, SFX)
│  ├─ preview.py             – xuất video xem trước từ draft
│  ├─ restore.py             – khôi phục bản sao lưu
│  ├─ prepare.py             – chuẩn bị trên máy: transcript + ảnh clip + tài nguyên → work/<dự án>/
│  ├─ find_resources.py      – tìm đường dẫn font / hiệu ứng / SFX trong Cache CapCut
│  ├─ download_model.py      – tải model Whisper
│  ├─ draft.py, common.py    – đọc/ghi dự án, tiện ích thời gian theo khung hình
│  └─ templates/segments.json– segment mẫu (video, voice, phụ đề, SFX) lấy từ CapCut 187.0.0
├─ skills/
│  └─ capcut-auto-edit/SKILL.md – skill Claude: dựng dự án chỉ bằng prompt
└─ examples/
   ├─ plan_1107.json         – kế hoạch thực tế của dự án 1107
   └─ transcript_1107.json   – lời thoại đã sửa của dự án 1107
```

## Giới hạn cần biết

- Viết cho **CapCut PC, draft dạng JSON thường** (đã kiểm tra với `new_version 187.0.0`). Nếu bản CapCut mới mã hoá `draft_content.json`, công cụ sẽ báo lỗi và không ghi gì.
- Hiệu ứng chú thích, font và SFX là tài nguyên CapCut: phải **có sẵn trong bộ nhớ đệm** (`%LOCALAPPDATA%\CapCut\User Data\Cache\effect` và `...\Cache\music`). Nếu thiếu, hãy dùng thử chúng một lần trong CapCut. Các đường dẫn hiện tại đã khai báo trong `examples/plan_1107.json`.
- Mốc thời gian **từng chữ** (cho Color and zoom) được ước lượng theo độ dài chữ trong câu; mốc **từng câu** lấy chính xác từ khoảng lặng của voice. Nếu cần chuẩn hơn, dùng nút đồng bộ phụ đề của CapCut sau khi mở.
- Chọn cảnh (clip nào cho câu nào) là phần **sáng tạo** – bạn khai báo trong file kế hoạch, công cụ lo phần căn khung hình, phụ đề, SFX và cấu trúc file.
