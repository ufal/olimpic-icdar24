from typing import Set
from .constants import *


def generate_train_partition(
    all_scores,
    test_sets_ids: Set[int],
    dev_scores_ids: Set[int]
) -> Set[int]:
    # go through the sets and through their scores, until we get
    # the target test score count, whilst skipping ignored scores
    train_scores_ids: Set[str] = set()

    for score_id, score in all_scores.items():
        # skip globally ignored scores
        if score_id in GLOBALLY_IGNORED_SCORES:
            continue

        # skip those that are in a set that is in the test partition
        if score["set_id"] in test_sets_ids:
            continue

        # skip those that are in the dev partition
        if score_id in dev_scores_ids:
            continue

        train_scores_ids.add(score_id)
    
    return train_scores_ids
