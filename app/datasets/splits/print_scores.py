from typing import List
import glob
import os
from .constants import *


def print_scores(all_scores, score_ids: List[int]):
    assert os.path.isdir(SCANNED_DATASET_PATH), "Set up the scanned dataset"
    annotated_scores = glob.glob(f"{SCANNED_DATASET_PATH}/corpus_to_imslp/*.yaml")
    annotated_scores = set(
        int(os.path.basename(path)[:-5])
        for path in annotated_scores
    )
    
    for i, score_id in enumerate(score_ids):
        score = all_scores[score_id]
        is_annotated = score_id in annotated_scores
        print(
            (str(i + 1) + ")").rjust(4),
            "[x]" if is_annotated else "[ ]",
            score_id,
            score["path"]
        )