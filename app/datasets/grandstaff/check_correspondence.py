import glob
import os
from ..config import GRANDSTAFF_DATASET_PATH, MSCORE


def check_correspondence():
    paths = glob.glob(
        os.path.join(GRANDSTAFF_DATASET_PATH, "**/*.krn"),
        recursive=True
    )
    paths = list(sorted(path[:-len(".krn")] for path in paths))

    for path in paths:
        if not os.path.exists(path + ".musicxml"):
            print("Missing MusicXML", path)
        if not os.path.exists(path + ".lmx"):
            print("Missing LMX", path)
    
    print("Done.")
