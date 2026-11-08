"""Tạo ảnh "contact sheet" (6 khung hình / clip) để xem nhanh nội dung và chọn cảnh.

Ưu tiên dùng file proxy .LRF của DJI (nhẹ hơn ~3 lần) nếu nằm cạnh file .MP4.

    python -m capcut_tool.contact_sheet --draft "C:/.../com.lveditor.draft/1107" -o work/sheets
    python -m capcut_tool.contact_sheet clip1.mp4 clip2.mp4 -o work/sheets
"""
import argparse
import os
import subprocess

from .common import ffprobe_duration, need, save_json
from .draft import list_media


def proxy_for(path):
    base, _ = os.path.splitext(path)
    for ext in (".LRF", ".lrf"):
        if os.path.exists(base + ext):
            return base + ext
    return path


def sheet(path, out_jpg, label, frames=6, height=240):
    d = ffprobe_duration(path)
    tmp = []
    for k in range(frames):
        t = d * (k + 0.5) / frames
        o = f"{out_jpg}.{k}.jpg"
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{t:.3f}", "-i", path,
                        "-frames:v", "1", "-vf", f"scale=-2:{height}", o], check=True)
        tmp.append(o)
    label = label.replace(":", r"\:").replace("'", "")
    args = ["ffmpeg", "-loglevel", "error", "-y"]
    for f in tmp:
        args += ["-i", f]
    args += ["-filter_complex",
             "".join(f"[{i}]" for i in range(frames)) + f"hstack={frames},"
             f"drawtext=text='{label}':fontsize=22:fontcolor=yellow:box=1:boxcolor=black:x=5:y=5",
             out_jpg]
    subprocess.run(args, check=True)
    for f in tmp:
        os.remove(f)
    return d


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("clips", nargs="*", help="danh sách video (bỏ trống nếu dùng --draft)")
    ap.add_argument("--draft", help="thư mục dự án CapCut: lấy toàn bộ video đã import vào dự án")
    ap.add_argument("-o", "--out", default="work/sheets")
    ap.add_argument("--frames", type=int, default=6)
    a = ap.parse_args()
    need("ffmpeg")
    clips = list(a.clips)
    if a.draft:
        clips += [m["path"] for m in list_media(a.draft) if m["kind"] == "video"]
    os.makedirs(a.out, exist_ok=True)
    index = []
    for i, c in enumerate(clips):
        src = proxy_for(c)
        if not os.path.exists(src):
            print(f"[bỏ qua] không thấy file: {c}")
            continue
        name = os.path.basename(c)
        d = sheet(src, os.path.join(a.out, f"{i:02d}.jpg"), f"{i:02d} {name} {ffprobe_duration(src):.0f}s", a.frames)
        index.append({"index": i, "file": c, "duration": round(d, 3), "sheet": f"{i:02d}.jpg"})
        print(f"{i:02d}  {d:7.1f}s  {c}")
    save_json(index, os.path.join(a.out, "index.json"), compact=False)
    print(f"\nXong. Mở các ảnh trong {a.out} để chọn cảnh; index.json ghi số thứ tự <-> file.")


if __name__ == "__main__":
    main()
