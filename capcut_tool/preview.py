"""Xuất video xem trước (540x960) từ draft_content.json để kiểm tra nhịp cắt, phụ đề, SFX
mà không cần mở CapCut. Dùng proxy .LRF nếu có.

    python -m capcut_tool.preview work/draft_content.json -o work/preview.mp4
"""
import argparse
import os
import subprocess
import tempfile

from .common import load_json, need
from .contact_sheet import proxy_for


def ts(t):
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


def remap(path, maps):
    for old, new in maps:
        if path.lower().startswith(old.lower()):
            return new + path[len(old):]
    return path


def render(content_path, out, font="Montserrat", width=540, height=960, maps=()):
    need("ffmpeg")
    out = os.path.abspath(out)
    d = load_json(content_path)
    M = {m["id"]: m for v in d["materials"].values() for m in v}
    vt = next(t for t in d["tracks"] if t["type"] == "video")
    tt = next((t for t in d["tracks"] if t["type"] == "text" and t["flag"] == 1), {"segments": []})
    at = [s for t in d["tracks"] if t["type"] == "audio" for s in t["segments"]]
    with tempfile.TemporaryDirectory() as td:
        parts = []
        for i, s in enumerate(sorted(vt["segments"], key=lambda s: s["target_timerange"]["start"])):
            src = proxy_for(remap(M[s["material_id"]]["path"], maps))
            o = os.path.join(td, f"v{i:03d}.mp4")
            subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{s['source_timerange']['start']/1e6:.6f}",
                            "-i", src, "-t", f"{s['target_timerange']['duration']/1e6:.6f}", "-an",
                            "-vf", f"scale={width}:{height},fps=30", "-c:v", "libx264", "-preset", "veryfast",
                            "-crf", "26", o], check=True)
            parts.append(o)
        lst = os.path.join(td, "list.txt")
        with open(lst, "w", encoding="utf-8") as f:
            f.writelines(f"file '{p}'\n" for p in parts)
        ass = ["[Script Info]", f"PlayResX: {width}", f"PlayResY: {height}", "", "[V4+ Styles]",
               "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
               "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
               f"Style: Y,{font},34,&H0000FFF0,&H00FFFFFF,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,3,0,2,30,30,{int(height*0.2)},1",
               "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
        for s in tt["segments"]:
            m = M[s["material_id"]]
            a = s["target_timerange"]["start"] / 1e6
            b = a + s["target_timerange"]["duration"] / 1e6
            w = m["words"]
            toks = [(t, st) for t, st in zip(w["text"], w["start_time"]) if t.strip()]
            if not toks:
                continue
            for j, (t, st) in enumerate(toks):  # mô phỏng "color & zoom": từ đang đọc phóng to, đổi màu
                ws = a + st / 1000
                we = a + toks[j + 1][1] / 1000 if j + 1 < len(toks) else b
                txt = " ".join(("{\\fscx118\\fscy118\\c&H00FFFFFF&}" + x + "{\\r}") if k == j else x
                               for k, (x, _) in enumerate(toks))
                ass.append(f"Dialogue: 0,{ts(ws)},{ts(we)},Y,,0,0,0,,{txt}")
        assf = os.path.join(td, "subs.ass")
        with open(assf, "w", encoding="utf-8") as f:
            f.write("\n".join(ass))
        ins, flt, labels = [], [], []
        for s in at:
            m = M[s["material_id"]]
            apath = remap(m["path"], maps)
            if not os.path.exists(apath):
                print("[thiếu âm thanh]", apath)
                continue
            n = len(labels) + 1
            ins += ["-i", apath]
            ms = s["target_timerange"]["start"] // 1000
            srcs = s["source_timerange"]["start"] / 1e6 if s.get("source_timerange") else 0
            du = s["target_timerange"]["duration"] / 1e6
            flt.append(f"[{n}:a]atrim={srcs}:{srcs+du},asetpts=PTS-STARTPTS,volume={s['volume']},adelay={ms}|{ms}[a{n}]")
            labels.append(f"[a{n}]")
        fc = ";".join(flt + [f"{''.join(labels)}amix=inputs={len(labels)}:normalize=0[a]",
                             "[0:v]ass=subs.ass[v]"])
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst] + ins +
                       ["-filter_complex", fc, "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "veryfast",
                        "-crf", "27", "-c:a", "aac", "-b:a", "128k", "-t", f"{d['duration']/1e6:.3f}", out],
                       check=True, cwd=td)  # cwd=td: tránh lỗi escape đường dẫn Windows trong filter ass
    print("Đã xuất", out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("content", help="draft_content.json (vd. work/draft_content.json)")
    ap.add_argument("-o", "--out", default="work/preview.mp4")
    ap.add_argument("--font", default="Montserrat", help="tên font đã cài trong Windows")
    ap.add_argument("--map", action="append", default=[], metavar="CŨ=MỚI",
                    help="đổi tiền tố đường dẫn, vd. --map \"F:/DCIM=E:/DCIM\" khi ổ đĩa đổi tên")
    a = ap.parse_args()
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    render(a.content, a.out, a.font, maps=[tuple(m.split("=", 1)) for m in a.map])


if __name__ == "__main__":
    main()
