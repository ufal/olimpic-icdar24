import random
import yaml
from typing import List
from .constants import *


# With cca 16 systems (or 4 pages) per score on average, taking 100 scores
# yields about 1600 systems to test on. Also it is almost 10% of the corpus
# (which would be ~130 scores) and it is a nice round number.
TARGET_SCORE_COUNT = 100


def generate_dev_partition(all_scores, test_sets_ids):
    """Shuffle scores go through them sequentially."""
    all_scores_ids = list(all_scores.keys())
    rng = random.Random(SEED)
    rng.shuffle(all_scores_ids)

    # go through the sets and through their scores, until we get
    # the target test score count, whilst skipping ignored scores
    dev_score_ids: List[str] = []

    for score_id in all_scores_ids:
        score = all_scores[score_id]
        if len(dev_score_ids) >= TARGET_SCORE_COUNT:
            break

        # skip globally ignored scores
        if score_id in GLOBALLY_IGNORED_SCORES:
            continue

        # skip those that were problematic to annotate
        if score_id in ANNOTATION_PROBLEMATIC_SCORES:
            continue

        # skip those that are in a set that is in the test partition
        if score["set_id"] in test_sets_ids:
            continue

        dev_score_ids.append(score_id)
    
    return dev_score_ids
