"""Khôi phục dự án từ thư mục sao lưu do build.py tạo.

    python -m capcut_tool.restore "C:/.../1107/_backup_capcut_tool_20261108_170000"
"""
import os
import sys

from .draft import restore


def main():
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    bdir = os.path.abspath(sys.argv[1])
    restore(bdir, os.path.dirname(bdir))
    print("Xong. Mở lại dự án trong CapCut.")


if __name__ == "__main__":
    main()
