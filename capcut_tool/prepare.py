"""Chuẩn bị mọi dữ liệu nặng cho một dự án NGAY TRÊN MÁY (dùng môi trường đã cài sẵn):
chép lời voice, ảnh xem nhanh các clip, tài nguyên CapCut. Sau đó Claude chỉ cần đọc các file nhỏ
trong work/<dự án>/ để viết kế hoạch — không phải cài đặt hay tải model lại.

    python -m capcut_tool.prepare 1109
    python -m capcut_tool.prepare "C:/.../com.lveditor.draft/1109" --force   # làm lại từ đầu

Kết quả (work/<dự án>/):
    info.json        – voice, danh sách clip (đường dẫn, thời lượng, số thứ tự), fps, canvas
    transcript.json  – lời thoại theo câu + mốc thời gian (bỏ qua nếu đã có, trừ khi --force)
    resources.json   – font / hiệu ứng chữ / SFX còn trong Cache CapCut
    sheets/NN.jpg    – 6 khung hình mỗi clip;  sheets/grid_NN.jpg – gộp 6 clip/ảnh để xem nhanh
    READY            – đánh dấu đã chuẩn bị xong
"""
import argparse
import os
import platform
import subprocess

from . import draft as D
from .common import ffprobe_duration, need, save_json, load_json
from .contact_sheet import proxy_for, sheet
from .find_resources import scan

TOOL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def default_drafts_root():
    if platform.system() == "Windows":
        return os.path.join(os.environ.get("LOCALAPPDATA", ""), "CapCut", "User Data", "Projects", "com.lveditor.draft")
    for p in ("~/Movies/CapCut/User Data/Projects/com.lveditor.draft",
              "~/Library/Containers/com.lemon.lvoverseas/Data/Movies/CapCut/User Data/Projects/com.lveditor.draft"):
        p = os.path.expanduser(p)
        if os.path.isdir(p):
            return p
    return os.path.expanduser("~/Movies/CapCut/User Data/Projects/com.lveditor.draft")


def grids(sheet_dir, files, per=6):
    out = []
    for g in range(0, len(files), per):
        chunk = files[g:g + per]
        args = ["ffmpeg", "-loglevel", "error", "-y"]
        for f in chunk:
            args += ["-i", os.path.join(sheet_dir, f)]
        name = f"grid_{g:02d}.jpg"
        # clip quay ngang cho ảnh rộng hơn -> co/đệm mọi ảnh về cùng khổ 816x240 để vstack được
        fit = "scale=816:240:force_original_aspect_ratio=decrease,pad=816:240:0:(oh-ih)/2"
        if len(chunk) == 1:
            args += ["-vf", fit, os.path.join(sheet_dir, name)]
        else:
            fc = ";".join(f"[{i}]{fit}[v{i}]" for i in range(len(chunk)))
            fc += ";" + "".join(f"[v{i}]" for i in range(len(chunk))) + f"vstack={len(chunk)}"
            args += ["-filter_complex", fc, os.path.join(sheet_dir, name)]
        subprocess.run(args, check=True)
        out.append(name)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project", help="tên dự án (vd. 1109) hoặc đường dẫn đầy đủ tới thư mục dự án")
    ap.add_argument("--drafts-root", default=None, help="thư mục com.lveditor.draft (mặc định theo hệ điều hành)")
    ap.add_argument("--model", default=os.path.join(TOOL_DIR, "models", "sherpa-onnx-whisper-medium"))
    ap.add_argument("--lang", default="vi")
    ap.add_argument("--force", action="store_true", help="làm lại kể cả khi đã có transcript/sheets")
    ap.add_argument("--no-sheets", action="store_true")
    a = ap.parse_args()
    need("ffmpeg")

    root = a.drafts_root or default_drafts_root()
    proj = a.project if os.path.isdir(a.project) else os.path.join(root, a.project)
    if not os.path.isfile(os.path.join(proj, "draft_content.json")):
        raise SystemExit(f"Không thấy dự án: {proj}")
    name = os.path.basename(os.path.normpath(proj))
    root = os.path.dirname(os.path.normpath(proj))
    out = os.path.join(TOOL_DIR, "work", name)
    os.makedirs(out, exist_ok=True)
    ready = os.path.join(out, "READY")
    if os.path.exists(ready):
        os.remove(ready)

    content = D.load_content(proj)  # cũng kiểm tra draft có phải JSON thường
    media = D.list_media(proj)
    voices = [m for m in media if m["kind"] == "audio"]
    videos = [m for m in media if m["kind"] == "video"]
    if not voices:
        raise SystemExit("Dự án chưa import voice (audio) vào thư viện media.")
    voice = voices[-1]
    print(f"Dự án {name}: {len(videos)} clip, voice = {voice['path']}")

    # 1. transcript
    tpath = os.path.join(out, "transcript.json")
    if a.force or not os.path.exists(tpath) or load_json(tpath).get("audio_src") != voice["path"]:
        from .transcribe import transcribe
        print("\n[1/3] Chép lời voice...")
        res = transcribe(voice["path"], a.model, a.lang)
        res["audio_src"] = voice["path"]
        save_json(res, tpath, compact=False)
    else:
        print("\n[1/3] Đã có transcript.json — bỏ qua (dùng --force để làm lại)")

    # 2. contact sheets
    sdir = os.path.join(out, "sheets")
    os.makedirs(sdir, exist_ok=True)
    clips = []
    print("\n[2/3] Ảnh xem nhanh các clip...")
    for i, m in enumerate(videos):
        src = proxy_for(m["path"])
        item = {"index": i, "file": m["path"], "duration": round(m["duration_us"] / 1e6, 3),
                "width": m["width"], "height": m["height"], "sheet": f"{i:02d}.jpg", "available": os.path.exists(src)}
        if not item["available"]:
            print(f"  [thiếu file] {m['path']} (ổ đĩa chưa cắm?)")
        elif not a.no_sheets:
            jpg = os.path.join(sdir, item["sheet"])
            if a.force or not os.path.exists(jpg):
                sheet(src, jpg, f"{i:02d} {os.path.basename(m['path'])} {item['duration']:.0f}s")
            print(f"  {i:02d} {item['duration']:7.1f}s {os.path.basename(m['path'])}")
        clips.append(item)
    grid_files = grids(sdir, [c["sheet"] for c in clips if c["available"]]) if not a.no_sheets else []

    # 3. resources + info
    print("\n[3/3] Tài nguyên CapCut...")
    _, fonts, anims, sounds = scan(root)
    ok = lambda p: os.path.exists(p)
    save_json({"fonts": [v for v in fonts.values() if ok(v["path"])],
               "animations": [v for v in anims.values() if ok(v["path"])],
               "sounds": [v for v in sounds.values() if ok(v["path"])]},
              os.path.join(out, "resources.json"), compact=False)
    save_json({"project": name, "draft_dir": proj.replace("\\", "/"), "drafts_root": root.replace("\\", "/"),
               "fps": content.get("fps"), "canvas": content.get("canvas_config"),
               "voice": {"path": voice["path"], "duration_us": voice["duration_us"]},
               "clips": clips, "grids": grid_files}, os.path.join(out, "info.json"), compact=False)
    open(ready, "w").close()
    print(f"\nXONG. Dữ liệu ở: {out}\nGiờ chỉ cần nhắn Claude: \"dựng dự án {name}\".")


if __name__ == "__main__":
    main()
