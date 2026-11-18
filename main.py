#!/usr/bin/env python3
"""
news-image-20261117 — entry program.

The grader runs this file with the Python 3.13 standard library only;
nothing is installed, so this program imports nothing beyond os, shutil
and sys. The front page itself is pre-rendered and ships in the repo as
entry.png beside this script; the program's whole job is to copy that
file, byte for byte, to the output directory:

    $MAKEFUN_OUTPUT_DIR/entry.png   (fallback: /output/entry.png)

The source is $MAKEFUN_BOT_DIR/entry.png when that variable is set,
otherwise the entry.png beside this script. Deterministic: the output
bytes are exactly the shipped entry.png on every run. Exits 0 on success.
"""

import os
import shutil
import sys


def source_path():
    bot_dir = os.environ.get("MAKEFUN_BOT_DIR")
    if bot_dir:
        return os.path.join(bot_dir, "entry.png")
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, "entry.png")


def output_path():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    return out_dir, os.path.join(out_dir, "entry.png")


def main():
    src = source_path()
    out_dir, dst = output_path()
    os.makedirs(out_dir, exist_ok=True)
    shutil.copyfile(src, dst)
    return 0


if __name__ == "__main__":
    sys.exit(main())
