import os
import glob
from typing import Dict, Any


def check_sample_pairing(
    scores: Dict[int, Dict[str, Any]],
    dataset_path: str,
    formats=["png", "lmx", "musicxml"]
):
    print("Checking sample pairing...")
    
    for score_id in scores.keys():
        dir_path = os.path.join(
            dataset_path, "samples", str(score_id)
        )

        # build up the set of all base names
        bases = set()
        for format in formats:
            for path in glob.glob(os.path.join(glob.escape(dir_path), "*." + format)):
                bases.add(path[:-len("."+format)])

        if len(bases) == 0:
            print("NO SAMPLES FOUND IN:", dir_path)
            continue

        # check that each format is present for each base
        for format in formats:
            for base in bases:
                path = base + "." + format
                if not os.path.isfile(path):
                    print("MISSING SAMPLE:", path)

    print("Checking done.")
