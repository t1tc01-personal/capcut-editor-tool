"""Quét các dự án CapCut để tìm đường dẫn font, hiệu ứng chú thích, hiệu ứng âm thanh đã dùng
— in ra đoạn JSON dán thẳng vào file kế hoạch (captions.font, captions.animation, sfx.library).

Dùng khi chuyển máy / chuyển sang macOS (đường dẫn Cache khác Windows).

    python -m capcut_tool.find_resources "<thư mục com.lveditor.draft>"
    python -m capcut_tool.find_resources "<thư mục com.lveditor.draft>" --check   # kiểm tra file còn trong Cache
"""
import argparse
import json
import os
import re

from .common import load_json


def slug(name):
    s = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
    return (s or "sfx")[:24]


def scan(root):
    # os.walk (không dùng glob) để quét cả thư mục ẩn như .recycle_bin
    files = [os.path.join(dp, "draft_content.json") for dp, _, fs in os.walk(root) if "draft_content.json" in fs]
    fonts, anims, sounds = {}, {}, {}
    for f in files:
        try:
            d = load_json(f)
        except Exception:
            continue  # draft bị mã hoá hoặc hỏng
        mats = d.get("materials", {})
        for t in mats.get("texts", []):
            for fo in t.get("fonts", []) or []:
                if fo.get("path"):
                    fonts[fo.get("resource_id") or fo["path"]] = {
                        "id": fo.get("resource_id", ""), "title": fo.get("title", ""), "path": fo["path"]}
        for a in mats.get("material_animations", []):
            for x in a.get("animations", []) or []:
                if x.get("path"):
                    anims[x.get("resource_id") or x["path"]] = {
                        "id": x.get("resource_id", ""), "name": x.get("name", ""), "path": x["path"],
                        "type": x.get("type", "")}
        for s in mats.get("audios", []):
            if s.get("type") == "sound" and s.get("path"):
                sounds[s["path"]] = {"name": s.get("name", ""), "path": s["path"],
                                     "duration_us": s.get("duration", 0), "effect_id": s.get("effect_id", ""),
                                     "volume": 0.7}
    return files, fonts, anims, sounds


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("drafts_root", help="thư mục com.lveditor.draft (chứa các dự án)")
    ap.add_argument("--check", action="store_true", help="chỉ in tài nguyên còn tồn tại trên máy")
    a = ap.parse_args()
    files, fonts, anims, sounds = scan(a.drafts_root)
    ok = (lambda p: os.path.exists(p)) if a.check else (lambda p: True)
    print(f"Đã quét {len(files)} file draft_content.json\n")
    print("== FONT (captions.font) ==")
    for v in fonts.values():
        if ok(v["path"]):
            print(json.dumps(v, ensure_ascii=False))
    print("\n== HIỆU ỨNG CHỮ (captions.animation – chọn loại type=caption) ==")
    for v in anims.values():
        if ok(v["path"]):
            print(json.dumps({k: v[k] for k in ("id", "name", "path")}, ensure_ascii=False), f"  # type={v['type']}")
    print("\n== HIỆU ỨNG ÂM THANH (sfx.library) ==")
    lib, used = {}, set()
    for v in sounds.values():
        if not ok(v["path"]):
            continue
        k = slug(v["name"])
        while k in used:
            k += "_2"
        used.add(k)
        lib[k] = v
    print(json.dumps(lib, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
