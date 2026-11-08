"""CapCut Editor Tool – dựng timeline CapCut bằng cách ghi trực tiếp file dự án."""
__version__ = "1.0.0"

import sys as _sys

# Cửa sổ lệnh Windows mặc định không phải UTF-8: tránh lỗi khi in tiếng Việt.
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
