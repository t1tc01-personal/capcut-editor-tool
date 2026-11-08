"""Shared helpers: timing (frame-accurate), CapCut-style IDs, JSON IO, ffmpeg wrappers."""
import json
import os
import shutil
import subprocess
import uuid

FPS = 30


def sec_to_frame(t, fps=FPS):
    return int(round(t * fps))


def frame_to_us(f, fps=FPS):
    return int(round(f * 1_000_000 / fps))


def snap_us(t_sec, fps=FPS):
    """Seconds -> microseconds, snapped to the nearest frame boundary."""
    return frame_to_us(sec_to_frame(t_sec, fps), fps)


def new_id():
    """UUID in the mixed-case style CapCut writes (e.g. 5C883D9A-A389-4ade-BF6A-61AE1D6F318C)."""
    s = str(uuid.uuid4()).upper()
    return s[:14] + s[14:23].lower() + s[23:]


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(obj, path, compact=True):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        if compact:
            json.dump(obj, f, ensure_ascii=False, separators=(",", ":"))
        else:
            json.dump(obj, f, ensure_ascii=False, indent=2)


def need(tool):
    if shutil.which(tool) is None:
        raise SystemExit(f"Không tìm thấy '{tool}'. Xem docs/INSTALL.md để cài đặt.")


def ffprobe_duration(path):
    need("ffprobe")
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path]
    )
    return float(out.decode().strip())


def ffprobe_size(path):
    need("ffprobe")
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
         "stream=width,height", "-of", "csv=p=0", path]
    ).decode().strip()
    if not out:
        return 0, 0
    w, h = out.split(",")[:2]
    return int(w), int(h)


def norm(p):
    """CapCut stores paths with forward slashes."""
    return p.replace("\\", "/")
