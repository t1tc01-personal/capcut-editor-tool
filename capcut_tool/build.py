"""Dựng timeline CapCut từ file kế hoạch (plan JSON) — ghi thẳng vào draft_content.json.

    python -m capcut_tool.build examples/plan_1107.json            # ghi vào dự án (tự sao lưu)
    python -m capcut_tool.build examples/plan_1107.json --dry-run  # chỉ kiểm tra, ghi ra work/draft_content.json

Kế hoạch gồm: voice, transcript (từ transcribe.py), danh sách cảnh, kiểu phụ đề, hiệu ứng âm thanh.
Mọi mốc thời gian đều được làm tròn theo khung hình (fps của dự án) để khớp tuyệt đối.
Xem docs/PLAN_FORMAT.md.
"""
import argparse
import copy
import json
import os
import re
import uuid

from . import draft as D
from .common import (FPS, ffprobe_duration, frame_to_us, load_json, new_id, norm, save_json, sec_to_frame)

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATES = load_json(os.path.join(HERE, "templates", "segments.json"))

DEFAULT_CAPTION = {
    "max_words": 6,
    "color": "#f0ff00",
    "stroke_color": "#000000",
    "stroke_width": 0.06,
    "font_size": 10,
    "position_y": -0.56,
    "tail": 0.25,
    "font": {
        "id": "7542214368361057553",
        "title": "Montserrat",
        "path": "C:/Users/PC/AppData/Local/CapCut/User Data/Cache/effect/7542214368361057553/d376267c892ee3a53654ae93a78dcfb7/font.ttf",
    },
    "animation": {
        "id": "7325378104753394178",
        "name": "Phóng to và tô màu",
        "path": "C:/Users/PC/AppData/Local/CapCut/User Data/Cache/effect/7325378104753394178/d6d6d5855f135143ce9617387626f79f",
    },
}


def hex_rgb(h):
    h = h.lstrip("#")
    return [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]


class Builder:
    def __init__(self, plan, base_content, fps=FPS):
        self.plan = plan
        self.base = base_content
        self.fps = fps
        self.mats = {k: [] for k in base_content["materials"]}

    # --- thời gian theo khung hình ---
    def f(self, sec):
        return sec_to_frame(sec, self.fps)

    def us(self, frame):
        return frame_to_us(frame, self.fps)

    # --- nhân bản segment mẫu ---
    def add(self, kind, start_us, dur_us, src_us=None, patch_main=None, patch_seg=None):
        tpl = TEMPLATES[kind]
        seg = copy.deepcopy(tpl["segment"])
        seg["id"] = new_id()
        ids = []
        for i, (mk, m) in enumerate(tpl["materials"]):
            m = copy.deepcopy(m)
            m["id"] = new_id()
            if i == 0 and patch_main:
                patch_main(m)
            if mk == "material_animations":
                for a in m.get("animations", []):
                    a["start"], a["duration"] = 0, dur_us
            self.mats.setdefault(mk, []).append(m)
            ids.append(m["id"])
        seg["material_id"], seg["extra_material_refs"] = ids[0], ids[1:]
        seg["target_timerange"] = {"start": start_us, "duration": dur_us}
        if src_us is not None:
            seg["source_timerange"] = {"start": src_us, "duration": dur_us}
        seg["keyframe_refs"], seg["common_keyframes"] = [], []
        if patch_seg:
            patch_seg(seg)
        return seg

    @staticmethod
    def track(typ, segs, flag=0, attr=0):
        return {"id": new_id(), "type": typ, "segments": segs, "flag": flag, "attribute": attr,
                "name": "", "is_default_name": True}


def resolve_media(draft_dir, path):
    path = norm(path)
    for m in D.list_media(draft_dir):
        if m["path"].lower() == path.lower():
            return m
    if os.path.exists(path):  # chưa import vào CapCut: vẫn dùng được, lấy thông số bằng ffprobe
        from .common import ffprobe_size
        w, h = ffprobe_size(path) if not path.lower().endswith((".mp3", ".wav", ".m4a", ".aac")) else (0, 0)
        return {"path": path, "id": str(uuid.uuid4()), "duration_us": int(ffprobe_duration(path) * 1e6),
                "width": w, "height": h, "extra_info": os.path.basename(path)}
    raise SystemExit(f"Không tìm thấy media: {path} (chưa import vào dự án và cũng không có trên máy).")


def word_times(text, a, b):
    """Chia thời lượng câu cho từng từ theo độ dài (tiếng Việt: 1 từ ~ 1 âm tiết).
    Dấu ' | ' trong text = ngắt dòng phụ đề."""
    toks = text.replace("|", " | ").split()
    real = [t for t in toks if t != "|"]
    if not real:
        return []
    wt = [len(re.sub(r"[^\w]", "", w)) + 1.5 for w in real]
    total, t, i, out = sum(wt), a, 0, []
    for tok in toks:
        if tok == "|":
            out.append(None)
            continue
        d = (b - a) * wt[i] / total
        i += 1
        out.append((tok, t, t + d))
        t += d
    return out


def group_lines(words, max_words):
    lines, cur, manual = [], [], None in words
    for w in words:
        if w is None:
            if cur:
                lines.append(cur)
            cur = []
        else:
            cur.append(w)
    if cur:
        lines.append(cur)
    if manual:
        return lines
    out = []
    for ln in lines:  # tự chia đều nếu quá dài
        n = len(ln)
        k = -(-n // max_words)
        size = -(-n // k)
        parts = [ln[i:i + size] for i in range(0, n, size)]
        if len(parts) > 1 and len(parts[-1]) <= 2:
            parts[-2] += parts.pop()
        out += parts
    return out


def build(plan):
    draft_dir = plan["draft_dir"]
    base = D.load_content(draft_dir)
    fps = int(round(plan.get("fps") or base.get("fps") or FPS))
    B = Builder(plan, base, fps)
    md5 = D.material_md5_map(draft_dir)

    # ---------- transcript ----------
    tr = load_json(plan["transcript"])
    chunks = tr["chunks"] if isinstance(tr, dict) else tr
    cap = {**DEFAULT_CAPTION, **plan.get("captions", {})}
    texts = cap.get("texts")
    if texts:
        if len(texts) != len(chunks):
            raise SystemExit(f"captions.texts có {len(texts)} dòng nhưng transcript có {len(chunks)} câu.")
        for c, t in zip(chunks, texts):
            c["text"] = t
    for fix_from, fix_to in cap.get("replace", {}).items():
        for c in chunks:
            c["text"] = c["text"].replace(fix_from, fix_to)

    # ---------- voice ----------
    vcfg = plan["voice"]
    vm = resolve_media(draft_dir, vcfg["path"])
    voice_us = int(vm["duration_us"])
    end_f = voice_us * fps // 1_000_000
    if plan.get("end"):
        end_f = min(end_f, B.f(plan["end"]))
    END = B.us(end_f)

    def voice_main(m):
        m.update(path=vm["path"], duration=voice_us, music_id=str(uuid.uuid4()), local_material_id="",
                 name=vm.get("extra_info") or os.path.basename(vm["path"]))

    voice = B.add("voice", 0, END, 0, voice_main,
                  lambda s: s.update(volume=vcfg.get("volume", 1.0), track_render_index=2))

    def chunk_start(i):
        return chunks[i]["start"] if i > 0 else 0.0

    # ---------- video ----------
    vplan = plan["video"]
    clips = vplan["clips"]
    starts = []
    for i, c in enumerate(clips):
        at = c.get("at")
        if at is None and "chunk" in c:
            at = chunk_start(c["chunk"])
        if i == 0:
            at = 0.0
        if at is None:
            raise SystemExit(f"Cảnh #{i} thiếu 'at' (giây) hoặc 'chunk' (số thứ tự câu).")
        starts.append(B.f(at))
    cuts = starts + [end_f]
    vsegs = []
    for i, c in enumerate(clips):
        m = resolve_media(draft_dir, c["file"])
        a, b = cuts[i], cuts[i + 1]
        if b <= a:
            raise SystemExit(f"Cảnh #{i} có thời lượng <= 0 (kiểm tra thứ tự 'at').")
        dur = B.us(b) - B.us(a)
        src = B.us(B.f(c.get("src", 0)))
        if src + dur > m["duration_us"]:
            raise SystemExit(f"Cảnh #{i}: {c['file']} chỉ dài {m['duration_us']/1e6:.2f}s, "
                             f"không đủ từ src={c.get('src', 0)}s cho {dur/1e6:.2f}s.")
        name = os.path.basename(m["path"])

        def vmain(x, m=m, name=name):
            x.update(path=m["path"], material_name=name, duration=m["duration_us"],
                     width=m["width"] or 1080, height=m["height"] or 1920,
                     local_material_id=m.get("id", ""), unique_id=md5.get(name, ""), has_audio=True)

        def vseg(s, c=c):
            s["volume"] = 0.0 if vplan.get("mute", True) else c.get("volume", 1.0)
            s["clip"]["scale"] = {"x": c.get("scale", 1.0), "y": c.get("scale", 1.0)}
            s["clip"]["transform"] = {"x": 0.0, "y": 0.0}
            s["uniform_scale"] = {"on": True, "value": c.get("scale", 1.0)}
            s["track_render_index"] = 0

        vsegs.append(B.add("video", B.us(a), dur, src, vmain, vseg))

    # ---------- captions ----------
    rgb, stroke_rgb = hex_rgb(cap["color"]), hex_rgb(cap["stroke_color"])
    font = cap["font"]
    lines = []
    for c in chunks:
        lines += group_lines(word_times(c["text"], c["start"], c["end"]), cap["max_words"])
    lines = [ln for ln in lines if ln]
    csegs = []
    for li, ln in enumerate(lines):
        text = " ".join(w for w, _, _ in ln)
        a = B.f(ln[0][1])
        b = B.f(ln[-1][2] + cap["tail"])
        if li + 1 < len(lines):
            b = min(b, B.f(lines[li + 1][0][1]))
        b = min(max(b, a + 6), end_f)
        if b <= a:
            continue
        st, du = B.us(a), B.us(b) - B.us(a)
        toks, ss, es = [], [], []
        for j, (w, ws, we) in enumerate(ln):
            s_ms = max(0, round((ws - st / 1e6) * 1000))
            e_ms = min(max(s_ms, round((we - st / 1e6) * 1000)), du // 1000)
            toks.append(w); ss.append(s_ms); es.append(e_ms)
            if j < len(ln) - 1:
                toks.append(" "); ss.append(e_ms); es.append(e_ms)

        def tmain(m, text=text, toks=toks, ss=ss, es=es):
            c = json.loads(m["content"])
            c["text"] = text
            sty = c["styles"][0]
            sty["range"] = [0, len(text)]
            sty["size"] = cap["font_size"]
            sty["fill"]["content"]["solid"]["color"] = rgb
            sty["font"] = {"path": font["path"], "id": font["id"]}
            sty["strokes"] = [{"content": {"render_type": "solid", "solid": {"color": stroke_rgb}},
                               "width": cap["stroke_width"], "mode": 0}]
            m["content"] = json.dumps(c, ensure_ascii=False, separators=(",", ":"))
            bc = json.loads(m["base_content"])
            bc["text"] = text
            bc["styles"][0]["range"] = [0, len(text)]
            m["base_content"] = json.dumps(bc, ensure_ascii=False, separators=(",", ":"))
            m["words"] = {"start_time": ss, "end_time": es, "text": toks}
            m.update(text_color=cap["color"], border_color=cap["stroke_color"], font_size=float(cap["font_size"]),
                     font_path=font["path"], font_resource_id=font["id"], recognize_task_id="", group_id="")
            for fo in m["fonts"]:
                fo.update(id=new_id(), path=font["path"], resource_id=font["id"], effect_id=font["id"],
                          title=font.get("title", ""))

        def tseg(s):
            s["clip"]["transform"] = {"x": 0.0, "y": cap["position_y"]}
            s["track_render_index"] = 1

        seg = B.add("caption", st, du, None, tmain, tseg)
        anim_mat = B.mats["material_animations"][-1]
        if cap.get("animation"):
            an = cap["animation"]
            for x in anim_mat["animations"]:
                x.update(id=an["id"], resource_id=an["id"], third_resource_id=an["id"], path=an["path"],
                         name=an.get("name", ""), start=0, duration=du)
        else:
            anim_mat["animations"] = []
        csegs.append(seg)

    # ---------- sound effects ----------
    sfx = plan.get("sfx", {})
    lib = sfx.get("library", {})
    all_words = [w for ln in lines for w in ln]

    def find_word(word, near):
        cands = [s for w, s, _ in all_words if word.lower() in w.lower()]
        if not cands:
            raise SystemExit(f"SFX: không tìm thấy từ '{word}' trong phụ đề.")
        return min(cands, key=lambda s: abs(s - near))

    events = []
    for ev in sfx.get("events", []):
        if ev["kind"] not in lib:
            raise SystemExit(f"SFX: '{ev['kind']}' chưa khai báo trong sfx.library.")
        if "word" in ev:
            t = find_word(ev["word"], ev.get("near", 0))
        elif "chunk" in ev:
            t = chunk_start(ev["chunk"])
        elif "cut" in ev:
            t = cuts[ev["cut"]] / fps
        else:
            t = ev["at"]
        fr = B.f(t) + ev.get("offset_frames", lib[ev["kind"]].get("offset_frames", 0))
        events.append((max(0, fr), ev))
    events.sort(key=lambda e: e[0])
    lanes, lane_end = [], []
    for fr, ev in events:
        L = lib[ev["kind"]]
        a = B.us(fr)
        if a >= END:
            continue
        dur = min(int(L["duration_us"]), END - a)
        li = next((i for i, e in enumerate(lane_end) if a >= e), None)
        if li is None:
            lanes.append([]); lane_end.append(0); li = len(lanes) - 1

        def smain(m, L=L):
            m.update(name=L["name"], path=norm(L["path"]), duration=int(L["duration_us"]),
                     effect_id=L.get("effect_id", ""), type="sound")

        def sseg(s, ev=ev, L=L, li=li):
            s["volume"] = ev.get("volume", L.get("volume", 0.7))
            s["track_render_index"] = 3 + li

        lanes[li].append(B.add("sound", a, dur, 0, smain, sseg))
        lane_end[li] = a + dur

    out = copy.deepcopy(base)
    out["materials"] = B.mats
    out["tracks"] = ([B.track("video", vsegs, 0, 1), B.track("text", csegs, 1, 0), B.track("audio", [voice])]
                     + [B.track("audio", l) for l in lanes])
    out["duration"] = END
    out["config"]["video_mute"] = bool(vplan.get("mute", True))
    stats = dict(duration=END / 1e6, scenes=len(vsegs), captions=len(csegs), sfx=sum(map(len, lanes)))
    return out, stats


def validate(content):
    ids = {m["id"] for v in content["materials"].values() for m in v}
    problems = []
    for t in content["tracks"]:
        prev = -1
        for s in sorted(t["segments"], key=lambda s: s["target_timerange"]["start"]):
            tr = s["target_timerange"]
            if tr["start"] < prev:
                problems.append(f"chồng lấn trên track {t['type']} tại {tr['start']/1e6:.3f}s")
            prev = tr["start"] + tr["duration"]
            for r in [s["material_id"]] + s["extra_material_refs"]:
                if r not in ids:
                    problems.append(f"thiếu material {r}")
    return problems


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("plan")
    ap.add_argument("--dry-run", action="store_true", help="không ghi vào dự án, chỉ xuất work/draft_content.json")
    ap.add_argument("--out", default="work/draft_content.json")
    a = ap.parse_args()
    plan = load_json(a.plan)
    content, stats = build(plan)
    probs = validate(content)
    if probs:
        raise SystemExit("Lỗi kiểm tra:\n  " + "\n  ".join(probs))
    save_json(content, a.out)
    print(f"Timeline: {stats['duration']:.2f}s | {stats['scenes']} cảnh | {stats['captions']} phụ đề | {stats['sfx']} SFX")
    print(f"Đã xuất {a.out}")
    if a.dry_run:
        return
    bdir = D.backup(plan["draft_dir"])
    D.write_draft(plan["draft_dir"], content)
    print(f"Đã ghi vào dự án: {plan['draft_dir']}")
    print(f"Sao lưu bản cũ tại: {bdir}  (khôi phục: python -m capcut_tool.restore \"{bdir}\")")
    print("Hãy ĐÓNG dự án trong CapCut trước khi chạy, rồi mở lại để xem.")


if __name__ == "__main__":
    main()
