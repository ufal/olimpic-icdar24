from .splits.data import *
from .slice_scores import slice_scores
from typing import Optional


def take_scores(
    train: bool,
    dev: bool,
    test: bool,

    slice_index: int = 0,
    slice_count: int = 1,

    inspect: Optional[int] = None
) -> dict:
    """Load the scores for building a dataset"""
    scores = {}

    print(f"Loading scores...")

    if train:
        scores.update(TRAIN_SCORES)
    
    if dev:
        scores.update(DEV_SCORES)
    
    if test:
        scores.update(TEST_SCORES)

    # sort scores by path
    scores = dict(
        sorted(scores.items(), key=lambda pair: pair[1]["path"])
    )

    if inspect is not None:
        assert inspect in scores.keys()
        slice_count = len(scores)
        slice_index = list(scores.keys()).index(inspect)
        scores = {
            inspect: scores[inspect]
        }
    else:
        scores = slice_scores(scores, slice_index, slice_count)
    
    print(f"Loaded {len(scores)} scores.")

    return scores, slice_index, slice_count
