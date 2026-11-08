"""Đọc / ghi thư mục dự án CapCut (draft_content.json, draft_meta_info.json, Timelines/...)."""
import datetime
import os
import shutil

from .common import load_json, norm, save_json


def content_paths(draft_dir):
    """Tất cả file draft_content.json cần ghi (gốc + bản trong Timelines/<main_timeline_id>/)."""
    paths = [os.path.join(draft_dir, "draft_content.json")]
    pj = os.path.join(draft_dir, "Timelines", "project.json")
    if os.path.exists(pj):
        tid = load_json(pj).get("main_timeline_id")
        if tid:
            p = os.path.join(draft_dir, "Timelines", tid, "draft_content.json")
            if os.path.exists(p):
                paths.append(p)
    return paths


def load_content(draft_dir):
    p = os.path.join(draft_dir, "draft_content.json")
    try:
        return load_json(p)
    except Exception as e:
        raise SystemExit(
            f"Không đọc được {p} dạng JSON ({e}).\n"
            "Một số bản CapCut mới mã hoá file này; công cụ chỉ chạy với draft dạng JSON thường."
        )


def load_meta(draft_dir):
    p = os.path.join(draft_dir, "draft_meta_info.json")
    return load_json(p) if os.path.exists(p) else None


def list_media(draft_dir):
    """Media đã import vào thư viện của dự án (theo draft_meta_info.json)."""
    meta = load_meta(draft_dir) or {}
    out = []
    for group in meta.get("draft_materials", []):
        for x in group.get("value", []):
            mt = x.get("metetype")
            kind = {"video": "video", "photo": "photo", "music": "audio"}.get(mt)
            if kind is None and group.get("type") == 1:
                kind = "audio"
            if kind is None:
                continue
            out.append({
                "kind": kind, "path": norm(x["file_Path"]), "id": x.get("id", ""),
                "duration_us": x.get("duration", 0), "width": x.get("width", 0), "height": x.get("height", 0),
                "extra_info": x.get("extra_info", ""),
            })
    # bỏ trùng theo path, ưu tiên mục có kind cụ thể
    seen, uniq = set(), []
    for m in out:
        if (m["kind"], m["path"]) not in seen:
            seen.add((m["kind"], m["path"]))
            uniq.append(m)
    return uniq


def material_md5_map(draft_dir):
    p = os.path.join(draft_dir, "key_value.json")
    if not os.path.exists(p):
        return {}
    kv = load_json(p)
    return {v["materialName"]: k for k, v in kv.items()
            if isinstance(v, dict) and v.get("materialCategory") == "media" and "materialName" in v}


def backup(draft_dir):
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    bdir = os.path.join(draft_dir, f"_backup_capcut_tool_{stamp}")
    os.makedirs(bdir, exist_ok=True)
    for p in content_paths(draft_dir) + [os.path.join(draft_dir, "draft_meta_info.json")]:
        if os.path.exists(p):
            rel = os.path.relpath(p, draft_dir).replace(os.sep, "__")
            shutil.copy2(p, os.path.join(bdir, rel))
    return bdir


def write_draft(draft_dir, content):
    for p in content_paths(draft_dir):
        save_json(content, p)
    meta_p = os.path.join(draft_dir, "draft_meta_info.json")
    if os.path.exists(meta_p):
        meta = load_json(meta_p)
        meta["tm_duration"] = content["duration"]
        save_json(meta, meta_p)


def restore(backup_dir, draft_dir):
    for f in os.listdir(backup_dir):
        dst = os.path.join(draft_dir, *f.split("__"))
        shutil.copy2(os.path.join(backup_dir, f), dst)
        print("khôi phục", dst)
