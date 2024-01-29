import random
from typing import Set
from .constants import *


# With cca 16 systems (or 4 pages) per score on average, taking 100 scores
# yields about 1600 systems to test on. Also it is almost 10% of the corpus
# (which would be ~130 scores) and it is a nice round number.
TARGET_SCORE_COUNT = 100

# Look at the size distribution of sets:
# https://github.com/OpenScore/Lieder?tab=readme-ov-file#data-plots
# Most are below 10, almost all below 7. But some have 20-30 scores.
# We want diversity in the test set, so we choose smaller sets, so that
# we have more of them. Five seems like a good maximum number
# of similar-looking scores to have in a test set of size 100.
MAXIMUM_SET_SIZE = 5


def generate_test_partition(all_scores, all_sets) -> Set[int]:
    """Shuffle sets that are not unreasonably large and go through them sequentially."""
    all_sets_ids = list(all_sets.keys())
    rng = random.Random(SEED)
    rng.shuffle(all_sets_ids)

    # remove sets that are too large
    sets_ids = [
        id for id in all_sets_ids
        if all_sets[id]["scores"] <= MAXIMUM_SET_SIZE
    ]

    # go through the sets and through their scores, until we get
    # the target test score count, whilst skipping ignored scores
    test_scores_ids: Set[int] = set()

    for score_id in _generate_score_ids(sets_ids, all_scores):
        if len(test_scores_ids) >= TARGET_SCORE_COUNT:
            break

        # skip globally ignored scores
        if score_id in GLOBALLY_IGNORED_SCORES:
            continue

        # skip those that were problematic to annotate
        if score_id in ANNOTATION_PROBLEMATIC_SCORES:
            continue

        test_scores_ids.add(score_id)
    
    return test_scores_ids


def _generate_score_ids(sets_ids, all_scores):
    for set_id in sets_ids:
        for score_id, score in all_scores.items():
            if score["set_id"] == set_id:
                yield score_id
