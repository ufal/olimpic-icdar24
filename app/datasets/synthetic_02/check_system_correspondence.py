import os
import glob
from typing import Iterable
from .config import *


def check_system_correspondence(
    score_ids: Iterable[int],
    flavor: str
):
    print("Ckecking for non-paired PNG-LMX files...")
    for score_id in score_ids:
        dir_path = os.path.join(
            DATASET_PATH, "samples", str(score_id)
        )
        if not os.path.isdir(dir_path):
            print("MISSING SAMPLE DIRECTORY:", dir_path)
            continue

        png_pattern = os.path.join(dir_path, f"*.png")
        lmx_pattern = os.path.join(dir_path, f"*.{flavor}.lmx")

        png_files = set(f.replace(".png", "") for f in glob.glob(png_pattern))
        lmx_files = set(f.replace(f".{flavor}.lmx", "") for f in glob.glob(lmx_pattern))

        diff = png_files.symmetric_difference(lmx_files)
        for file in diff:
            print("LONELY:", file)
    print("Checking done.")
