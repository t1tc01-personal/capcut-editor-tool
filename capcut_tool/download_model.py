"""Tải model nhận dạng giọng nói Whisper (bản sherpa-onnx) vào thư mục models/.

    python -m capcut_tool.download_model            # medium (~1.9 GB, tốt cho tiếng Việt)
    python -m capcut_tool.download_model small      # nhẹ hơn (~600 MB), kém chính xác hơn
"""
import os
import sys
import tarfile
import urllib.request

URL = "https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-whisper-{}.tar.bz2"


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "medium"
    os.makedirs("models", exist_ok=True)
    target = os.path.join("models", f"sherpa-onnx-whisper-{name}")
    if os.path.isdir(target):
        print("Đã có:", target)
        return
    arc = target + ".tar.bz2"
    url = URL.format(name)
    print("Đang tải", url)

    def hook(n, bs, total):
        if total > 0:
            print(f"\r  {min(100, n * bs * 100 // total)}%", end="", flush=True)

    urllib.request.urlretrieve(url, arc, hook)
    print("\nGiải nén...")
    with tarfile.open(arc, "r:bz2") as t:
        t.extractall("models")
    os.remove(arc)
    print("Xong:", target)


if __name__ == "__main__":
    main()
