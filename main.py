# news-image-20261117 entry (Python 3.13, standard library only).
#
# The entry is one image: a newspaper front page that sums up the world
# news of Tuesday 17 November 2026 — thirty stories, from the Kerch
# Strait to Shenzhen, drawn and typeset as a single page. The image is
# the entry.png beside this file, and the program copies it, byte for
# byte, to /output/entry.png. The gate takes a whole PNG or JPEG of at
# most 1 MiB and at most 1024 by 1024 pixels, and the judge sees exactly
# the bytes copied.
#
# Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for
# /output:
#   mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py

import os
import shutil

# The grader sets no variable and expects the image at /output/entry.png;
# MAKEFUN_OUTPUT_DIR only redirects it for runs outside the container.
OUTPUT_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
IMAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")

os.makedirs(OUTPUT_DIR, exist_ok=True)
shutil.copyfile(IMAGE_PATH, os.path.join(OUTPUT_DIR, "entry.png"))
