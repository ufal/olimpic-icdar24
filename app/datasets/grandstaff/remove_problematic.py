import shutil
import os
from ..config import GRANDSTAFF_DATASET_PATH


# there were problems with loading these score's humdrum kern,
# so we decided to remove them, instead of patching
# (the patch was not obvious, the music21 parser broke down)
# "Could not determine spineType for spine with id 2"
PROBLEMATIC_SCORES = [
    "beethoven/piano-sonatas/sonata07-1",
    "beethoven/piano-sonatas/sonata07-3",
    "beethoven/piano-sonatas/sonata09-2",
    "beethoven/piano-sonatas/sonata15-1",
    "chopin/mazurkas/mazurka41-2",
    "joplin/joplin/pleasant"
]


def remove_problematic():
    for path in PROBLEMATIC_SCORES:

        path = os.path.join(GRANDSTAFF_DATASET_PATH, path)

        if os.path.isdir(path):
            shutil.rmtree(path)
