"""Chép lời voice (offline) -> transcript JSON có mốc thời gian theo từng câu.

Cách làm: tách câu theo khoảng lặng (ffmpeg silencedetect), mỗi câu đưa vào
Whisper (sherpa-onnx, chạy CPU, không cần GPU / HuggingFace).

    python -m capcut_tool.transcribe voice.mp3 -o work/transcript.json --model models/sherpa-onnx-whisper-medium --lang vi
"""
import argparse
import os
import re
import subprocess
import tempfile

import numpy as np

from .common import need, save_json

MODEL_URL = "https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-whisper-{name}.tar.bz2"


def to_wav16k(src, dst):
    need("ffmpeg")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", src, "-ar", "16000", "-ac", "1", dst], check=True)


def detect_speech_chunks(wav, noise_db=-35, min_silence=0.25, min_chunk=0.15):
    p = subprocess.run(
        ["ffmpeg", "-i", wav, "-af", f"silencedetect=noise={noise_db}dB:d={min_silence}", "-f", "null", "-"],
        capture_output=True, text=True,
    )
    txt = p.stderr
    st = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", txt)]
    en = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", txt)]
    import soundfile as sf
    info = sf.info(wav)
    dur = info.frames / info.samplerate
    bounds, prev = [], 0.0
    for s, e in zip(st, en):
        if s - prev > min_chunk:
            bounds.append((prev, s))
        prev = e
    if dur - prev > min_chunk:
        bounds.append((prev, dur))
    return bounds, dur


def find_model_files(model_dir):
    files = os.listdir(model_dir)
    enc = [f for f in files if f.endswith("-encoder.int8.onnx")] or [f for f in files if f.endswith("-encoder.onnx")]
    dec = [f for f in files if f.endswith("-decoder.int8.onnx")] or [f for f in files if f.endswith("-decoder.onnx")]
    tok = [f for f in files if f.endswith("-tokens.txt")]
    if not (enc and dec and tok):
        raise SystemExit(f"Thư mục model không hợp lệ: {model_dir}. Xem docs/INSTALL.md (tải model Whisper).")
    j = lambda f: os.path.join(model_dir, f)
    return j(enc[0]), j(dec[0]), j(tok[0])


def transcribe(audio, model_dir, lang="vi", threads=4, noise_db=-35, min_silence=0.25):
    import sherpa_onnx
    import soundfile as sf

    enc, dec, tok = find_model_files(model_dir)
    rec = sherpa_onnx.OfflineRecognizer.from_whisper(
        encoder=enc, decoder=dec, tokens=tok, num_threads=threads, language=lang, task="transcribe"
    )
    with tempfile.TemporaryDirectory() as td:
        wav = os.path.join(td, "voice16k.wav")
        to_wav16k(audio, wav)
        bounds, dur = detect_speech_chunks(wav, noise_db, min_silence)
        data, sr = sf.read(wav, dtype="float32")
    out = []
    for a, b in bounds:
        # đệm thêm ngữ cảnh + khoảng lặng để Whisper không nuốt chữ cuối
        seg = data[max(0, int((a - 0.2) * sr)): int((b + 0.25) * sr)]
        seg = np.concatenate([np.zeros(int(0.3 * sr), "float32"), seg, np.zeros(int(1.0 * sr), "float32")])
        s = rec.create_stream()
        s.accept_waveform(sr, seg)
        rec.decode_stream(s)
        text = s.result.text.strip()
        out.append({"start": round(a, 3), "end": round(b, 3), "text": text})
        print(f"{a:7.2f}-{b:7.2f}  {text}", flush=True)
    return {"audio": os.path.abspath(audio), "duration": dur, "chunks": out}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("audio", help="file voice (mp3/wav/m4a...)")
    ap.add_argument("-o", "--out", default="work/transcript.json")
    ap.add_argument("--model", default="models/sherpa-onnx-whisper-medium", help="thư mục model sherpa-onnx whisper")
    ap.add_argument("--lang", default="vi")
    ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--noise-db", type=float, default=-35, help="ngưỡng coi là im lặng (dB)")
    ap.add_argument("--min-silence", type=float, default=0.25, help="khoảng lặng tối thiểu để tách câu (giây)")
    a = ap.parse_args()
    res = transcribe(a.audio, a.model, a.lang, a.threads, a.noise_db, a.min_silence)
    save_json(res, a.out, compact=False)
    print(f"\nĐã lưu {len(res['chunks'])} câu -> {a.out}")
    print("Mẹo: mở file, sửa chính tả trong trường 'text' và dùng ' | ' để ngắt dòng phụ đề.")


if __name__ == "__main__":
    main()
